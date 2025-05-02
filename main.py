import pygame
from game import Engine
from enemy import reset_enemy
from weapons import reset_bullets
from collectables import reset_carrots
from display import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCREEN
from title import Title


state = 'title'

if __name__ == '__main__':
    state = 'title'

    while state != -1:
        if state == 'title':
            title = Title()
            state = title.show()
        elif state == 'play':
            reset_enemy()
            reset_bullets()
            reset_carrots()
            game_engine = Engine()
            state = game_engine.run()
    pygame.quit()
