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
        self.animations = {
            "d": Animate('./assets/player/walk_down.png', self.x, self.y, self.width, self.height, 5, 2),
            "l": Animate('./assets/player/walk_left.png', self.x, self.y, self.width, self.height, 8, 2),
            "r": Animate('./assets/player/walk_right.png', self.x, self.y, self.width, self.height, 8, 2),
        }
        self.current_animation = self.animations["d"]
    
    def render(self, screen, keys):
        direction = "d"

        if keys[pygame.K_a]:
            direction = "l"
        elif keys[pygame.K_d]:
            direction = "r"
        elif keys[pygame.K_s]:
            direction = "d"

        # Only change animation if direction changes
        if self.current_animation != self.animations[direction]:
            self.current_animation = self.animations[direction]

        # Update position for animation object
        self.current_animation.x = self.x
        self.current_animation.y = self.y

        # Animate current frame
        self.current_animation.animate(screen)

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