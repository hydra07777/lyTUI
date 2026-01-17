import vlc

class AudioEngine:
    def __init__(self):
        self.player = vlc.MediaPlay()

    def play(self, song):
        self.player.set_media(vlc.Media(song))
        self.player.play()
    def pause(self):
        self.player.pause()
       
    def stop(self):
        self.player.stop()

    def get_time(self):
        """temps en millisecondes"""
        ms = self.player.get_time()
        return max(0, ms//1000)