import pygame
import math
import random
from animator import Animate

class Morph1:
    
    def __init__(self, x, y, width, height, scale):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scale = scale
        self.speed = 4

        self.render_x = x
        self.render_y = y

        self.animations = {
            "idle" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 0, self.scale, 50),
            "follow" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 1, self.scale, 50)
        }
        self.mode = "idle"
        self.flipped = False
    
        # Distance at which enemy stops moving toward the player
        self.stop_radius = 150  # Enemy stops moving within this radius from the player

    def updatePosition(self, display_scroll):
        self.render_x = self.x - display_scroll[0]
        self.render_y = self.y - display_scroll[1]  

    def moveToPlayer(self, player_x, player_y, display_scroll):
        # Calculate direction vector
        if not self.flipped:
            dx = (player_x + display_scroll[0]) - (self.x + (self.width//2 - 40))
        else:
            dx = (player_x + display_scroll[0]) - (self.x + (self.width//2 + 40)) + self.stop_radius
        print(dx)
        if dx < 0:
            self.flipped = True
        else:
            self.flipped = False
        # dx = player_x + display_scroll[0] - self.x
        dy = (player_y + display_scroll[1]) - (self.y + (self.height))

        # Calculate the distance to prevent division by zero
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.stop_radius:
            # Normalize the direction and apply speed
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            self.mode = "follow"
        else:
            self.mode = "idle"
    
    def render(self, screen, player_x, player_y, display_scroll):
        

        # Render with corrected position
        self.moveToPlayer(player_x, player_y, display_scroll)
        # self.animations[self.mode].animate(screen, True, self.render_x, self.render_y, 0, False)
        if self.flipped:
            self.animations[self.mode].animate_old(screen, self.render_x - 200, self.render_y, self.flipped)
        else:
            self.animations[self.mode].animate_old(screen, self.render_x, self.render_y, self.flipped)



