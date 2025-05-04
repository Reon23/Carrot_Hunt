import pygame
from display import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCREEN

#Initialize Pygame
pygame.init()

# Constants
# SCREEN_WIDTH = 1280
# SCREEN_HEIGHT = 720
# SCREEN_WIDTH = 1920
# SCREEN_HEIGHT = 1080
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = DISPLAY_WIDTH, DISPLAY_HEIGHT

# Culling margin (prevents pop-in)
CULLING_MARGIN = 500 
# Delta Time
time = {'delta' : 1}

# pygame setup
screen = SCREEN 

# Font setup
pygame.font.init()
font = pygame.font.Font('./assets/font/VeniceClassic.ttf', 30)  # Default pygame font

from player import Player
from hud import CrossHair, WaveBar
from enemy import enemy_list, enemy_bullets
from weapons import bullets
from spawner import EnemySpawner, CollectableSpawner, wave_manager
from collectables import collectable_list
from effects import ScreenEffects
from audio import MusicPlayer

class Engine:

    # Initialize variables

    def __init__(self):
        self.running = True
        self.clock = pygame.time.Clock()
        self.display_scroll = [0, 0]
        self.player_speed = 10
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 32, 32, self.player_speed)
        self.screen_effect = ScreenEffects()
        self.player_crosshair = CrossHair()
        self.enemy_spawner = EnemySpawner()
        self.collectable_spawner = CollectableSpawner()
        self.wave_bar = WaveBar()
        self.music = MusicPlayer()
        self.music_playing = False
        self.waiting = True
        self.wait_cooldown = 8000 + pygame.time.get_ticks()
        self.last_update = 0
        self.fullscreen = True
        self.show_frames = False
        self.entities = []
        self.fading = False
        pygame.mouse.set_visible(False)

    def render_fps(self):
        """Displays the FPS counter on the screen."""
        fps_text = font.render(f"{int(self.clock.get_fps())}", True, (255, 255, 255))
        screen.blit(fps_text, ((SCREEN_WIDTH * 0.025), int(SCREEN_HEIGHT * 0.95)))  # Draw FPS in the top-left corner

    def run(self):
        global state
        while self.running:
            current_time = pygame.time.get_ticks()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return -1
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return "title"

            # Handle keyboard events
            movement = pygame.math.Vector2(0, 0)
            keys = pygame.key.get_pressed()

            if keys[pygame.K_a]:
                movement.x -= 1
            if keys[pygame.K_d]:
                movement.x += 1
            if keys[pygame.K_w]:
                movement.y -= 1
            if keys[pygame.K_s]:
                movement.y += 1

            # Normalize the movement vector to prevent faster diagonal movement
            if movement.length_squared() > 0:
                movement = movement.normalize()

            # Apply movement
            self.display_scroll[0] += movement.x * self.player_speed * time['delta'] * 60
            self.display_scroll[1] += movement.y * self.player_speed * time['delta'] * 60

            # Render screen
            screen.fill((133, 51, 19))

            # **Optimize Enemy Rendering with Culling Offset**
            screen_rect = pygame.Rect(
                self.display_scroll[0] - CULLING_MARGIN, 
                self.display_scroll[1] - CULLING_MARGIN, 
                SCREEN_WIDTH + (CULLING_MARGIN * 2), 
                SCREEN_HEIGHT + (CULLING_MARGIN * 2)
            )

            if not wave_manager['wave set']:
                self.enemy_spawner.updateSpawner()
            
            if not self.waiting:
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
                    bullet.handleBullets(bullets, self.player, screen)
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
            if self.show_frames:
                self.render_fps()
            self.player_crosshair.render(screen, mouse_x, mouse_y)

            if current_time - self.last_update >= self.wait_cooldown:
                self.waiting = False

            if not self.waiting:
                self.wave_bar.render(screen)

            if not self.waiting and not self.music_playing:
                self.music.play()
                self.music_playing = True

            if self.music_playing:
                self.music.update()

            if not self.screen_effect.fade_complete:
                self.screen_effect.FadeOut(screen)
            
            if self.enemy_spawner.waves_complete:
                self.music.stop()
                self.screen_effect.FadeIn(screen, 1)
            pygame.display.flip()
            
            # Calculate Delta Time & Set Frame Rate
            time['delta'] = self.clock.tick(120) / 1000.0

            if self.player.player_health.health <= 0:
                self.running = False
                self.enemy_spawner.resetSpawner()
                self.player.player_score.saveScore()
                self.music.stop()
                return 'death'


            if self.screen_effect.fade_in_complete:
                self.enemy_spawner.resetSpawner()
                return 'end'

