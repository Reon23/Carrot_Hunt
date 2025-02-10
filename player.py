import pygame
import math

class Player:
    
    #Initalize player variables
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def render(self, screen):
        pygame.draw.rect(screen, "blue", (self.x, self.y, self.width, self.height))

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