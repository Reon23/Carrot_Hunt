import pygame

from player import Player

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Variables
display_scroll = [0, 0]

# pygame setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

# Game objects
player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, 32, 32)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # poll for keyboard events
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        display_scroll[0] -= 5
    if keys[pygame.K_d]:
        display_scroll[0] += 5
    if keys[pygame.K_w]:
        display_scroll[1] -= 5
    if keys[pygame.K_s]:
        display_scroll[1] += 5


    # fill the screen with a color to wipe away anything from last frame
    screen.fill((184, 66, 78))

    # RENDER YOUR GAME HERE
    pygame.draw.rect(screen, "green", (300-display_scroll[0], 400-display_scroll[1], 16, 16))
    pygame.draw.rect(screen, "green", (600-display_scroll[0], 600-display_scroll[1], 16, 16))
    player.render(screen);
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()