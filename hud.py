import pygame
from game import SCREEN_WIDTH, SCREEN_HEIGHT, font
from spawner import wave_manager


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
        self.font = font

    def addScore(self, value):
        self.score += value

    def render(self, screen):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, ((int(SCREEN_WIDTH * 0.025)), int(SCREEN_HEIGHT * 0.05)))

class WaveBar:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.Font('./assets/font/VeniceClassic.ttf', 50)  # Default pygame font
        self.wave = None

    def render(self, screen):
        self.wave = (wave_manager['wave no'] - 1)
        wave_text = self.font.render(f'Wave {self.wave}', True, (255, 255, 255))
        screen.blit(wave_text, ((int(SCREEN_WIDTH * 0.48)), int(SCREEN_HEIGHT * 0.065)))

class CrossHair:
    def __init__(self):
        self.sprite = pygame.image.load('./assets/ui/crosshair/crosshair.png')

    def render(self, screen, mouse_x, mouse_y):
        screen.blit(self.sprite, (mouse_x - 16, mouse_y - 16))