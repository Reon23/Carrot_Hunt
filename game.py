import pygame

# Constants
# SCREEN_WIDTH = 1280
# SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
# Culling margin (prevents pop-in)
CULLING_MARGIN = 500 
# Delta Time
time = {'delta' : 1}

from player import Player
from hud import CrossHair
from enemy import enemy_list, enemy_bullets
from weapons import bullets
from spawner import EnemySpawner, CollectableSpawner
from collectables import collectable_list


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
        self.player_speed = 10
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 32, 32, self.player_speed)
        self.player_crosshair = CrossHair()
        self.enemy_spawner = EnemySpawner()
        self.collectable_spawner = CollectableSpawner()
        self.fullscreen = False
        self.entities = []
        # Hides the mouse
        pygame.mouse.set_visible(False)

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
                self.display_scroll[0] -= self.player_speed * time['delta'] * 60
            if keys[pygame.K_d]:
                self.display_scroll[0] += self.player_speed * time['delta'] * 60
            if keys[pygame.K_w]:
                self.display_scroll[1] -= self.player_speed * time['delta'] * 60
            if keys[pygame.K_s]:
                self.display_scroll[1] += self.player_speed * time['delta'] * 60

            # Render screen
            screen.fill((133, 51, 19))

            # **Optimize Enemy Rendering with Culling Offset**
            screen_rect = pygame.Rect(
                self.display_scroll[0] - CULLING_MARGIN, 
                self.display_scroll[1] - CULLING_MARGIN, 
                SCREEN_WIDTH + (CULLING_MARGIN * 2), 
                SCREEN_HEIGHT + (CULLING_MARGIN * 2)
            )

            
            self.enemy_spawner.handle_spawn(self.display_scroll)
            self.collectable_spawner.handle_spawn(self.display_scroll)

            # Clear entities list to prevent duplicates
            self.entities.clear()

            for enemy in enemy_list:
                enemy.updatePosition(self.display_scroll, self.player, screen)
                enemy.handleCollision(bullets, self.player)
                # **Only render enemies near or inside the screen view**
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if screen_rect.colliderect(enemy_rect):
                    self.entities.append(enemy)

            for bullet in enemy_bullets:
                bullet.updatePosition(self.display_scroll, self.player)
                bullet.handleCollision(self.player, screen)
                if bullet.__class__.__name__ == "MageBlob":
                    bullet.handleBullets(bullets, screen)
                bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
                if screen_rect.colliderect(bullet_rect):
                    if bullet.__class__.__name__ == 'MageCast':
                        bullet.render(screen)
                    else:
                        self.entities.append(bullet)


            for item in collectable_list:
                item.updatePosition(self.display_scroll)
                item.handleCollision(self.player)

                # Render items within screen
                item_rect = pygame.Rect(item.x, item.y, item.width, item.height)
                if screen_rect.colliderect(item_rect):
                    item.render(screen)
            
            self.entities.append(self.player)


            # print([(sprite.y - self.display_scroll[1] + 100 + getattr(sprite, 'height', 64)) if sprite != self.player else (sprite.y + getattr(sprite, 'height', 32)) for sprite in self.entities])
            # **Sort by the bottom Y position to fix rendering order**
            self.entities.sort(key=lambda entity: (entity.y - self.display_scroll[1] + 100 + getattr(entity, 'height', 64))
                                if entity != self.player else (entity.y + getattr(entity, 'height', 64)))

            for entity in self.entities:
                if entity == self.player:
                    entity.render(screen, keys)
                else:
                    entity.render(screen)


            # self.player.render(screen, keys)


            # Render FPS counter
            self.render_fps()
            self.player_crosshair.render(screen, mouse_x, mouse_y)

            pygame.display.flip()
            
            # Calculate Delta Time & Set Frame Rate
            time['delta'] = clock.tick(120) / 1000.0

        pygame.quit()

