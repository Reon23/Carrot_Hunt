import pygame
from animator import Animate

collectable_list = pygame.sprite.Group()

class Carrot(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        self.x = x
        self.y = y
        self.render_x = self.x
        self.render_y = self.y
        self.width = 512
        self.height = 512
        self.scale = scale
        self.sprite = Animate('./assets/collectables/carrot/carrot.png', 
                              self.x, self.y, self.width, self.height, 7, 0, self.scale, 50)
    
    def updatePosition(self, displayScroll):
        self.render_x = self.x - displayScroll[0]
        self.render_y = self.y - displayScroll[1]

    def render(self, screen):
        self.sprite.animate_old(screen, self.render_x, self.render_y)