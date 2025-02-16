import pygame
import random
from player import Player
from enemy import Morph1

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Cursed Carrots')
clock = pygame.time.Clock()

class Engine:

    # initialize variables
    def __init__(self):
        self.running = True
        self.display_scroll = [0, 0]
        self.enemy_list = []
        self.player_speed = 8
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 32, 32, self.player_speed)
        self.spawnEnemy()
        self.spawnEnemy()

    def spawnEnemy(self):
        self.enemy_list.append(Morph1(random.randrange(-SCREEN_WIDTH, SCREEN_WIDTH), random.randrange(-SCREEN_HEIGHT, SCREEN_HEIGHT), 128, 64, 3)) 

    def run(self):
        while self.running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False  # Use instance variable

            # Handle keyboard events
            keys = pygame.key.get_pressed()

            if keys[pygame.K_a]:
                self.display_scroll[0] -= self.player_speed
            if keys[pygame.K_d]:
                self.display_scroll[0] += self.player_speed
            if keys[pygame.K_w]:
                self.display_scroll[1] -= self.player_speed
            if keys[pygame.K_s]:
                self.display_scroll[1] += self.player_speed
            

            # Render screen
            screen.fill("green")

            for enemy in self.enemy_list:
                enemy.updatePosition(self.display_scroll)
                enemy.moveToPlayer(self.player.x - 64, self.player.y - 64, self.display_scroll)
                enemy.render(screen)
            
            self.player.render(screen, keys)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
