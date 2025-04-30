import pygame

pygame.init()
info = pygame.display.Info()
DISPLAY_WIDTH, DISPLAY_HEIGHT = info.current_w, info.current_h
SCREEN = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
