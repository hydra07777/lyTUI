"""
Audio player module using Pygame for MP3 playback.
"""

from mutagen.mp3 import MP3
import pygame

class AudioPlayer:
    """
    Simple audio player using Pygame mixer.

    Handles loading, playing, pausing, and position tracking of MP3 files.
    """

    def __init__(self):
        pygame.mixer.init()
        self.length = 0

    def load(self, path):
        pygame.mixer.music.load(path)
        self.length = MP3(path).info.length

    def play(self):
        pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def stop(self):
        pygame.mixer.music.stop()

    def position(self):
        pos = pygame.mixer.music.get_pos()
        return max(0, pos / 1000)
