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
        self.health = value  # Prevents health from going negative

    def render(self, screen):
        current_width = max(0, (self.width * (self.health / self.max_health)))  # Smooth scaling
        pygame.draw.rect(screen, self.color, (30, 30, current_width, self.height))

class ScoreBar:
    def __init__(self):
        self.score = 0
        pygame.font.init()
        self.font = pygame.font.Font(None, 30)

    def addScore(self, value):
        self.score += value

    def render(self, screen):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH//1.1 - (len(str(self.score)) * 10), 20))

