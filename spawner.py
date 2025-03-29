import pygame
import numpy as np
import random

from enemy import enemy_list, Morph1, Morph2, Dummy
from collectables import collectable_list, Carrot
from game import SCREEN_WIDTH, SCREEN_HEIGHT

class EnemySpawner:
    def __init__(self):
        self.choice = ['morph1', 'morph2']
        self.probabilities = [0.7, 0.3]
        self.max_spawn = 100
        self.spawn_count = 0

        self.spawn_cooldown = 2000
        self.last_spawn = 0

        self.outside_cooldown = 1000  # Adjustable cooldown in milliseconds
        
        enemy_list.add(Dummy())
        enemy_list.add(Dummy())

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
            # print("Ememy ",self.spawn_count, " Type : ", spawning_enemy)

    def handle_outside(self, displayScroll):
        scroll_x, scroll_y = displayScroll
        current_time = pygame.time.get_ticks()
        
        for enemy in enemy_list:
            # --- Horizontal check ---
            if not getattr(enemy, 'hurt', False):
                if enemy.x + enemy.width < scroll_x:
                    if not hasattr(enemy, 'outside_horizontal_since') or enemy.outside_horizontal_since is None:
                        enemy.outside_horizontal_since = current_time
                    elif current_time - enemy.outside_horizontal_since >= self.outside_cooldown:
                        enemy.x = random.randint(SCREEN_WIDTH + 50, SCREEN_WIDTH + 200) + scroll_x
                        enemy.outside_horizontal_since = None
                elif enemy.x > scroll_x + SCREEN_WIDTH:
                    if not hasattr(enemy, 'outside_horizontal_since') or enemy.outside_horizontal_since is None:
                        enemy.outside_horizontal_since = current_time
                    elif current_time - enemy.outside_horizontal_since >= self.outside_cooldown:
                        enemy.x = random.randint(-200, -50) + scroll_x
                        enemy.outside_horizontal_since = None
                else:
                    enemy.outside_horizontal_since = None  # Reset if enemy is visible

                # --- Vertical check ---
                if enemy.y + enemy.height * 2 < scroll_y:
                    if not hasattr(enemy, 'outside_vertical_since') or enemy.outside_vertical_since is None:
                        enemy.outside_vertical_since = current_time
                    elif current_time - enemy.outside_vertical_since >= self.outside_cooldown:
                        enemy.y = random.randint(SCREEN_HEIGHT + 50, SCREEN_HEIGHT + 200) + scroll_y
                        enemy.outside_vertical_since = None
                elif enemy.y > scroll_y + SCREEN_HEIGHT:
                    if not hasattr(enemy, 'outside_vertical_since') or enemy.outside_vertical_since is None:
                        enemy.outside_vertical_since = current_time
                    elif current_time - enemy.outside_vertical_since >= self.outside_cooldown:
                        enemy.y = random.randint(-200, -50) + scroll_y
                        enemy.outside_vertical_since = None
                else:
                    enemy.outside_vertical_since = None  # Reset if enemy is visible

    def handle_spawn(self, displayScroll):
        current_time = pygame.time.get_ticks()
        self.handle_outside(displayScroll)
        if current_time - self.last_spawn >= self.spawn_cooldown:
            self.last_spawn = current_time
            self.spawn_enemy(displayScroll)

class CollectableSpawner:

    def __init__(self):
        self.max_spawn = 20
        self.spawn_count = 0

        self.spawn_cooldown = 2000
        self.last_spawn = 0

        self.outside_cooldown = 5000  # Adjustable cooldown in milliseconds
        collectable_list.add_internal(Dummy())
        collectable_list.add_internal(Dummy())

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

    def spawn_item(self, displayScroll):
        if self.spawn_count < self.max_spawn:
            x, y = self.get_spawn_position(displayScroll)
            collectable_list.add_internal(Carrot(x, y, 2))

    def handle_outside(self, displayScroll):
        scroll_x, scroll_y = displayScroll
        current_time = pygame.time.get_ticks()
        
        for item in collectable_list:
            # --- Horizontal check ---
            if item.x + item.width < scroll_x:
                if not hasattr(item, 'outside_horizontal_since') or item.outside_horizontal_since is None:
                    item.outside_horizontal_since = current_time
                elif current_time - item.outside_horizontal_since >= self.outside_cooldown:
                    collectable_list.remove_internal(item)
                    item.outside_horizontal_since = None
            elif item.x > scroll_x + SCREEN_WIDTH:
                if not hasattr(item, 'outside_horizontal_since') or item.outside_horizontal_since is None:
                    item.outside_horizontal_since = current_time
                elif current_time - item.outside_horizontal_since >= self.outside_cooldown:
                    collectable_list.remove_internal(item)
                    item.outside_horizontal_since = None
            else:
                item.outside_horizontal_since = None  # Reset if enemy is visible

            # --- Vertical check ---
            if item.y + item.height * 2 < scroll_y:
                if not hasattr(item, 'outside_vertical_since') or item.outside_vertical_since is None:
                    item.outside_vertical_since = current_time
                elif current_time - item.outside_vertical_since >= self.outside_cooldown:
                    collectable_list.remove_internal(item)
                    item.outside_vertical_since = None
            elif item.y > scroll_y + SCREEN_HEIGHT:
                if not hasattr(item, 'outside_vertical_since') or item.outside_vertical_since is None:
                    item.outside_vertical_since = current_time
                elif current_time - item.outside_vertical_since >= self.outside_cooldown:
                    collectable_list.remove_internal(item)
                    item.outside_vertical_since = None
            else:
                item.outside_vertical_since = None  # Reset if enemy is visible

    def handle_spawn(self, displayScroll):
        self.spawn_count = len(collectable_list)
        current_time = pygame.time.get_ticks()
        self.handle_outside(displayScroll)
        if current_time - self.last_spawn >= self.spawn_cooldown:
            self.last_spawn = current_time
            self.spawn_item(displayScroll)
