import pygame
from display import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCREEN
from effects import ScreenEffects
from audio import SFXplayer

details = {"score": 0}

class Death:
    def __init__(self):
        self.screen = SCREEN
        self.font_large = pygame.font.Font('./assets/font/VeniceClassic.ttf', 110)
        self.font = pygame.font.Font('./assets/font/VeniceClassic.ttf', 50)
        self.image = pygame.image.load("./assets/its_dead.png")
        self.image = pygame.transform.scale(self.image, (500, 500))
        self.screen_effect = ScreenEffects()
        self.death_sfx = SFXplayer("./assets/audio/not_good.ogg", 0.5)
        self.sfx_played = False

        self.options = [
            {"text": "Try Again", "return": "play", "rect": None},
            {"text": "Quit :(", "return": -1, "rect": None}
        ]

    def show(self):
        clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))  # Black background

            screen_width, screen_height = DISPLAY_WIDTH, DISPLAY_HEIGHT

            # Draw image centered
            image_rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2 - 100))
            self.screen.blit(self.image, image_rect)

            # Render "You Died" caption and center it
            caption_surface = self.font_large.render("You Died", True, "white")
            caption_rect = caption_surface.get_rect(center=(screen_width // 2, int(screen_height * 0.15)))
            self.screen.blit(caption_surface, caption_rect)

            # Render score text and center it
            score_surface = self.font.render(f'Score : {details["score"]}', True, "Yellow")
            score_rect = score_surface.get_rect(center=(screen_width // 2, int(screen_height * 0.8)))
            self.screen.blit(score_surface, score_rect)

            # Prepare and render buttons
            total_width = 0
            rendered_options = []
            for option in self.options:
                text_surface = self.font.render(option["text"], True, (255, 255, 255))
                rendered_options.append(text_surface)
                total_width += text_surface.get_width() + 40

            start_x = (screen_width - total_width + 40) // 2
            y = image_rect.bottom + 20
            mouse_pos = pygame.mouse.get_pos()

            for i, option in enumerate(self.options):
                text_surface = rendered_options[i]
                rect = text_surface.get_rect(topleft=(start_x, y))
                option["rect"] = rect

                # Hover effect
                if rect.collidepoint(mouse_pos):
                    text_surface = self.font.render(option["text"], True, (150, 150, 150))  # Gray on hover

                self.screen.blit(text_surface, rect)
                start_x += text_surface.get_width() + 40

            # Apply fade effect if not done
            if not self.screen_effect.fade_complete:
                self.screen_effect.FadeOut(self.screen, 5)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for option in self.options:
                        if option["rect"].collidepoint(event.pos):
                            return option["return"]  # Return distinct value
            
            if not self.sfx_played:
                self.death_sfx.playSound()
                self.sfx_played = True

            clock.tick(60)
