import pygame
from player import Player, PlayerBullet

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
        self.player_bullets = []
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 32, 32)
        self.player_speed = 8

    def run(self):
        while self.running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False  # Use instance variable

                # Handle mouse events
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player_bullets.append(PlayerBullet(self.player.x, self.player.y, mouse_x, mouse_y))

            # Handle keyboard events
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.display_scroll[0] -= self.player_speed
                for bullet in self.player_bullets:
                    bullet.x += self.player_speed
            if keys[pygame.K_d]:
                self.display_scroll[0] += self.player_speed
                for bullet in self.player_bullets:
                    bullet.x -= self.player_speed
            if keys[pygame.K_w]:
                self.display_scroll[1] -= self.player_speed
                for bullet in self.player_bullets:
                    bullet.y += self.player_speed
            if keys[pygame.K_s]:
                self.display_scroll[1] += self.player_speed
                for bullet in self.player_bullets:
                    bullet.y -= self.player_speed

            # Render screen
            screen.fill("green")
            pygame.draw.rect(screen, "red", (300 - self.display_scroll[0], 400 - self.display_scroll[1], 16, 16))
            pygame.draw.rect(screen, "red", (600 - self.display_scroll[0], 600 - self.display_scroll[1], 16, 16))

            self.player.render(screen, keys)

            for bullet in self.player_bullets:
                bullet.render(screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
