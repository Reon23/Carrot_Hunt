import pygame
import math
from animator import Animate

class ak47:

    def __init__(self, x, y, scale):
        self.x = x
        self.y = y
        self.width = 96
        self.height = 48
        self.scale = scale

        self.animations = {
            "idle": Animate('./assets/weapons/ak47/AK 47.png', self.x, self.y, self.width, self.height, 1, 0, self.scale)
        }
        self.weapon_state = "idle"
        self.flipped = False

    def rotateWeapon(self, player_x, player_y):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        rel_x, rel_y = mouse_x - player_x, mouse_y - player_y
        angle = (180 / math.pi) * math.atan2(-rel_y, rel_x)  # Calculate correct angle

        # Determine if the weapon should be flipped
        self.flipped = rel_x < 0  # Flip when the mouse is to the left

        # If flipped, adjust the angle to maintain correct rotation
        if self.flipped:
            angle = -angle + 180  # Invert the Y rotation when flipped

        return angle
    
    def render(self, screen, pos_x, pos_y):
        angle = self.rotateWeapon(pos_x, pos_y)

        # Adjust position offsets when flipping
        if self.flipped:
            offset_x, offset_y = -10, 26  # Adjust weapon position when flipped
        else:
            offset_x, offset_y = 10, 26  # Normal position

        self.animations[self.weapon_state].animate(screen, True, pos_x + offset_x, pos_y + offset_y, angle, self.flipped)
