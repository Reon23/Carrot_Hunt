import pygame
from game import SCREEN_WIDTH

class healthBar:

    def __init__(self, health):
        self.max_health = health
        self.health = health
        self.color = "red"
        self.height = 20
        self.width = SCREEN_WIDTH // 3
    
    def updateHealth(self, value):
        self.health = max(0, self.health - value)  # Prevents health from going negative

    def render(self, screen):
        current_width = max(0, (self.width * (self.health / self.max_health)))  # Smooth scaling
        pygame.draw.rect(screen, self.color, (30, 30, current_width, self.height))
