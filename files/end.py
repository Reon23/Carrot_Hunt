import pygame
from display import DISPLAY_HEIGHT, DISPLAY_WIDTH, SCREEN
from effects import ScreenEffects

class End:
    def __init__(self):
        # Load and scale image proportionally to match screen height
        self.image = pygame.image.load("./assets/the_end.png").convert_alpha()
        orig_width, orig_height = self.image.get_size()

        scale_factor = DISPLAY_HEIGHT / orig_height
        new_width = int(orig_width * scale_factor)
        new_height = DISPLAY_HEIGHT
        self.effects = ScreenEffects()

        self.image = pygame.transform.smoothscale(self.image, (new_width, new_height))
        self.to_title = False

        # Center the image horizontally
        self.x = (DISPLAY_WIDTH - new_width) // 2
        self.y = 0

    def show(self):
        clock = pygame.time.Clock()
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return -1
                if ev.type == pygame.MOUSEBUTTONDOWN and self.effects.fade_complete:
                    self.to_title = True
                if ev.type == pygame.KEYDOWN and self.effects.fade_complete:
                    self.to_title = True
            
            SCREEN.fill((0, 0, 0))  # Clear screen

            SCREEN.blit(self.image, (self.x, self.y))

            if not self.effects.fade_complete:
                self.effects.FadeOut(SCREEN, 5)

            if self.to_title:
                self.effects.FadeIn(SCREEN, 5)

            if self.to_title and self.effects.fade_in_complete:
                return "title"

            pygame.display.flip()
            clock.tick(60)
