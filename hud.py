import pygame
from game import SCREEN_WIDTH, SCREEN_HEIGHT

class healthBar:

    def __init__(self, health):
        self.x = int(SCREEN_WIDTH * 0.025)
        self.y = int(SCREEN_HEIGHT * 0.025)
        self.max_health = health
        self.health = health
        self.color = "red"
        self.height = 20
        self.width = int(SCREEN_WIDTH * 0.35)
    
    def updateHealth(self, value):
        self.health = value  # Prevents health from going negative

    def render(self, screen):
        current_width = max(0, (self.width * (self.health / self.max_health)))  # Smooth scaling
        pygame.draw.rect(screen, self.color, (self.x, self.y, current_width, self.height))

class ScoreBar:
    def __init__(self):
        self.score = 0
        pygame.font.init()
        self.font = pygame.font.Font(None, 30)

    def addScore(self, value):
        self.score += value

    def render(self, screen):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH//1.1 - (len(str(self.score)) * 10), int(SCREEN_HEIGHT * 0.025)))

class CrossHair:
    def __init__(self):
        self.sprite = pygame.image.load('./assets/ui/crosshair/crosshair.png')

    def render(self, screen, mouse_x, mouse_y):
        screen.blit(self.sprite, (mouse_x - 16, mouse_y - 16))