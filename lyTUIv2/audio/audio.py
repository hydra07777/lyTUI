import sounddevice as sd
import soundfile as sf
import threading

class PlaybackState:
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"

class AudioEngine:
    def __init__(self):
        self.state = PlaybackState.STOPPED
        self.buffer = None
        self.samplerate = None
        self.channels = None

        self.frame_index = 0
        self.stream = None
        self.lock = threading.Lock()

    def load(self, path):
        self.buffer, self.samplerate = sf.read(path, dtype="float32")
        if self.buffer.ndim  == 1:
            self.buffer = self.buffer[:,None]
        self.channels = self.buffer.shape[1]

        self.frame_index = 0
        self.state = PlaybackState.STOPPED

    def _callback(self, oudata, frames, time, status):
        with self.lock:
            if self.state != PlaybackState.PLAYING:
                oudata.fill(0)
                return
            end = self.frame_index + frames
            chunk = self.buffer[self.frame_index:end]

            if len(chunk) < frames:
                oudata[:len(chunk)] = chunk
                oudata[len(chunk):].fill(0)
                self.stop()
                return
            
            oudata[:] = chunk
            self.frame_index = end

    def play(self):
        if self.stream is None:
            self.stream = sd.OutputStream(samplerate=self.samplerate, channels=self.channels, callback=self._callback)
            self.stream.start()
        self.state = PlaybackState.PLAYING

    def pause(self):
        self.state = PlaybackState.PAUSED
    
    def resume(self):
        if self.state == PlaybackState.PAUSED:
            self.state = PlaybackState.PLAYING

    def stop(self):
        self.state = PlaybackState.PAUSED
        self.frame_index = 0

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    def get_time(self):
        return self.frame_index / self.samplerate