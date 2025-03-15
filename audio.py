import pygame
pygame.mixer.init

class SFXplayer:
    def __init__(self, audio, volume = 0.7):
        self.audio = pygame.mixer.Sound(audio)
        self.audio.set_volume(volume)

    def stopSound(self):
        self.audio.stop()

    def playSound(self):
        self.audio.play()