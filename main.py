import pygame

from player import Player, PlayerBullet

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Variables
display_scroll = [0, 0]
player_bullets = []

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

# Game objects
player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 32, 32)

while running:
    # poll for events
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # poll for mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player_bullets.append(PlayerBullet(player.x, player.y, mouse_x, mouse_y))
    # poll for keyboard events
    keys = pygame.key.get_pressed()

    

    if keys[pygame.K_a]:
        display_scroll[0] -= 5
        for bullet in player_bullets:
            bullet.x += 5
    if keys[pygame.K_d]:
        display_scroll[0] += 5
        for bullet in player_bullets:
            bullet.x -= 5
    if keys[pygame.K_w]:
        display_scroll[1] -= 5
        for bullet in player_bullets:
            bullet.y += 5
    if keys[pygame.K_s]:
        display_scroll[1] += 5
        for bullet in player_bullets:
            bullet.y -= 5


    # fill the screen with a color to wipe away anything from last frame
    screen.fill("green")

    # RENDER YOUR GAME HERE
    pygame.draw.rect(screen, "red", (300-display_scroll[0], 400-display_scroll[1], 16, 16))
    pygame.draw.rect(screen, "red", (600-display_scroll[0], 600-display_scroll[1], 16, 16))
    player.render(screen);

    for bullet in player_bullets:
        bullet.render(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()