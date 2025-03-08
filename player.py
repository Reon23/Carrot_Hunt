import pygame
import math
from animator import Animate
from weapons import Ak47, GlockP80, Submachine
from hud import healthBar

class Player:
    
    #Initalize player variables
    def __init__(self, x, y, width, height, player_speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.player_speed = player_speed
        self.player_health = healthBar(100)
        self.animations = {
            "d": Animate('./assets/player/walk_down.png', self.x, self.y, self.width, self.height, 5, 0, 2, 50),
            "l": Animate('./assets/player/walk_left.png', self.x, self.y, self.width, self.height, 8, 0, 2, 50),
            "r": Animate('./assets/player/walk_right.png', self.x, self.y, self.width, self.height, 8, 0, 2, 50),
        }
        self.direction = "d"
        self.current_animation = self.animations[self.direction]
        self.play_animation = False

        # self.player_weapon = Ak47(self.x, self.y, 0.8, self.player_speed)
        self.player_weapon = GlockP80(self.x, self.y, 0.8, self.player_speed)
        # self.player_weapon = Submachine(self.x, self.y, 0.8, self.player_speed)
    
    def hurt(self, damage):
        self.player_health.updateHealth(max(0, self.player_health.health - damage))
        if self.player_health.health - damage <= 0:
            self.kill()
    
    def kill(self):
        pass

    def render(self, screen, keys):
        self.direction = "d"

        # Handle player movement
        if keys[pygame.K_a]:
            self.direction = "l"
            self.play_animation = True
        if keys[pygame.K_d]:
            self.direction = "r"
            self.play_animation = True
        if keys[pygame.K_s] or keys[pygame.K_w]:
            self.direction = "d"
            self.play_animation = True
        if not keys[pygame.K_a] and not keys[pygame.K_d] and not keys[pygame.K_s] and not keys[pygame.K_w]:
            self.play_animation = False

        # Only change animation if direction changes
        if self.current_animation != self.animations[self.direction]:
            self.current_animation = self.animations[self.direction]

        # Update position for animation object
        self.current_animation.x = self.x
        self.current_animation.y = self.y

        # Animate current frame
        self.current_animation.animate(screen, self.play_animation, self.x, self.y, 0, False)
        self.player_weapon.render(screen, self.x, self.y, keys)
        self.player_health.render(screen)
