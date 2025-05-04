import pygame
from game import Engine
from enemy import reset_enemy
from weapons import reset_bullets
from collectables import reset_carrots
from title import Title
from death import Death
from end import End


if __name__ == '__main__':
    state = 'title'

    while state != -1:
        if state == 'title':
            pygame.mouse.set_visible(True)
            title = Title()
            state = title.show()
        elif state == 'play':
            reset_enemy()
            reset_bullets()
            reset_carrots()
            game_engine = Engine()
            state = game_engine.run()
        elif state == 'death':
            pygame.mouse.set_visible(True)
            death = Death()
            state = death.show()
        elif state == 'end':
            end = End()
            state = end.show()
    pygame.quit()
