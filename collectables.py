import pygame
from animator import Animate

collectable_list = pygame.sprite.Group()

class Carrot(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        self.x = x
        self.y = y
        self.render_x = self.x
        self.render_y = self.y
        self.points = 30
        self.width = 32
        self.height = 32
        self.offset = 30
        self.scale = scale
        self.sprite = Animate('./assets/collectables/carrot/carrot.png', 
                              self.x, self.y, self.width, self.height, 8, 0, self.scale, 100)
        self.hitbox = pygame.Rect(self.render_x, self.render_y, self.width//4, self.height//4)

    def handleCollision(self, player):
        self.hitbox = pygame.Rect(self.render_x + self.offset//2, self.render_y + self.offset//2, 
                                  (self.width * self.scale) - self.offset, (self.height * self.scale) - self.offset)
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

        if self.hitbox.colliderect(player_rect):
            player.player_score.addScore(self.points)
            self.kill()
    
    def updatePosition(self, displayScroll):
        self.render_x = self.x - displayScroll[0]
        self.render_y = self.y - displayScroll[1]

    def kill(self):
        collectable_list.remove_internal(self)

    def render(self, screen):
        self.sprite.animate_old(screen, self.render_x, self.render_y)

class Heart(pygame.sprite.Sprite):
    def __init__(self, x, y, points):
        self.x = x
        self.y = y
        self.render_x = self.x
        self.render_y = self.y
        self.offset = 30
        self.width = 32
        self.height = 32
        self.scale = 1.75
        self.points = points
        self.sprite = Animate('./assets/collectables/heart/demonheart.png', 
                              self.x, self.y, self.width, self.height, 7, 0, self.scale, 100)
    
    def handleCollision(self, player):
        self.hitbox = pygame.Rect(self.render_x + self.offset//2, self.render_y + self.offset//2, 
                                  (self.width * self.scale) - self.offset, (self.height * self.scale) - self.offset)
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

        if self.hitbox.colliderect(player_rect):
            player.heal(self.points)
            self.kill()
    
    def updatePosition(self, displayScroll):
        self.render_x = self.x - displayScroll[0]
        self.render_y = self.y - displayScroll[1]
    
    def kill(self):
        collectable_list.remove_internal(self)

    def render(self, screen):
        self.sprite.animate_old(screen, self.render_x, self.render_y)