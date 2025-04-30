import pygame
from game import Engine
from display import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCREEN
from title import show_title_screen


state = 'title'

if __name__ == '__main__':
    game_engine = Engine()
    state = 'title'

    # keep going until the user quits
    while state != -1:
        if state == 'title':
            pygame.mouse.set_visible(True)
            state = show_title_screen()     # returns "play" or -1
        elif state == 'play':
            pygame.mouse.set_visible(False)
            game_engine.run()               # this blocks until the game exits
            state = 'title'                 # after game over, go back to title
    pygame.quit()
