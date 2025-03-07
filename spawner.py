import pygame
import numpy as np
import random

from enemy import enemy_list, Morph1, Morph2
from game import SCREEN_WIDTH, SCREEN_HEIGHT

class Spawner:
    def __init__(self):
        self.choice = ['morph1', 'morph2']
        self.probabilities = [0.7, 0.3]
        self.max_spawn = 20
        self.spawn_count = 0

        self.spawn_cooldown = 1000
        self.last_spawn = 0
        enemy_list.add_internal(Morph1(-10000, 10000, 128, 64, 0))
        enemy_list.add_internal(Morph2(-10000, 10000, 128, 64, 0))

    def get_spawn_position(self, displayScroll):
        """Returns a random position outside the screen boundaries, adjusted for scrolling."""
        scroll_x, scroll_y = displayScroll  # Unpack scrolling offset
        side = random.choice(['left', 'right', 'top', 'bottom'])

        if side == 'left':
            return random.randint(-200, -50) + scroll_x, random.randint(50, SCREEN_HEIGHT) + scroll_y
        elif side == 'right':
            return random.randint(SCREEN_WIDTH + 50, SCREEN_WIDTH + 200) + scroll_x, random.randint(50, SCREEN_HEIGHT) + scroll_y
        elif side == 'top':
            return random.randint(50, SCREEN_WIDTH) + scroll_x, random.randint(-200, -50) + scroll_y
        else:  # 'bottom'
            return random.randint(50, SCREEN_WIDTH) + scroll_x, random.randint(SCREEN_HEIGHT + 50, SCREEN_HEIGHT + 200) + scroll_y

    def spawn_enemy(self, displayScroll):
        if self.spawn_count < self.max_spawn:
            spawning_enemy = np.random.choice(self.choice, p=self.probabilities)
            x, y = self.get_spawn_position(displayScroll)

            if spawning_enemy == 'morph1':
                enemy_list.add_internal(Morph1(x, y, 128, 64, 3))
            else:
                enemy_list.add_internal(Morph2(x, y, 128, 128, 3))

            self.spawn_count += 1
            print("Ememy ",self.spawn_count, " Type : ", spawning_enemy)

    def handle_spawn(self, displayScroll):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn >= self.spawn_cooldown:
            self.last_spawn = current_time
            self.spawn_enemy(displayScroll)
