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
            "idle" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 0, self.scale),
            "follow" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 1, self.scale)
        }
        self.mode = "idle"
    
        # Variables to create a wobbly/sloppy movement effect
        self.sloppy_offset_x = random.uniform(-10, 10)
        self.sloppy_offset_y = random.uniform(-10, 10)
        self.sloppy_timer = 0   

        # Distance at which enemy stops moving toward the player
        self.stop_radius = 150  # Enemy stops moving within this radius from the player

    def updatePosition(self, display_scroll):
        self.render_x = self.x - display_scroll[0]
        self.render_y = self.y - display_scroll[1]  

    def moveToPlayer(self, player_x, player_y, display_scroll):
        # Adjust player's position with display scroll
        adjusted_player_x = player_x + display_scroll[0]
        adjusted_player_y = player_y + display_scroll[1]

        # Calculate direction vector
        dx = adjusted_player_x - self.x
        dy = adjusted_player_y - self.y

        # Calculate the distance
        distance = math.sqrt(dx**2 + dy**2)
        
        # Enemy stops moving if it's within the stop radius
        if distance > self.stop_radius:
            if distance != 0:
                # Normalize the direction
                dx /= distance
                dy /= distance

                # Introduce a slight delay before changing the randomness
                self.sloppy_timer += 1
                if self.sloppy_timer % 10 == 0:  # Change direction slightly every 10 frames
                    self.sloppy_offset_x = random.uniform(-1.5, 1.5)
                    self.sloppy_offset_y = random.uniform(-1.5, 1.5)

                # Apply movement with a bit of randomness
                self.x += (dx * self.speed) + self.sloppy_offset_x
                self.y += (dy * self.speed) + self.sloppy_offset_y
                self.mode = "follow"
        else:
            self.mode = "idle"  # Enemy stops moving
    
    def render(self, screen):
        self.animations[self.mode].animate(screen, True, self.render_x, self.render_y)
