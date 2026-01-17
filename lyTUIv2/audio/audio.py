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
        
        # CORRECTION 1 : Utiliser "fltp" (Float Planar). 
        # Cela garantit que PyAV sort du (Channels, Samples), 
        # rendant le .transpose() logiquement correct pour obtenir (Samples, Channels).
        self.av_format = "fltp" 
        
        # État interne
        self.state = PlaybackState.STOPPED
        self.stream = None
        # On augmente un peu la taille de la queue pour avoir de la marge
        self.audio_q = queue.Queue(maxsize=50) 
        self.leftover = np.zeros((0, 2), dtype=self.dtype)
        
        # Contrôle
        self.stop_event = threading.Event()
        self.decoder_thread = None
        self.duration = 0.0
        self.current_time = 0.0

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
        
        # Pré-buffering un peu plus robuste
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
                format=self.av_format, # Utilise fltp
                layout='stereo',
                rate=self.target_samplerate
            )

            for frame in container.decode(stream):
                if self.stop_event.is_set():
                    break
                
                frame.pts = None 
                frames = resampler.resample(frame)
                
                # Note: resampler peut retourner plusieurs frames ou aucune
                for f in frames:
                    # Conversion : (Channels, Samples) -> (Samples, Channels)
                    array = f.to_ndarray().transpose()
                    
                    # On s'assure que c'est bien du float32 contigu pour éviter les copies inutiles
                    if array.dtype != np.float32:
                        array = array.astype(np.float32)

                    while not self.stop_event.is_set():
                        try:
                            self.audio_q.put(array, timeout=0.1)
                            break
                        except queue.Full:
                            continue 
                            
        except Exception as e:
            print(f"Erreur moteur (décodage): {e}")
        finally:
            if container:
                container.close()

    def _callback(self, outdata, frames, time_info, status):
        if status:
            print(f"Status: {status}") # Debug: voir s'il y a des 'underflow'
            
        if self.state != PlaybackState.PLAYING:
            outdata.fill(0)
            return

        current_pos = 0
        
        # 1. Gestion du surplus (leftover)
        if len(self.leftover) > 0:
            take = min(frames, len(self.leftover))
            outdata[:take] = self.leftover[:take]
            self.leftover = self.leftover[take:]
            current_pos += take

        # 2. Remplissage depuis la Queue
        while current_pos < frames:
            needed = frames - current_pos
            try:
                # get_nowait est très rapide, c'est bien
                data = self.audio_q.get_nowait()
                
                # Mise à jour du temps approximatif
                self.current_time += len(data) / self.target_samplerate
                
                if len(data) > needed:
                    outdata[current_pos:] = data[:needed]
                    self.leftover = data[needed:]
                    current_pos += needed # On a fini de remplir outdata
                    break
                else:
                    outdata[current_pos : current_pos + len(data)] = data
                    current_pos += len(data)
                    
            except queue.Empty:
                # Si la queue est vide, on remplit de zéros pour éviter le bruit
                outdata[current_pos:].fill(0)
                if not self.decoder_thread.is_alive() and len(self.leftover) == 0:
                      self.state = PlaybackState.STOPPED
                break

    def play(self):
        if self.state == PlaybackState.STOPPED and not self.decoder_thread:
            return
            
        if self.stream is None:
            # CORRECTION 2 : Définir un blocksize et une latence.
            # Sans blocksize, PortAudio demande des tout petits paquets,
            # ce qui tue les performances Python. 
            # 2048 ou 4096 samples est un bon compromis (env 40ms à 100ms de latence).
            self.stream = sd.OutputStream(
                samplerate=self.target_samplerate,
                channels=self.channels,
                callback=self._callback,
                dtype=self.dtype,
                blocksize=4096,  # IMPORTANT pour la stabilité
                latency='high'   # Demande à l'OS d'être moins agressif
            )
            self.stream.start()
        self.state = PlaybackState.PLAYING

    def pause(self):
        self.state = PlaybackState.PAUSED

    def stop(self):
        self.state = PlaybackState.STOPPED
        self.stop_event.set()
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
        # Vidage rapide de la queue
        while not self.audio_q.empty():
            try:
                self.audio_q.get_nowait()
            except queue.Empty:
                break
        
        if self.decoder_thread:
            self.decoder_thread.join(timeout=0.2)
            self.decoder_thread = None

    def get_time(self):
        return self.current_time
    
    def get_duration(self):
        return self.duration

# --- Exemple d'utilisation ---
# engine = AudioEngine()
# engine.load("Jérémy Frerot - Un homme.mp3")
# engine.play()
# while engine.get_time() < engine.get_duration():
#     time.sleep(1)