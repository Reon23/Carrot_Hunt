import pygame
import math
from animator import Animate
        
        
enemy_list = pygame.sprite.Group()

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
        self.hurt = False
        self.last_hit_time = 0
        self.hit_cooldown = 2000
        # self.death_start_time = None
        # self.death_duration = 1000

        self.animations = {
            "idle" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 0, self.scale, 50),
            "follow" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 1, self.scale, 50),
            "hit" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 2, 2, self.scale, 50),
            "death" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 7, 6, self.scale, 50)
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

        # ** Separation logic to prevent enemies from overlapping **
        separation_x, separation_y = 0, 0
        min_separation_distance = 100  # Adjust based on enemy size

        for other in enemy_list:
            if other != self:  # Don't check against itself
                diff_x = self.x - other.x
                diff_y = self.y - other.y
                enemy_distance = math.sqrt(diff_x**2 + diff_y**2)

                if enemy_distance < min_separation_distance:  # If too close
                    # Apply a force away from the other enemy
                    separation_x += diff_x / enemy_distance
                    separation_y += diff_y / enemy_distance

        # Normalize the separation force
        separation_magnitude = math.sqrt(separation_x**2 + separation_y**2)
        if separation_magnitude > 0:
            separation_x = (separation_x / separation_magnitude) * self.speed
            separation_y = (separation_y / separation_magnitude) * self.speed

        # Move only if outside stop radius
        if distance > self.stop_radius:
            # Normalize movement vector
            self.x += (dx / distance) * self.speed + separation_x
            self.y += (dy / distance) * self.speed + separation_y
            
            self.mode = "hit" if self.hurt else "follow"
        else:
            self.mode = "hit" if self.hurt else "idle"

    def handleCollision(self, bullet_group):
        if self.hurt:
            current = pygame.time.get_ticks()
        else:
            current = 0
        enemy_rect = pygame.Rect(self.render_x + self.width//2, self.render_y + self.height + 10, self.width//2, self.height)
        # pygame.draw.rect(screen, "red", enemy_rect)
        for bullet in bullet_group.sprites():  # Iterate over bullets properly
            bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
            if enemy_rect.colliderect(bullet_rect):  # Check collision
                print("hit")
                self.hurt = True
                self.health -= bullet.damage
                self.mode = "hit"
                bullet.kill()  # Remove bullet on impact

        if current - self.last_hit_time >= self.hit_cooldown:
            print("reset")
            self.last_hit_time = current
            self.hurt = False

        if self.health <= 0:
            self.mode = "death"
            enemy_list.remove_internal(self)  # Remove enemy when health reaches zero

    def render(self, screen, player_x, player_y, display_scroll):
        
        # Render with corrected position
        self.moveToPlayer(player_x, player_y, display_scroll)

        # self.animations[self.mode].animate(screen, True, self.render_x, self.render_y, 0, False)
        if self.flipped:
            self.animations[self.mode].animate_old(screen, self.render_x - 200, self.render_y, self.flipped)
        else:
            self.animations[self.mode].animate_old(screen, self.render_x, self.render_y, self.flipped)