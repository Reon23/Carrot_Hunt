import pygame
import math
from animator import Animate

class Player:
    
    #Initalize player variables
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animations = [
            './assets/player/walk_down.png',
            './assets/player/walk_left.png',
            './assets/player/walk_right.png'
        ]
        self.player = Animate(self.animations[0], self.x, self.y, self.width, self.height)
    
    def render(self, screen, keys):
        direction = "d"

        if keys[pygame.K_a]:
            direction = "l"
        elif keys[pygame.K_d]:
            direction = "r"
        elif keys[pygame.K_s]:
            direction = "d"

        # Map directions
        animation_map = {"l": 1, "r": 2, "d": 0}

        self.player = Animate(self.animations[animation_map[direction]], self.x, self.y, self.width, self.height)
        self.player.animate(screen, 2)

class PlayerBullet:

    #Initalize bullet variables
    def __init__(self, x, y, mouse_x, mouse_y):
        self.x = x
        self.y = y
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.speed = 15
        self.angle = math.atan2(y-mouse_y, x-mouse_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed

    def render(self, screen):
        self.x -= int(self.x_vel)
        self.y -= int(self.y_vel)

        pygame.draw.circle(screen, "black", (self.x, self.y), 5) 