import pygame
from game import SCREEN_WIDTH, SCREEN_HEIGHT

class ScreenEffects:
    def __init__(self):
        self.fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade.fill((0, 0, 0))
        self.fade_alpha = 255
        self.fade_complete = False
        self.fade_in_complete = False

    def FadeOut(self, screen, speed = 1):
        if self.fade_alpha > 0:
            self.fade.set_alpha(self.fade_alpha)
            screen.blit(self.fade, (0, 0))
            self.fade_alpha -= speed  # adjust speed here
        else:
            self.fade_complete = True
            self.fade.set_alpha(0)
            screen.blit(self.fade, (0, 0))
    
    def FadeIn(self, screen, speed=1):
        if self.fade_alpha < 255:
            self.fade.set_alpha(self.fade_alpha)
            screen.blit(self.fade, (0, 0))
            self.fade_alpha += speed  # increase alpha to fade in
        else:
            self.fade_alpha = 255
            self.fade.set_alpha(self.fade_alpha)
            screen.blit(self.fade, (0, 0))
            self.fade_complete = True
            self.fade_in_complete = True
