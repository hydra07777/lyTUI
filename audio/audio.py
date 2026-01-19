import time
import threading
import queue
import av
import sounddevice as sd
import numpy as np

class PlaybackState:
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"

class AudioEngine:
    def __init__(self):
        # Configuration
        self.target_samplerate = 44100 
        self.channels = 2
        self.dtype = "float32"
        self.av_format = "fltp" 
        
        # État interne
        self.state = PlaybackState.STOPPED
        self.stream = None
        self.audio_q = queue.Queue(maxsize=50) 
        self.leftover = np.zeros((0, 2), dtype=self.dtype)
        
        # Contrôle
        self.stop_event = threading.Event()
        self.decoder_thread = None
        self.duration = 0.0
        self.current_time = 0.0
        self.volume = 0.5
        
        # Switch automatique
        self.current_device_id = sd.default.device[1] # ID du périphérique de sortie par défaut
        self.monitor_thread = threading.Thread(target=self._monitor_devices, daemon=True)
        self.monitor_thread.start()

    def _monitor_devices(self):
        """Surveille le changement de périphérique par défaut avec rafraîchissement."""
        while True:
            if self.state == PlaybackState.PLAYING:
                try:
                    # On récupère le nom du périphérique par défaut actuel
                    # C'est plus fiable que l'ID qui peut rester le même
                    current_default_name = sd.query_devices(kind='output')['name']
                    
                    # On stocke le nom du périphérique utilisé par le stream actuel
                    # Si on n'a pas encore de nom stocké, on le prend
                    if not hasattr(self, '_last_device_name'):
                        self._last_device_name = current_default_name

                    # Si le nom a changé, c'est qu'on a switché (ex: "Speakers" -> "Headphones")
                    if current_default_name != self._last_device_name:
                        print(f"Switch détecté vers : {current_default_name}")
                        self._last_device_name = current_default_name
                        self._restart_stream()
                        
                except Exception as e:
                    # Parfois query_devices échoue pendant la transition physique
                    pass
            
            time.sleep(1.0) # Vérification toutes les secondes

    def _restart_stream(self, device_id=None):
        """Relance le flux sur un périphérique spécifique ou par défaut."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        self.stream = sd.OutputStream(
            samplerate=self.target_samplerate,
            channels=self.channels,
            callback=self._callback,
            dtype=self.dtype,
            blocksize=4096,
            device=device_id # Si None, utilise le défaut
        )
        self.stream.start()

    def load(self, path: str):
        self.stop()
        self.stop_event.clear()
        self.current_time = 0.0
        self.leftover = np.zeros((0, 2), dtype=self.dtype)
        
        self.decoder_thread = threading.Thread(
            target=self._decoder_loop, 
            args=(path,), 
            daemon=True
        )
        self.decoder_thread.start()
        
        while self.audio_q.qsize() < 15 and self.decoder_thread.is_alive():
            time.sleep(0.01)
            
        self.state = PlaybackState.PAUSED

    def _decoder_loop(self, path):
        container = None
        try:
            container = av.open(path)
            stream = container.streams.audio[0]
            self.duration = float(stream.duration * stream.time_base)

            resampler = av.AudioResampler(
                format=self.av_format,
                layout='stereo',
                rate=self.target_samplerate
            )

            for frame in container.decode(stream):
                if self.stop_event.is_set():
                    break
                
                frame.pts = None 
                frames = resampler.resample(frame)
                
                for f in frames:
                    array = f.to_ndarray().transpose()
                    if array.dtype != np.float32:
                        array = array.astype(np.float32)

                    while not self.stop_event.is_set():
                        try:
                            self.audio_q.put(array, timeout=0.1)
                            break
                        except queue.Full:
                            continue 
                            
        except Exception as e:
            print(f"Erreur décodage: {e}")
        finally:
            if container: container.close()

    def _callback(self, outdata, frames, time_info, status):
        # Ne rien faire si on n'est pas en lecture
        if self.state != PlaybackState.PLAYING:
            outdata.fill(0)
            return

        current_pos = 0
        if len(self.leftover) > 0:
            take = min(frames, len(self.leftover))
            outdata[:take] = self.leftover[:take]
            self.leftover = self.leftover[take:]
            current_pos += take

        while current_pos < frames:
            needed = frames - current_pos
            try:
                data = self.audio_q.get_nowait()
                self.current_time += len(data) / self.target_samplerate
                
                if len(data) > needed:
                    outdata[current_pos:] = data[:needed]
                    self.leftover = data[needed:]
                    current_pos += needed
                    break
                else:
                    outdata[current_pos : current_pos + len(data)] = data
                    current_pos += len(data)
            except queue.Empty:
                outdata[current_pos:].fill(0)
                if not self.decoder_thread.is_alive() and len(self.leftover) == 0:
                      self.state = PlaybackState.STOPPED
                break

        # APPLICATION DU VOLUME LOGICIEL
        outdata[:] *= self.volume

    def play(self):
        if self.state == PlaybackState.STOPPED and (not self.decoder_thread or not self.decoder_thread.is_alive()):
            return

        if self.stream is None or not self.stream.active:
            self._restart_stream()
            
        self.state = PlaybackState.PLAYING

    def pause(self):
        self.state = PlaybackState.PAUSED

    def un_pause(self):
        if self.state == PlaybackState.PAUSED:
            self.play()

    def stop(self):
        self.state = PlaybackState.STOPPED
        self.stop_event.set()
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
        while not self.audio_q.empty():
            try: self.audio_q.get_nowait()
            except queue.Empty: break
        
        if self.decoder_thread:
            self.decoder_thread.join(timeout=0.2)
            self.decoder_thread = None

    def get_output_devices(self):
        """Retourne une liste des périphériques de sortie disponibles."""
        devices = sd.query_devices()
        output_devices = []
        for i, d in enumerate(devices):
            # On ne garde que les périphériques qui ont des canaux de sortie
            if d['max_output_channels'] > 0:
                output_devices.append({
                    "id": i,
                    "name": d['name'],
                    "hostapi": d['hostapi']
                })
        return output_devices

    def set_output_device(self, device_id):
        """Change le périphérique de sortie et relance le flux."""
        self.current_device_id = device_id
        # On force le redémarrage sur ce nouvel ID
        self._restart_stream(device_id=device_id)

    def get_time(self):
        return self.current_time
    
    def get_duration(self):
        return self.duration

    def debug_status(self):
        return f"--- DEBUG | Vol: {self.volume} | Device: {self.current_device_id} | Time: {self.current_time:.1f}s ---"
    