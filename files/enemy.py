import pygame
import math
import random
import numpy as np
from game import time
from audio import SFXplayer
from animator import Animate
from collectables import collectable_list, Heart
from numba import njit

enemy_list = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

def reset_enemy():
    for enemy in enemy_list:
        enemy_list.remove_internal(enemy)
    for bullet in enemy_bullets.sprites():
        bullet.kill()

# This function computes the separation force for enemy avoidance.
@njit
def compute_separation(x, y, speed, enemy_positions, min_separation_distance, smoothing=0.2):
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
        separation_x = (separation_x / separation_magnitude) * speed * smoothing
        separation_y = (separation_y / separation_magnitude) * speed * smoothing
    return separation_x, separation_y



class Morph1(pygame.sprite.Sprite):
    
    def __init__(self, x, y, width, height, scale):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scale = scale
        self.speed = 6

        self.render_x = x
        self.render_y = y
        
        self.health = 50
        self.drop_health = 0.35
        self.drop_points = self.health//2
        self.points = 40
        self.weakened_health = 10
        self.hurt = False
        self.attack = False
        self.attack_hit = False
        self.post_attack_delay = 5000  # Rest time before another attack
        self.last_post_attack_time = 0  # Tracks when attack was completed
        self.selected_attack = None
        self.last_attact_time = 0
        self.attack_cooldwon = 300
        self.last_hit_time = 0
        self.hit_cooldown = 2000
        self.play_sfx = True
        self.sfx_atk1 = SFXplayer('./assets/audio/morph_atk1.ogg', 1)
        self.sfx_atk2 = SFXplayer('./assets/audio/morph_atk2.mp3')

        self.animations = {
            "idle" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 0, self.scale, 50),
            "follow" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 1, self.scale, 50),
            "hit" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 2, 2, self.scale, 200),
            "death" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 7, 6, self.scale, 50),
            "atk1" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 8, 4, self.scale, 50),
            "atk2" : Animate('./assets/enemy/Morph1/Morph.png', self.x, self.y, self.width, self.height, 6, 5, self.scale, 120)
        }
        self.mode = "idle"
        self.flipped = False
    
        # Distance at which enemy stops moving toward the player
        self.stop_radius = 80  # Enemy stops moving within this radius from the player

        self.separation_update_interval = 60  # Update every specified frames
        self.frame_counter = 0
        self.cached_separation = (0.0, 0.0)

    def updatePosition(self, display_scroll, player, screen):
        player_x = player.x - (player.width * 2)
        player_y = player.y - (player.height * 2)
        self.render_x = self.x - display_scroll[0]
        self.render_y = self.y - display_scroll[1]  
        
        if not self.hurt or self.attack:
            self.moveToPlayer(player_x, player_y, display_scroll)

        if self.attack:
            self.handleAttack(player, screen)

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
        # Only update separation force every 'separation_update_interval' frames
        self.frame_counter += 1
        if self.frame_counter % self.separation_update_interval == 0:
            enemy_positions = []
            for other in enemy_list:
                if other != self:
                    enemy_positions.append((other.x, other.y))
            if enemy_positions:
                enemy_positions = np.array(enemy_positions, dtype=np.float64)
                separation_x, separation_y = compute_separation(
                    self.x, self.y, self.speed, enemy_positions, min_separation_distance=150
                )
                self.cached_separation = (separation_x, separation_y)
            else:
                self.cached_separation = (0.0, 0.0)
        else:
            separation_x, separation_y = self.cached_separation

        # Move only if outside stop radius
        if distance > self.stop_radius and not self.attack:
            # Normalize movement vector and add separation force
            self.x += (dx / distance) * (self.speed * time['delta'] * 60) + separation_x
            self.y += (dy / distance) * (self.speed * time['delta'] * 60) + separation_y
            self.mode = "hit" if self.hurt else "follow"
        else:
            if self.hurt:
                self.mode = "hit"
            else:
                if not self.attack:
                    self.mode = "idle"
            self.attack = True if not self.hurt else False

    def handleAttack(self, player, screen):
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
        
        if self.selected_attack == 'atk1' and self.play_sfx:
            self.sfx_atk1.playSound()
            self.play_sfx = False
        
        if self.selected_attack == 'atk2' and self.play_sfx:
            self.sfx_atk2.playSound()
            self.play_sfx = False
        self.attackHit(self.mode, player, screen)

        # If attack is finished (cooldown over), enter post-attack delay
        if current_time - self.last_attact_time >= self.attack_cooldwon:
            self.selected_attack = None  # Reset attack selection
            self.last_post_attack_time = current_time  # Start post-attack delay timer
            self.play_sfx = True
            self.attack = False  # Enemy is no longer attacking
            self.attack_hit = False
    
    def attackHit(self, type, player, screen):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        if self.attack:
            
            if type == "atk1":
                if not self.flipped:
                    enemy_rect = pygame.Rect(self.render_x + self.width//2 + 50, 
                            self.render_y + self.height + 30, 
                            self.width + 40, 
                            self.height
                            )
                else:
                    enemy_rect = pygame.Rect(self.render_x - self.width//2 - 50, 
                            self.render_y + self.height + 30, 
                            self.width + 40, 
                            self.height
                            )
                # pygame.draw.rect(screen, "red", enemy_rect)
                if enemy_rect.colliderect(player_rect):
                    if not self.attack_hit:
                        player.hurt(10)
                        self.attack_hit = True
            
            elif type == "atk2":
                if not self.flipped:
                    enemy_rect = pygame.Rect(self.render_x + self.width//2 + 50, 
                            self.render_y + self.height, 
                            self.width + 100, 
                            self.height + 50
                            )
                else:
                    enemy_rect = pygame.Rect(self.render_x - self.width//2 - 50, 
                            self.render_y + self.height, 
                            self.width + 100, 
                            self.height + 50
                            )
                # pygame.draw.rect(screen, "red", enemy_rect)
                if enemy_rect.colliderect(player_rect):
                    if not self.attack_hit:
                        player.hurt(10)
                        self.attack_hit = True


    def handleCollision(self, bullet_group, player):
        # start timer when hurt
        if self.hurt:
            current = pygame.time.get_ticks()
        else:
            current = 0
        # Enemy hitbox
        enemy_rect = pygame.Rect(self.render_x + self.width//2, self.render_y + self.height + 10, self.width//2, self.height)
        for bullet in bullet_group.sprites():
            if enemy_rect.colliderect(bullet.hitbox):
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
            self.dropHealth()
            self.mode = "death"
            player.player_score.addScore(self.points)
            enemy_list.remove_internal(self)  # Remove enemy when health reaches zero

    def dropHealth(self):
        if np.random.choice([True, False], p=[self.drop_health, 1-self.drop_health]):
            collectable_list.add_internal(Heart(self.x + self.width//2, self.y + self.height//2, self.drop_points))

    def render(self, screen):
        # Render with corrected position
        if self.flipped:
            self.animations[self.mode].animate_old(screen, self.render_x - 200, self.render_y, self.flipped)
        else:
            self.animations[self.mode].animate_old(screen, self.render_x, self.render_y, self.flipped)


class Morph2(pygame.sprite.Sprite):
    
    def __init__(self, x, y, width, height, scale):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scale = scale
        self.speed = 5 

        self.render_x = x
        self.render_y = y
        
        self.health = 70
        self.drop_health = 0.2
        self.drop_points = self.health//2
        self.points = 70
        self.weakened_health = 20
        self.hurt = False
        self.attack = False
        self.attack_hit = False
        self.post_attack_delay = 4000  # Rest time before another attack
        self.last_post_attack_time = 0  # Tracks when attack was completed
        self.selected_attack = None
        self.last_attack_time = 0
        self.attack_cooldown = 400
        self.last_hit_time = 0
        self.hit_cooldown = 2500
        self.play_sfx = True
        self.sfx_atk1 = SFXplayer('./assets/audio/morph_atk1.ogg', 1)
        self.sfx_atk2 = SFXplayer('./assets/audio/morph_atk2.mp3')

        self.animations = {
            "idle": Animate('./assets/enemy/Morph2/Morph2.png', self.x, self.y, self.width, self.height, 6, 0, self.scale, 50),
            "follow": Animate('./assets/enemy/Morph2/Morph2.png', self.x, self.y, self.width, self.height, 6, 1, self.scale, 50),
            "hit": Animate('./assets/enemy/Morph2/Morph2.png', self.x, self.y, self.width, self.height, 2, 2, self.scale, 200),
            "death": Animate('./assets/enemy/Morph2/Morph2.png', self.x, self.y, self.width, self.height, 7, 6, self.scale, 50),
            "atk1": Animate('./assets/enemy/Morph2/Morph2.png', self.x, self.y, self.width, self.height, 8, 4, self.scale, 50),
            "atk2": Animate('./assets/enemy/Morph2/Morph2.png', self.x, self.y, self.width, self.height, 6, 5, self.scale, 120)
        }
        self.mode = "idle"
        self.flipped = False
    
        self.stop_radius = 100  # Morph2 stops a bit further away
        
        self.separation_update_interval = 60  # Update every specified frames
        self.frame_counter = 0
        self.cached_separation = (0.0, 0.0)

    def updatePosition(self, display_scroll, player, screen):
        player_x = player.x - (player.width * 2)
        player_y = player.y - (player.height * 2)
        self.render_x = self.x - display_scroll[0]
        self.render_y = self.y - display_scroll[1]  
        
        if not self.hurt or self.attack:
            self.moveToPlayer(player_x, player_y, display_scroll)

        if self.attack:
            self.handleAttack(player, screen)

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
        # Only update separation force every 'separation_update_interval' frames
        self.frame_counter += 1
        if self.frame_counter % self.separation_update_interval == 0:
            enemy_positions = []
            for other in enemy_list:
                if other != self:
                    enemy_positions.append((other.x, other.y))
            if enemy_positions:
                enemy_positions = np.array(enemy_positions, dtype=np.float64)
                separation_x, separation_y = compute_separation(
                    self.x, self.y, self.speed, enemy_positions, min_separation_distance=150
                )
                self.cached_separation = (separation_x, separation_y)
            else:
                self.cached_separation = (0.0, 0.0)
        else:
            separation_x, separation_y = self.cached_separation

        # Move only if outside stop radius
        if distance > self.stop_radius and not self.attack:
            # Normalize movement vector and add separation force
            self.x += (dx / distance) * (self.speed * time['delta'] * 60) + separation_x
            self.y += (dy / distance) * (self.speed * time['delta'] * 60) + separation_y
            self.mode = "hit" if self.hurt else "follow"
        else:
            if self.hurt:
                self.mode = "hit"
            else:
                if not self.attack:
                    self.mode = "idle"
            self.attack = True if not self.hurt else False

    def handleAttack(self, player, screen):
        current_time = pygame.time.get_ticks()
        options = ["atk1", "atk2"]
        probabilities = [0.7, 0.3]  # Higher chance for atk2

        if self.selected_attack is None and current_time - self.last_post_attack_time < self.post_attack_delay:
            self.attack = False
            return

        if self.selected_attack is None:
            self.selected_attack = np.random.choice(options, p=probabilities)
            animation = self.animations[self.selected_attack]
            self.attack_cooldown = animation.frames * animation.animation_cooldown
            self.last_attack_time = current_time
            self.mode = self.selected_attack
            self.attack = True
        
        if self.selected_attack == 'atk1' and self.play_sfx:
            self.sfx_atk1.playSound()
            self.play_sfx = False
        
        if self.selected_attack == 'atk2' and self.play_sfx:
            self.sfx_atk2.playSound()
            self.play_sfx = False
        self.attackHit(self.mode, player, screen)

        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.selected_attack = None
            self.last_post_attack_time = current_time
            self.attack = False
            self.play_sfx = False
            self.attack_hit = False

    def attackHit(self, type, player, screen):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        if self.attack:
            
            if type == "atk1":
                if not self.flipped:
                    enemy_rect = pygame.Rect(self.render_x + self.width//2 + 50, 
                            self.render_y + self.height + 30, 
                            self.width + 40, 
                            self.height
                            )
                else:
                    enemy_rect = pygame.Rect(self.render_x - self.width//2 - 50, 
                            self.render_y + self.height + 30, 
                            self.width + 40, 
                            self.height
                            )
                # pygame.draw.rect(screen, "red", enemy_rect)
                if enemy_rect.colliderect(player_rect):
                    if not self.attack_hit:
                        player.hurt(10)
                        self.attack_hit = True
            
            elif type == "atk2":
                enemy_rect = pygame.Rect(self.render_x, 
                        self.render_y + self.height, 
                        self.width + 100, 
                        self.height + 50
                        )
                # pygame.draw.rect(screen, "red", enemy_rect)
                if enemy_rect.colliderect(player_rect):
                    if not self.attack_hit:
                        player.hurt(10)
                        self.attack_hit = True

    def handleCollision(self, bullet_group, player):
        if self.hurt:
            current = pygame.time.get_ticks()
        else:
            current = 0

        enemy_rect = pygame.Rect(self.render_x + self.width//2, self.render_y + self.height + 10, self.width//2, self.height)
        for bullet in bullet_group.sprites():
            if enemy_rect.colliderect(bullet.hitbox):
                self.health -= bullet.damage
                
                if self.health <= self.weakened_health:
                    self.hurt = True
                    self.mode = "hit"
                bullet.kill()

        if current - self.last_hit_time >= self.hit_cooldown:
            self.last_hit_time = current
            self.hurt = False
            self.health = self.weakened_health + self.weakened_health//2

        if self.health <= 0:
            self.dropHealth()
            self.mode = "death"
            player.player_score.addScore(self.points)
            enemy_list.remove_internal(self)

    def dropHealth(self):
        if np.random.choice([True, False], p=[self.drop_health, 1-self.drop_health]):
            collectable_list.add_internal(Heart(self.x + self.width//2, self.y + self.height//2, self.drop_points))
    
    def render(self, screen):
        self.animations[self.mode].animate_old(screen, self.render_x - 120 if self.flipped else self.render_x, self.render_y, self.flipped)


class Mage(pygame.sprite.Sprite):
    
    def __init__(self, x, y, width, height, scale):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scale = scale
        self.speed = 5  # Slightly slower than Morph1

        self.render_x = x
        self.render_y = y
        
        self.health = 30  # More health than Morph1
        self.drop_health = 0.4
        self.drop_points = self.health//2
        self.points = 50
        self.weakened_health = 0
        self.dying = False
        self.attack = False
        self.attack_hit = False
        self.post_attack_delay = 4000  # Rest time before another attack
        self.last_post_attack_time = 0  # Tracks when attack was completed
        self.selected_attack = None
        self.last_attack_time = 0
        self.attack_cooldown = 400
        self.death_period = 0
        self.spell_cast = False
        self.play_sfx = True
        self.sfx_cast = SFXplayer('./assets/audio/mage_cast.ogg', 0.6)
        self.sfx_blob = SFXplayer('./assets/audio/mage_blob.ogg')

        self.animations = {
            "idle": Animate('./assets/enemy/Mage/Mage.png', self.x, self.y, self.width, self.height, 7, 0, self.scale, 50),
            "follow": Animate('./assets/enemy/Mage/Mage.png', self.x, self.y, self.width, self.height, 6, 1, self.scale, 50),
            "hit": Animate('./assets/enemy/Mage/Mage.png', self.x, self.y, self.width, self.height, 1, 4, self.scale, 200),
            "death": Animate('./assets/enemy/Mage/Mage.png', self.x, self.y, self.width, self.height, 9, 5, self.scale, 50),
            "atk1": Animate('./assets/enemy/Mage/Mage.png', self.x, self.y, self.width, self.height, 10, 3, self.scale, 50),
            "atk2": Animate('./assets/enemy/Mage/Mage.png', self.x, self.y, self.width, self.height, 10, 3, self.scale, 120)
        }
        self.mode = "idle"
        self.flipped = False
    
        self.stop_radius = 350  # Morph2 stops a bit further away
        
        self.separation_update_interval = 60  # Update every specified frames
        self.frame_counter = 0
        self.cached_separation = (0.0, 0.0)

    def updatePosition(self, display_scroll, player, screen):
        player_x = player.x - (player.width * 2)
        player_y = player.y - (player.height * 2)
        self.render_x = self.x - display_scroll[0]
        self.render_y = self.y - display_scroll[1]  
        
        if not self.dying or self.attack:
            self.moveToPlayer(player_x, player_y, display_scroll)

        if self.attack:
            self.handleAttack(player, screen)

    def moveToPlayer(self, player_x, player_y, display_scroll):
        # Calculate direction vector to the player
        target_x = player_x + display_scroll[0]
        enemy_center_x = self.x + (self.width // 2)
        
        dx = target_x - enemy_center_x
        dy = (player_y + display_scroll[1]) - (self.y + self.height)

        # Determine flipping based on movement direction
        if dx < 0 and not self.dying:
            self.flipped = True
        elif not self.dying:
            self.flipped = False

        # Calculate distance to player
        distance = math.sqrt(dx**2 + dy**2)

        # Separation logic to prevent enemies from overlapping
        # Only update separation force every 'separation_update_interval' frames
        self.frame_counter += 1
        if self.frame_counter % self.separation_update_interval == 0:
            enemy_positions = []
            for other in enemy_list:
                if other != self:
                    enemy_positions.append((other.x, other.y))
            if enemy_positions:
                enemy_positions = np.array(enemy_positions, dtype=np.float64)
                separation_x, separation_y = compute_separation(
                    self.x, self.y, self.speed, enemy_positions, min_separation_distance=150
                )
                self.cached_separation = (separation_x, separation_y)
            else:
                self.cached_separation = (0.0, 0.0)
        else:
            separation_x, separation_y = self.cached_separation

        # Move only if outside stop radius
        if distance > self.stop_radius and not self.attack:
            # Normalize movement vector and add separation force
            self.x += (dx / distance) * (self.speed * time['delta'] * 60) + separation_x
            self.y += (dy / distance) * (self.speed * time['delta'] * 60) + separation_y
            self.mode = "death" if self.dying else "follow"
        else:
            if self.dying:
                self.mode = "death"
            else:
                if not self.attack and not self.dying:
                    self.mode = "idle"
            self.attack = True if not self.dying else False

    def handleAttack(self, player, screen):
        current_time = pygame.time.get_ticks()
        options = ["atk1", "atk2"]
        probabilities = [0.65, 0.35] 

        if self.selected_attack is None and current_time - self.last_post_attack_time < self.post_attack_delay:
            self.attack = False
            return

        if self.selected_attack is None:
            self.selected_attack = np.random.choice(options, p=probabilities)
            animation = self.animations[self.selected_attack]
            self.attack_cooldown = animation.frames * animation.animation_cooldown
            self.last_attack_time = current_time
            self.mode = self.selected_attack
            self.attack = True

        if self.selected_attack == "atk1" and self.play_sfx:
            self.sfx_blob.playSound()
            self.play_sfx = False
        if self.selected_attack == "atk2" and self.play_sfx:
            self.sfx_cast.playSound()
            self.play_sfx = False
        
        self.attackHit(self.mode, player, screen)

        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.selected_attack = None
            self.last_post_attack_time = current_time
            self.attack = False
            self.play_sfx = True
            self.attack_hit = False
            self.spell_cast = False

    def attackHit(self, type, player, screen):
        if not self.spell_cast:
            
            if type == "atk1":
                if not self.spell_cast:
                    if not self.flipped:
                        enemy_bullets.add_internal(MageBlob((self.x + self.width * 1.6) + random.randrange(-30, 30), (self.y + self.height) + random.randrange(-30, 30)))
                    else:
                        enemy_bullets.add_internal(MageBlob((self.x - self.width//2) + random.randrange(-30, 30), (self.y + self.height) + random.randrange(-30, 30)))
                    self.spell_cast = True
            elif type == "atk2":
                if not self.spell_cast:
                    enemy_bullets.add_internal(MageCast())
                    self.spell_cast = True

    def handleCollision(self, bullet_group, player):

        enemy_rect = pygame.Rect(self.render_x + self.width//2, self.render_y + self.height + 10, self.width//2, self.height)
        for bullet in bullet_group.sprites():
            if enemy_rect.colliderect(bullet.hitbox):
                self.health -= bullet.damage
                bullet.kill()

        if self.health <= 0:
            self.mode = "death"

            if self.death_period == 0:
                self.death_period = pygame.time.get_ticks()
                self.dying = True
                return

            current_time = pygame.time.get_ticks()
            animation = self.animations["death"]
            death_cooldown = (animation.frames - 1) * animation.animation_cooldown
            if current_time - self.death_period >= death_cooldown:
                self.death_period = current_time
                player.player_score.addScore(self.points)
                self.dropHealth()
                enemy_list.remove_internal(self)
            else:
                return

    def dropHealth(self):
        if np.random.choice([True, False], p=[self.drop_health, 1-self.drop_health]):
            collectable_list.add_internal(Heart(self.x + self.width//2, self.y + self.height//2, self.drop_points))
    
    def render(self, screen):
        self.animations[self.mode].animate_old(screen, self.render_x - 200 if self.flipped else self.render_x, self.render_y, self.flipped)

class MageBlob(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.render_x = self.x
        self.render_y = self.y
        self.width = 64
        self.height = 64
        self.damage = 20
        self.health = 25
        self.points = 10
        self.speed = 10
        self.animation = {'follow' : Animate('./assets/enemy/Mage/MageBlob.png', self.x, self.y, self.width, self.height, 10, 0, 1, 50)}
        self.blob_rect = pygame.Rect(self.render_x + self.width//4, self.render_y + self.height//4, self.width//2, self.height//2)
        self.blob_destroy_sfx = SFXplayer('./assets/audio/blob_destroy.ogg')
        self.blobBehavior = 'follow'
        self.blobLife = 6000
        self.blobkilled = False
        self.lastupdate = pygame.time.get_ticks()

    def updatePosition(self, displayScroll, player):
        # Calculate the player's world position.
        player_world_x = player.x + displayScroll[0]
        player_world_y = player.y + displayScroll[1]

        # Compute the direction toward the player.
        dx = player_world_x - self.x
        dy = player_world_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            # Normalize and scale by the enemy's speed.
            dir_x = dx / distance
            dir_y = dy / distance

            follow_dx = dir_x * self.speed
            follow_dy = dir_y * self.speed

            # Curve movement: calculate a perpendicular vector (rotated 90 degrees)
            perp_x = -dir_y
            perp_y = dir_x

            # Use a sine wave based on time to oscillate the curve
            wave = math.sin(pygame.time.get_ticks() * 0.0035)  # frequency = 0.005
            curve_strength = 6  # tweak this for stronger curvature

            # Apply the curve to the direction
            curve_dx = perp_x * wave * curve_strength
            curve_dy = perp_y * wave * curve_strength

            follow_dx += curve_dx
            follow_dy += curve_dy
        else:
            follow_dx, follow_dy = 0, 0

        # Compute separation from other blobs (optional, but included)
        enemy_positions = np.array([
            (other.x, other.y) for other in enemy_bullets if other != self
        ], dtype=np.float32)

        if enemy_positions.any():
            sep_dx, sep_dy = compute_separation(self.x, self.y, self.speed, enemy_positions, 100)
            total_dx = (follow_dx + sep_dx) * (time['delta'] * 60)
            total_dy = (follow_dy + sep_dy) * (time['delta'] * 60)
        else:
            total_dx = follow_dx * (time['delta'] * 60)
            total_dy = follow_dy * (time['delta'] * 60)

        # Update world position
        self.x += total_dx
        self.y += total_dy

        # Update render position
        self.render_x = self.x - displayScroll[0]
        self.render_y = self.y - displayScroll[1]

    def handleCollision(self, player, screen):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        self.blob_rect = pygame.Rect(self.render_x + self.width//4, self.render_y + self.height//4, self.width//2, self.height//2)
        # pygame.draw.rect(screen, "red", blob_rect)

        if self.blob_rect.colliderect(player_rect):
            player.hurt(self.damage)
            self.kill()

    def handleBullets(self, bullets, player, screen):
        self.blob_rect = pygame.Rect(self.render_x + self.width//4, self.render_y + self.height//4, self.width//2, self.height//2)
        # pygame.draw.rect(screen, "red", self.blob_rect)
        for bullet in bullets:
            # bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height*1.5)
            bullet_rect = bullet.hitbox

            if self.blob_rect.colliderect(bullet_rect):
                self.hurt(bullet.damage, player)
                bullet.kill()

    def hurt(self, damage, player):
        self.health -= damage
        if self.health <= 0:
            player.player_score.addScore(self.points)
            self.blob_destroy_sfx.playSound()
            self.kill()
    
    def kill(self):
        if not self.blobkilled:
            enemy_bullets.remove_internal(self)
            self.blobkilled = True
    
    def render(self, screen):
        current_time = pygame.time.get_ticks()

        if current_time - self.lastupdate >= self.blobLife:
            self.kill()

        self.animation[self.blobBehavior].animate_old(screen, self.render_x, self.render_y)

class MageCast(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.render_x = self.x
        self.render_y = self.y
        self.width = 128
        self.height = 64
        self.damage = {'large': 30, 'medium': 40, 'small': 50}
        self.choice = ['large', 'medium', 'small']
        self.probabilities = [0.35, 0.5, 0.15]
        self.animations = {
            'small': Animate('./assets/enemy/Mage/mage_atk2.png', self.x, self.y, self.width, self.height, 6, 1, 3, 120),
            'medium': Animate('./assets/enemy/Mage/mage_atk2.png', self.x, self.y, self.width, self.height, 6, 0, 3, 120),
            'large': Animate('./assets/enemy/Mage/mage_atk2.png', self.x, self.y, self.width, self.height, 6, 2, 3,120)
        }
        self.cast_type = np.random.choice(self.choice, p=self.probabilities)
        self.cast_set = False
        self.cast_can_hit = False
        self.cast_hit = False
        self.lastupdate = pygame.time.get_ticks()

    def placeCast(self, player, displayScroll):
        if not self.cast_set:
            self.x = player.x + displayScroll[0] - random.randrange(-120, 120) - self.width
            self.y = player.y + displayScroll[1] - random.randrange(-120, 120) - self.height
            self.cast_set = True
        else:
            return

    def updatePosition(self, displayScroll, player):
        self.placeCast(player, displayScroll)
        self.render_x = self.x - displayScroll[0]
        self.render_y = self.y - displayScroll[1]

    def handleCollision(self, player, screen):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        if self.cast_type == "small":
            cast_rect = pygame.Rect(self.render_x + self.width * 1.25, self.render_y + self.height * 1.7, self.width//2, self.height//2)
        elif self.cast_type == "medium":
            cast_rect = pygame.Rect(self.render_x + self.width, self.render_y + self.height * 1.5, self.width, self.height//1.5)
        else:
            cast_rect = pygame.Rect(self.render_x + self.width - 10, self.render_y + self.height + 10, self.width * 1.4, self.height)

        # pygame.draw.rect(screen, "red", cast_rect)

        if cast_rect.colliderect(player_rect) and not self.cast_hit and self.cast_can_hit:
            player.hurt(self.damage[self.cast_type])
            self.cast_hit = True

    def render(self, screen):
        current = pygame.time.get_ticks()
        animation = self.animations[self.cast_type]
        animation_duration = animation.frames * animation.animation_cooldown

        if current - self.lastupdate >= animation_duration - 10:
            self.cast_can_hit = True
        # Only remove the cast after the animation has fully played
        if current - self.lastupdate >= animation_duration:
            self.lastupdate = current
            enemy_bullets.remove_internal(self)

        animation.animate_old(screen, self.render_x, self.render_y)

class Dummy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()  # or pygame.sprite.Sprite.__init__(self)
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.scale = 0
        self.speed = 6

        self.render_x = 0
        self.render_y = 0

        self.health = 50
        self.weakened_health = 10
        self.hurt = False

    def updatePosition(self, display_scroll, player = None, screen = None):
        pass

    def moveToPlayer(self, player_x, player_y, display_scroll):
        pass

    def handleAttack(self, player, screen):
        pass

    def attackHit(self, type, player, screen):
        pass

    def handleCollision(self, bullet_group, player = None):
        pass

    def render(self, screen):
        pass