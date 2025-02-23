import pygame
import math
import numpy as np
from animator import Animate
from numba import njit

enemy_list = pygame.sprite.Group()

# This function computes the separation force for enemy avoidance.
@njit
def compute_separation(x, y, speed, enemy_positions, min_separation_distance):
    separation_x = 0.0
    separation_y = 0.0
    for i in range(enemy_positions.shape[0]):
        ex = enemy_positions[i, 0]
        ey = enemy_positions[i, 1]
        diff_x = x - ex
        diff_y = y - ey
        enemy_distance = math.sqrt(diff_x * diff_x + diff_y * diff_y)
        if enemy_distance < min_separation_distance and enemy_distance > 0:
            separation_x += diff_x / enemy_distance
            separation_y += diff_y / enemy_distance
    separation_magnitude = math.sqrt(separation_x * separation_x + separation_y * separation_y)
    if separation_magnitude > 0:
        separation_x = (separation_x / separation_magnitude) * speed
        separation_y = (separation_y / separation_magnitude) * speed
    return separation_x, separation_y

class Morph1(pygame.sprite.Sprite):
    
    def __init__(self, x, y, width, height, scale):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scale = scale
        self.speed = 4

        self.render_x = x
        self.render_y = y
        
        self.health = 50
        self.weakened_health = 10
        self.hurt = False
        self.attack = False
        self.post_attack_delay = 5000  # Rest time before another attack
        self.last_post_attack_time = 0  # Tracks when attack was completed
        self.selected_attack = None
        self.last_attact_time = 0
        self.attack_cooldwon = 300
        self.last_hit_time = 0
        self.hit_cooldown = 2000

        self.animations = {
            "idle" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 0, self.scale, 50),
            "follow" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 1, self.scale, 50),
            "hit" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 2, 2, self.scale, 200),
            "death" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 7, 6, self.scale, 50),
            "atk1" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 8, 4, self.scale, 50),
            "atk2" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 5, self.scale, 50)
        }
        self.mode = "idle"
        self.flipped = False
    
        # Distance at which enemy stops moving toward the player
        self.stop_radius = 150  # Enemy stops moving within this radius from the player

    def updatePosition(self, display_scroll):
        self.render_x = self.x - display_scroll[0]
        self.render_y = self.y - display_scroll[1]  

    def moveToPlayer(self, player_x, player_y, display_scroll):
        # Calculate direction vector to the player
        target_x = player_x + display_scroll[0]
        enemy_center_x = self.x + (self.width // 2)
        
        dx = target_x - enemy_center_x
        dy = (player_y + display_scroll[1]) - (self.y + self.height)

        # Determine flipping based on movement direction
        if dx < 0:
            self.flipped = True
        else:
            self.flipped = False

        # Calculate distance to player
        distance = math.sqrt(dx**2 + dy**2)

        # Separation logic to prevent enemies from overlapping
        min_separation_distance = 100  # Adjust based on enemy size
        enemy_positions = []
        for other in enemy_list:
            if other != self:
                enemy_positions.append((other.x, other.y))
        if enemy_positions:
            enemy_positions = np.array(enemy_positions, dtype=np.float64)
            separation_x, separation_y = compute_separation(self.x, self.y, self.speed, enemy_positions, min_separation_distance)
        else:
            separation_x, separation_y = 0.0, 0.0

        # Move only if outside stop radius
        if distance > self.stop_radius and not self.attack:
            # Normalize movement vector and add separation force
            self.x += (dx / distance) * self.speed + separation_x
            self.y += (dy / distance) * self.speed + separation_y
            self.mode = "hit" if self.hurt else "follow"
        else:
            if self.hurt:
                self.mode = "hit"
            else:
                if not self.attack:
                    self.mode = "idle"
            self.attack = True if not self.hurt else False

    def handleAttack(self):
        current_time = pygame.time.get_ticks()
        options = ["atk1", "atk2"]
        probabilities = [0.7, 0.3]

        # If the enemy is in the post-attack delay, it should not attack
        if self.selected_attack is None and current_time - self.last_post_attack_time < self.post_attack_delay:
            self.attack = False
            return

        # If no attack is selected, choose one and start attack cooldown
        if self.selected_attack is None:
            self.selected_attack = np.random.choice(options, p=probabilities)
            animation = self.animations[self.selected_attack]
            animation_duration = animation.frames * animation.animation_cooldown
            self.attack_cooldwon = animation_duration
            self.last_attact_time = current_time  # Start attack cooldown timer
            self.mode = self.selected_attack
            self.attack = True  # Set attack to True when actually attacking

        # If attack is finished (cooldown over), enter post-attack delay
        if current_time - self.last_attact_time >= self.attack_cooldwon:
            self.selected_attack = None  # Reset attack selection
            self.last_post_attack_time = current_time  # Start post-attack delay timer
            self.attack = False  # Enemy is no longer attacking

    def handleCollision(self, bullet_group):
        # start timer when hurt
        if self.hurt:
            current = pygame.time.get_ticks()
        else:
            current = 0
        # Enemy hitbox
        enemy_rect = pygame.Rect(self.render_x + self.width//2, self.render_y + self.height + 10, self.width//2, self.height)
        for bullet in bullet_group.sprites():
            bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
            if enemy_rect.colliderect(bullet_rect):
                self.health -= bullet.damage
                
                if self.health <= self.weakened_health:
                    self.hurt = True
                self.mode = "hit"
                bullet.kill()  # Remove bullet on impact

        # Reset weakened status after cooldown
        if current - self.last_hit_time >= self.hit_cooldown:
            self.last_hit_time = current
            self.hurt = False
            self.health = self.weakened_health + self.weakened_health//2

        if self.health <= 0:
            self.mode = "death"
            enemy_list.remove_internal(self)  # Remove enemy when health reaches zero

    def render(self, screen, player_x, player_y, display_scroll):
        
        if not self.hurt or self.attack:
            self.moveToPlayer(player_x, player_y, display_scroll)

        if self.attack:
            self.handleAttack()

        # Render with corrected position
        if self.flipped:
            self.animations[self.mode].animate_old(screen, self.render_x - 200, self.render_y, self.flipped)
        else:
            self.animations[self.mode].animate_old(screen, self.render_x, self.render_y, self.flipped)
