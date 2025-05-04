import pygame
import math
from game import time
from animator import Animate
from audio import SFXplayer

bullets = pygame.sprite.Group()

def reset_bullets():
    for bullet in bullets:
        bullets.remove_internal(bullet)

class Ak47:

    def __init__(self, x, y, scale, player_speed):
        self.x = x
        self.y = y
        self.width = 96
        self.height = 48
        self.scale = scale
        self.mouse_x, self.mouse_y = 0, 0
        
        self.bullet_speed = 50
        self.bullet_damage = 30
        self.last_update = pygame.time.get_ticks()
        self.player_speed = player_speed

        self.animations = {
            "idle": Animate('./assets/weapons/ak47/AK 47.png', self.x, self.y, self.width, self.height, 1, 0, self.scale, 50),
            "shoot": Animate('./assets/weapons/ak47/FIRE AK 47.png', self.x, self.y, self.width, self.height, 12, 0, self.scale, 20)
        }
        self.weapon_state = "idle"
        self.flipped = False

        self.weapon_sfx = SFXplayer('./assets/audio/ak47.ogg', 0.3)

    def rotateWeapon(self, player_x, player_y):
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        
        rel_x, rel_y = self.mouse_x - player_x, self.mouse_y - player_y
        angle = (180 / math.pi) * math.atan2(-rel_y, rel_x)  # Calculate correct angle

        # Determine if the weapon should be flipped
        self.flipped = rel_x < 0  # Flip when the mouse is to the left

        # If flipped, adjust the angle to maintain correct rotation
        if self.flipped:
            angle = -angle + 180  # Invert the Y rotation when flipped

        return angle
    
    def handleFire(self, pos_x, pos_y, angle):
        current_time = pygame.time.get_ticks()
        animation = self.animations[self.weapon_state]
        animation_duration = animation.frames * animation.animation_cooldown

        if current_time - self.last_update >= animation_duration: 
            self.last_update = current_time
            
            angle = self.rotateWeapon(pos_x, pos_y)
            
            # Muzzle offset (adjust this based on your weapon's dimensions)
            muzzle_offset = 5  # Adjust this to match the tip of your AK-47
            muzzle_x = pos_x + math.cos(math.radians(angle)) * muzzle_offset
            muzzle_y = pos_y - math.sin(math.radians(angle)) * muzzle_offset

            self.weapon_sfx.stopSound()
            self.weapon_sfx.playSound()
            bullets.add_internal(Bullet(muzzle_x, muzzle_y, self.mouse_x, self.mouse_y, self.bullet_speed, angle, self.bullet_damage, 50, 5))


    def renderBullets(self, screen, keys):
        
        if keys[pygame.K_a]:
            for bullet in bullets:
                bullet.x += self.player_speed * time['delta'] * 60
        if keys[pygame.K_d]:
            for bullet in bullets:
                bullet.x -= self.player_speed * time['delta'] * 60
        if keys[pygame.K_w]:
            for bullet in bullets:
                bullet.y += self.player_speed * time['delta'] * 60
        if keys[pygame.K_s]:
            for bullet in bullets:
                bullet.y -= self.player_speed * time['delta'] * 60
        
        for bullet in bullets:
            bullet.render(screen, self.flipped)
    
    def render(self, screen, pos_x, pos_y, keys):
        angle = self.rotateWeapon(pos_x, pos_y)

        # Adjust position offsets when flipping
        if self.flipped:
            offset_x, offset_y = -10, 26  # Adjust weapon position when flipped
        else:
            offset_x, offset_y = 10, 26  # Normal position

        mouse_button = pygame.mouse.get_pressed();

        if mouse_button[0]:
            self.weapon_state = "shoot"
            self.handleFire(pos_x + offset_x, pos_y + offset_y - 10, angle)
        else:
            self.weapon_state = "idle"
        self.renderBullets(screen, keys)
        self.animations[self.weapon_state].animate(screen, True, pos_x + offset_x, pos_y + offset_y, angle, self.flipped)

class Bullet:
    
    #Initalize bullet variables
    def __init__(self, x, y, mouse_x, mouse_y, speed, angle, damage, width = 10, height = 10, color = "yellow", lifetime = 250):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.speed = speed
        self.bullet_angle = angle
        self.damage = damage
        self.angle = math.atan2(y-mouse_y, x-mouse_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed
        self.hitbox = None
        self.bullet_sfx = SFXplayer('./assets/audio/impact.ogg')
        
        # Create a bullet surface with transparency
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill(self.color)  # Fill it with the specified color

        # bulletlifetime
        self.last_update = pygame.time.get_ticks()
        self.bullet_lifetime = lifetime

    def kill(self):
        self.bullet_sfx.playSound()
        bullets.remove_internal(self)
    
    def render(self, screen, flipped):
        current_time = pygame.time.get_ticks()
        self.x -= int(self.x_vel * time['delta'] * 60)
        self.y -= int(self.y_vel * time['delta'] * 60)

        if current_time - self.last_update >= self.bullet_lifetime:
            bullets.remove_internal(self)

        # Use correct angle for rotation (visual)
        visual_angle = -self.bullet_angle if flipped else self.bullet_angle
        rotated_image = pygame.transform.rotate(self.image, visual_angle)

        # Use self.angle (radians) for hitbox size calculation
        rotated_width = abs(self.width * math.cos(self.angle)) + abs(self.height * math.sin(self.angle))
        rotated_height = abs(self.width * math.sin(self.angle)) + abs(self.height * math.cos(self.angle))

        # Update hitbox
        self.hitbox = pygame.Rect(
            self.x - rotated_width // 2,
            self.y - rotated_height // 2,
            rotated_width,
            rotated_height
        )

        # Center the rotated image on (self.x, self.y)
        rotated_rect = rotated_image.get_rect(center=(self.x, self.y))

        # Draw the bullet
        screen.blit(rotated_image, rotated_rect.topleft)

        # draw hitbox for debug
        # pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 1)

class GlockP80:
    def __init__(self, x, y, scale, player_speed):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 48
        self.scale = scale
        self.mouse_x, self.mouse_y = 0, 0
        
        self.bullet_speed = 60  # Faster than AK-47
        self.bullet_damage = 8
        self.last_update = pygame.time.get_ticks()
        self.fire_rate = 250  # Faster fire rate (100ms cooldown)
        self.player_speed = player_speed

        self.animations = {
            "idle": Animate('./assets/weapons/Glock/Fire Glock.png', self.x, self.y, self.width, self.height, 1, 0, self.scale, 50),
            "shoot": Animate('./assets/weapons/Glock/Fire Glock.png', self.x, self.y, self.width, self.height, 10, 0, self.scale, 15)
        }
        self.weapon_state = "idle"
        self.flipped = False

        self.weapon_sfx = SFXplayer('./assets/audio/gawk.ogg', 0.4)

    def rotateWeapon(self, player_x, player_y):
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        
        rel_x, rel_y = self.mouse_x - player_x, self.mouse_y - player_y
        angle = (180 / math.pi) * math.atan2(-rel_y, rel_x)
        
        self.flipped = rel_x < 0
        if self.flipped:
            angle = -angle + 180
        
        return angle
    
    def handleFire(self, pos_x, pos_y, angle):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.fire_rate: 
            self.last_update = current_time
            
            angle = self.rotateWeapon(pos_x, pos_y)
            muzzle_offset = 6
            muzzle_x = pos_x + math.cos(math.radians(angle)) * muzzle_offset
            muzzle_y = pos_y - math.sin(math.radians(angle)) * muzzle_offset
            
            self.weapon_sfx.stopSound()
            self.weapon_sfx.playSound()
            bullets.add_internal(Bullet(muzzle_x, muzzle_y, self.mouse_x, self.mouse_y, self.bullet_speed, angle, self.bullet_damage, 45, 5))

    def renderBullets(self, screen, keys):
        for bullet in bullets:
            bullet.render(screen, self.flipped)
    
    def render(self, screen, pos_x, pos_y, keys):
        angle = self.rotateWeapon(pos_x, pos_y)
        
        offset_x, offset_y = (-10, 24) if self.flipped else (10, 24)
        
        mouse_button = pygame.mouse.get_pressed()
        
        if mouse_button[0]:
            self.weapon_state = "shoot"
            self.handleFire(pos_x + offset_x, pos_y + offset_y - 10, angle)
        else:
            self.weapon_state = "idle"
        
        self.renderBullets(screen, keys)
        self.animations[self.weapon_state].animate(screen, True, pos_x + offset_x, pos_y + offset_y, angle, self.flipped)

class Submachine:

    def __init__(self, x, y, scale, player_speed):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 48
        self.scale = scale
        self.mouse_x, self.mouse_y = 0, 0
        
        self.bullet_speed = 60
        self.bullet_damage = 20
        self.last_update = pygame.time.get_ticks()
        self.fire_rate = 100
        self.player_speed = player_speed

        self.animations = {
            "idle": Animate('./assets/weapons/Submachine/Fire Submachine.png', self.x, self.y, self.width, self.height, 1, 0, self.scale, 50),
            "shoot": Animate('./assets/weapons/Submachine/Fire Submachine.png', self.x, self.y, self.width, self.height, 10, 0, self.scale, 15)
        }
        self.weapon_state = "idle"
        self.flipped = False

        self.weapon_sfx = SFXplayer('./assets/audio/submachine.ogg', 1)

    def rotateWeapon(self, player_x, player_y):
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        
        rel_x, rel_y = self.mouse_x - player_x, self.mouse_y - player_y
        angle = (180 / math.pi) * math.atan2(-rel_y, rel_x)
        
        self.flipped = rel_x < 0
        if self.flipped:
            angle = -angle + 180
        
        return angle
    
    def handleFire(self, pos_x, pos_y, angle):
        current_time = pygame.time.get_ticks()
        animation = self.animations[self.weapon_state]
        animation_duration = animation.frames * animation.animation_cooldown

        if current_time - self.last_update >= animation_duration: 
            self.last_update = current_time
            
            angle = self.rotateWeapon(pos_x, pos_y)
            muzzle_offset = 8  
            muzzle_x = pos_x + math.cos(math.radians(angle)) * muzzle_offset
            muzzle_y = pos_y - math.sin(math.radians(angle)) * muzzle_offset

            self.weapon_sfx.stopSound()
            self.weapon_sfx.playSound()
            bullets.add_internal(Bullet(muzzle_x, muzzle_y, self.mouse_x, self.mouse_y, self.bullet_speed, angle, self.bullet_damage, 40, 5, "orange"))

    def renderBullets(self, screen, keys):
        for bullet in bullets:
            if keys[pygame.K_a]: bullet.x += self.player_speed * time['delta'] * 60
            if keys[pygame.K_d]: bullet.x -= self.player_speed * time['delta'] * 60
            if keys[pygame.K_w]: bullet.y += self.player_speed * time['delta'] * 60
            if keys[pygame.K_s]: bullet.y -= self.player_speed * time['delta'] * 60
            bullet.render(screen, self.flipped)
    
    def render(self, screen, pos_x, pos_y, keys):
        angle = self.rotateWeapon(pos_x, pos_y)
        offset_x, offset_y = (-12, 28) if self.flipped else (12, 28)

        mouse_button = pygame.mouse.get_pressed()
        
        if mouse_button[0]:
            self.weapon_state = "shoot"
            self.handleFire(pos_x + offset_x, pos_y + offset_y - 10, angle)
        else:
            self.weapon_state = "idle"
        
        self.renderBullets(screen, keys)
        self.animations[self.weapon_state].animate(screen, True, pos_x + offset_x, pos_y + offset_y, angle, self.flipped)

class AR:

    def __init__(self, x, y, scale, player_speed):
        self.x = x
        self.y = y
        self.width = 128
        self.height = 48
        self.scale = scale
        self.mouse_x, self.mouse_y = 0, 0
        
        self.bullet_speed = 60
        self.bullet_damage = 25
        self.last_update = pygame.time.get_ticks()
        self.fire_rate = 100
        self.player_speed = player_speed

        self.animations = {
            "idle": Animate('./assets/weapons/ar/ar.png', self.x, self.y, self.width, self.height, 1, 0, self.scale, 50),
            "shoot": Animate('./assets/weapons/ar/ar.png', self.x, self.y, self.width, self.height, 12, 0, self.scale, 10)
        }
        self.weapon_state = "idle"
        self.flipped = False

        self.weapon_sfx = SFXplayer('./assets/audio/ar.ogg')

    def rotateWeapon(self, player_x, player_y):
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        
        rel_x, rel_y = self.mouse_x - player_x, self.mouse_y - player_y
        angle = (180 / math.pi) * math.atan2(-rel_y, rel_x)
        
        self.flipped = rel_x < 0
        if self.flipped:
            angle = -angle + 180
        
        return angle
    
    def handleFire(self, pos_x, pos_y, angle):
        current_time = pygame.time.get_ticks()
        animation = self.animations[self.weapon_state]
        animation_duration = animation.frames * animation.animation_cooldown

        if current_time - self.last_update >= animation_duration: 
            self.last_update = current_time
            
            angle = self.rotateWeapon(pos_x, pos_y)
            muzzle_offset = 8  
            muzzle_x = pos_x + math.cos(math.radians(angle)) * muzzle_offset
            muzzle_y = pos_y - math.sin(math.radians(angle)) * muzzle_offset

            self.weapon_sfx.stopSound()
            self.weapon_sfx.playSound()
            bullets.add_internal(Bullet(muzzle_x, muzzle_y, self.mouse_x, self.mouse_y, self.bullet_speed, angle, self.bullet_damage, 40, 5, "red"))

    def renderBullets(self, screen, keys):
        for bullet in bullets:
            if keys[pygame.K_a]: bullet.x += self.player_speed * time['delta'] * 60
            if keys[pygame.K_d]: bullet.x -= self.player_speed * time['delta'] * 60
            if keys[pygame.K_w]: bullet.y += self.player_speed * time['delta'] * 60
            if keys[pygame.K_s]: bullet.y -= self.player_speed * time['delta'] * 60
            bullet.render(screen, self.flipped)
    
    def render(self, screen, pos_x, pos_y, keys):
        angle = self.rotateWeapon(pos_x, pos_y)
        offset_x, offset_y = (-12, 20) if self.flipped else (12, 20)

        mouse_button = pygame.mouse.get_pressed()
        
        if mouse_button[0]:
            self.weapon_state = "shoot"
            self.handleFire(pos_x + offset_x, pos_y + offset_y - 10, angle)
        else:
            self.weapon_state = "idle"
        
        self.renderBullets(screen, keys)
        self.animations[self.weapon_state].animate(screen, True, pos_x + offset_x, pos_y + offset_y, angle, self.flipped)