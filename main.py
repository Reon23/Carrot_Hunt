import pygame
from game import Engine
from display import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCREEN
from title import show_title_screen


state = 'title'

if __name__ == '__main__':
    game_engine = Engine()
    state = 'title'

    while state != -1:
        if state == 'title':
            state = show_title_screen()
        elif state == 'play':
            game_engine.run()
            state = 'title'
    pygame.quit()
