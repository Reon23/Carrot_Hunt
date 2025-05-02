import pygame
import numpy as np
import random

from enemy import enemy_list, Morph1, Morph2, Mage, Dummy
from collectables import collectable_list, Carrot
from game import SCREEN_WIDTH, SCREEN_HEIGHT

wave_manager = {
    "wave no": 5,
    "wave set": False,
    "wave complete": False,
    1: {
        "enemies" : [0.8, 0.2, 0],
        "max enemies" : 10,
        "spawn rate" : 1800
        },
    2: {
        "enemies" : [0.7, 0.3, 0],
        "max enemies" : 30,
        "spawn rate" : 1000
        },
    3: {
        "enemies" : [0.6, 0.4, 0],
        "max enemies" : 50,
        "spawn rate" : 800
        },
    4: {
        "enemies" : [0.55, 0.35, 0.1],
        "max enemies" : 100,
        "spawn rate" : 600
        },
    5: {
        "enemies" : [0.5, 0.3, 0.2],
        "max enemies" : 200,
        "spawn rate" : 500
        },
}

class EnemySpawner:
    def __init__(self):
        self.choice = ['morph1', 'morph2', 'mage']
        self.probabilities = [0.5, 0.3, 0.2]
        # self.probabilities = [1, 0, 0]
        self.max_spawn = 300
        self.spawn_count = 0

        self.spawn_cooldown = 1000
        self.last_spawn = 0

        self.outside_cooldown = 1000  # Adjustable cooldown in milliseconds
        self.remove_buffer = False
        
        self.buffer1 = Morph1(-10000, 10000, 128, 64, 1)
        self.buffer2 = Morph1(-10000, 10000, 128, 64, 1)
        enemy_list.add_internal(self.buffer1)
        enemy_list.add_internal(self.buffer2)
        enemy_list.add_internal(Dummy())
        enemy_list.add_internal(Dummy())

    def updateSpawner(self):
        if wave_manager['wave no'] <= 5:
            self.probabilities = wave_manager[wave_manager['wave no']]['enemies']
            self.max_spawn = wave_manager[wave_manager['wave no']]['max enemies']
            self.spawn_cooldown = wave_manager[wave_manager['wave no']]['spawn rate']
            self.spawn_count = 0
            wave_manager['wave no'] += 1
            wave_manager['wave set'] = True

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
            elif spawning_enemy == 'morph2':
                enemy_list.add_internal(Morph2(x, y, 128, 128, 3))
            else:
                enemy_list.add_internal(Mage(x, y, 128, 64, 3))

            self.spawn_count += 1
            # print("Ememy ",self.spawn_count, " Type : ", spawning_enemy)
            if not self.remove_buffer:
                enemy_list.remove_internal(self.buffer1)
                enemy_list.remove_internal(self.buffer2)
                self.remove_buffer = True
        else:
            if (len(enemy_list) - 2) == 0:
                wave_manager['wave complete'] = True
                wave_manager['wave set'] = False

    def handle_outside(self, displayScroll):
        scroll_x, scroll_y = displayScroll
        current_time = pygame.time.get_ticks()
        sides = ['left', 'right', 'top', 'bottom']

        for enemy in enemy_list:
            if getattr(enemy, 'hurt', False):
                continue

            # Determine if enemy is outside and which side
            current_side = None
            if enemy.x + enemy.width < scroll_x:
                current_side = 'left'
            elif enemy.x > scroll_x + SCREEN_WIDTH:
                current_side = 'right'
            elif enemy.y + enemy.height * 2 < scroll_y:
                current_side = 'top'
            elif enemy.y > scroll_y + SCREEN_HEIGHT:
                current_side = 'bottom'

            if current_side:
                # Initialize timer attribute name based on side
                timer_attr = f'outside_{current_side}_since'
                since = getattr(enemy, timer_attr, None)
                if since is None:
                    setattr(enemy, timer_attr, current_time)
                elif current_time - since >= self.outside_cooldown:
                    # Choose a new side excluding the current one
                    new_side = random.choice([s for s in sides if s != current_side])
                    # Reposition enemy to the new side
                    if new_side == 'left':
                        enemy.x = random.randint(-200, -50) + scroll_x
                        enemy.y = random.randint(50, SCREEN_HEIGHT) + scroll_y
                    elif new_side == 'right':
                        enemy.x = random.randint(SCREEN_WIDTH + 50, SCREEN_WIDTH + 200) + scroll_x
                        enemy.y = random.randint(50, SCREEN_HEIGHT) + scroll_y
                    elif new_side == 'top':
                        enemy.x = random.randint(50, SCREEN_WIDTH) + scroll_x
                        enemy.y = random.randint(-200, -50) + scroll_y
                    else:  # bottom
                        enemy.x = random.randint(50, SCREEN_WIDTH) + scroll_x
                        enemy.y = random.randint(SCREEN_HEIGHT + 50, SCREEN_HEIGHT + 200) + scroll_y
                    # Reset all outside timers
                    for side in sides:
                        attr = f'outside_{side}_since'
                        setattr(enemy, attr, None)
            else:
                # Reset timers if back on screen
                for side in ['horizontal', 'vertical']:
                    for pos in ['left', 'right'] if side == 'horizontal' else ['top', 'bottom']:
                        attr = f'outside_{pos}_since'
                        setattr(enemy, attr, None)

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
