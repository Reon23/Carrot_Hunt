import pygame

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
# SCREEN_WIDTH = 1920
# SCREEN_HEIGHT = 1080
# Culling margin (prevents pop-in)
CULLING_MARGIN = 500 

from player import Player
from enemy import enemy_list
from weapons import bullets
from spawner import Spawner


# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Cursed Carrots')
clock = pygame.time.Clock()

# Font setup for FPS display
pygame.font.init()
font = pygame.font.Font(None, 30)  # Default pygame font

class Engine:

    # Initialize variables

    def __init__(self):
        self.running = True
        self.display_scroll = [0, 0]
        self.player_speed = 8
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 32, 32, self.player_speed)
        self.enemy_spawner = Spawner()
        self.fullscreen = False

    def toggle_fullscreen(self):
        """Toggles fullscreen mode when F11 is pressed."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def render_fps(self):
        """Displays the FPS counter on the screen."""
        fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))  # Draw FPS in the top-left corner

    def run(self):
        while self.running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()

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

            # **Optimize Enemy Rendering with Culling Offset**
            screen_rect = pygame.Rect(
                self.display_scroll[0] - CULLING_MARGIN, 
                self.display_scroll[1] - CULLING_MARGIN, 
                SCREEN_WIDTH + (CULLING_MARGIN * 2), 
                SCREEN_HEIGHT + (CULLING_MARGIN * 2)
            )

            
            self.enemy_spawner.handle_spawn(self.display_scroll)

            for enemy in enemy_list:
                enemy.updatePosition(self.display_scroll, self.player, screen)
                enemy.handleCollision(bullets)

                # **Only render enemies near or inside the screen view**
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if screen_rect.colliderect(enemy_rect):
                    enemy.render(screen)

            self.player.render(screen, keys)

            # Render FPS counter
            self.render_fps()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
