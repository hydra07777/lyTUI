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
        
        # État interne
        self.state = PlaybackState.STOPPED
        self.stream = None
        self.audio_q = queue.Queue(maxsize=30) # Buffer de paquets décodés
        self.leftover = np.zeros((0, 2), dtype=self.dtype) # Surplus du callback
        
        # Contrôle et Métadonnées
        self.stop_event = threading.Event()
        self.decoder_thread = None
        self.duration = 0.0
        self.current_time = 0.0

    def load(self, path: str):
        """Charge n'importe quel fichier audio et prépare la lecture."""
        self.stop()
        
        self.stop_event.clear()
        self.current_time = 0.0
        self.leftover = np.zeros((0, 2), dtype=self.dtype)
        
        # Lancement du thread de décodage
        self.decoder_thread = threading.Thread(
            target=self._decoder_loop, 
            args=(path,), 
            daemon=True
        )
        self.decoder_thread.start()
        
        # Petite attente pour remplir le buffer initial (évite les coupures au départ)
        while self.audio_q.qsize() < 10 and self.decoder_thread.is_alive():
            time.sleep(0.01)
            
        self.state = PlaybackState.PAUSED

    def _decoder_loop(self, path):
        """Thread séparé qui décode le fichier vers la Queue."""
        container = None
        try:
            container = av.open(path)
            stream = container.streams.audio[0]
            self.duration = float(stream.duration * stream.time_base)

            # Conversion universelle vers le format de sortie
            resampler = av.AudioResampler(
                format=self.dtype,
                layout='stereo',
                rate=self.target_samplerate
            )

            for frame in container.decode(stream):
                if self.stop_event.is_set():
                    break
                
                frame.pts = None 
                frames = resampler.resample(frame)
                
                if frames:
                    # Conversion PyAV (Planar/Interleaved) -> Numpy (Samples, Channels)
                    array = frames[0].to_ndarray().transpose()
                    
                    # On pousse dans la queue (bloque si maxsize atteint, limitant la RAM)
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
        """Callback de la carte son (s'exécute dans un thread prioritaire)."""
        if status:
            pass # On peut logguer les 'output underflow' ici si besoin
            
        if self.state != PlaybackState.PLAYING:
            outdata.fill(0)
            return

        current_pos = 0
        
        # 1. On vide d'abord le surplus du tour précédent
        if len(self.leftover) > 0:
            take = min(frames, len(self.leftover))
            outdata[:take] = self.leftover[:take]
            self.leftover = self.leftover[take:]
            current_pos += take

        # 2. On complète avec les données de la Queue
        while current_pos < frames:
            needed = frames - current_pos
            try:
                data = self.audio_q.get_nowait()
                self.current_time += len(data) / self.target_samplerate
                
                if len(data) > needed:
                    outdata[current_pos:] = data[:needed]
                    self.leftover = data[needed:]
                    current_pos += needed
                else:
                    outdata[current_pos : current_pos + len(data)] = data
                    current_pos += len(data)
                    
            except queue.Empty:
                outdata[current_pos:].fill(0)
                # Si le décodeur a fini et plus de données : fin du morceau
                if not self.decoder_thread.is_alive() and len(self.leftover) == 0:
                     self.state = PlaybackState.STOPPED
                break

    def play(self):
        if self.state == PlaybackState.STOPPED and not self.decoder_thread:
            return
            
        if self.stream is None:
            self.stream = sd.OutputStream(
                samplerate=self.target_samplerate,
                channels=self.channels,
                callback=self._callback,
                dtype=self.dtype
            )
            self.stream.start()
        self.state = PlaybackState.PLAYING

    def pause(self):
        self.state = PlaybackState.PAUSED

    def stop(self):
        self.state = PlaybackState.STOPPED
        self.stop_event.set()
        
        # Nettoyage
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
        # Vider la queue proprement
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