import pygame
import math
from animator import Animate

bullets = pygame.sprite.Group()

class ak47:

    def __init__(self, x, y, scale, player_speed):
        self.x = x
        self.y = y
        self.width = 96
        self.height = 48
        self.scale = scale
        self.mouse_x, self.mouse_y = 0, 0
        
        self.bullet_speed = 50
        self.bullet_damage = 10
        self.last_update = pygame.time.get_ticks()
        self.player_speed = player_speed

        self.animations = {
            "idle": Animate('./assets/weapons/ak47/AK 47.png', self.x, self.y, self.width, self.height, 1, 0, self.scale, 50),
            "shoot": Animate('./assets/weapons/ak47/FIRE AK 47.png', self.x, self.y, self.width, self.height, 12, 0, self.scale, 20)
        }
        self.weapon_state = "idle"
        self.flipped = False


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

            bullets.add_internal(Bullet(muzzle_x, muzzle_y, self.mouse_x, self.mouse_y, self.bullet_speed, angle, self.bullet_damage, 50, 5))


    def renderBullets(self, screen, keys):
        
        if keys[pygame.K_a]:
            for bullet in bullets:
                bullet.x += self.player_speed
        if keys[pygame.K_d]:
            for bullet in bullets:
                bullet.x -= self.player_speed
        if keys[pygame.K_w]:
            for bullet in bullets:
                bullet.y += self.player_speed
        if keys[pygame.K_s]:
            for bullet in bullets:
                bullet.y -= self.player_speed
        
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
        
        # Create a bullet surface with transparency
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill(self.color)  # Fill it with the specified color

        # bulletlifetime
        self.last_update = pygame.time.get_ticks()
        self.bullet_lifetime = lifetime

    def kill(self):
        bullets.remove_internal(self)
    
    def render(self, screen, flipped):
        current_time = pygame.time.get_ticks()
        self.x -= int(self.x_vel)
        self.y -= int(self.y_vel)
        
        if current_time - self.last_update >= self.bullet_lifetime:
            self.last_update = current_time
            bullets.remove_internal(self)
        
        # Rotate the bullet image
        if not flipped:
            rotated_image = pygame.transform.rotate(self.image, self.bullet_angle)  # Rotate clockwise
        else:
            rotated_image = pygame.transform.rotate(self.image, -self.bullet_angle)  # Rotate counterclockwise

        # Get the new rect centered at the bullet's position
        rotated_rect = rotated_image.get_rect(center=(self.x, self.y))

        # Draw the rotated bullet
        screen.blit(rotated_image, rotated_rect.topleft)