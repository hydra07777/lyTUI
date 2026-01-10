import pygame

class AudioEngine:
    def __init__(self):
        pygame.mixer.init()
    
    def play(self, song):
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
    
    def pause(self):
        pygame.mixer.music.pause()
    
    def stop(self):
        pygame.mixer.music.stop