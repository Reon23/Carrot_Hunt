import pygame
import math
from display import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCREEN
from audio import SFXplayer
from effects import ScreenEffects

pygame.init()

WHITE = (255, 255, 255)
BACKGROUND_COLOR = (0, 0, 0)
font = pygame.font.Font('./assets/font/VeniceClassic.ttf', 100)

class TextButton:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def draw_pulsating(self, screen, time_ms):
        # Time in seconds
        t = time_ms / 2000.0
        # Pulsate between 180 and 255
        brightness = 180 + int(75 * (0.5 + 0.5 * math.sin(2 * math.pi * t)))
        pulsating_color = (brightness, brightness, brightness)
        text_surf = font.render(self.text, True, pulsating_color)
        rect = text_surf.get_rect(center=(self.x, self.y))
        screen.blit(text_surf, rect)
        self.rect = rect  # Update rect for is_hovered()

    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())


class Title:
    def __init__(self):
        self.background = pygame.image.load('./assets/bg.png')
        self.title = pygame.image.load('./assets/title.png')
        self.small_font = pygame.font.Font('./assets/font/VeniceClassic.ttf', 24)
        self.clock = pygame.time.Clock()
        self.screen_effect = ScreenEffects()
        self.start_game = False
        self.start_sfx = SFXplayer('./assets/audio/select.ogg')

    def scale_and_center_background(self, image, screen_w, screen_h, scale_offset=-0.75):
        img_w, img_h = image.get_size()
        scale_x = (screen_w + img_w - 1) // img_w
        scale_y = (screen_h + img_h - 1) // img_h
        auto_scale = max(scale_x, scale_y)
        scale = max(1, auto_scale + scale_offset)
        if scale != 1:
            scaled = pygame.transform.scale(image, (img_w * scale, img_h * scale))
        else:
            scaled = image
        new_w, new_h = scaled.get_size()
        x = (screen_w - new_w) // 2
        y = (screen_h - new_h) // 2
        return scaled, (x, y)

    def render_wrapped_text(self, text, font, color, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return [font.render(line, True, color) for line in lines]

    def show(self):
        SW, SH = DISPLAY_WIDTH, DISPLAY_HEIGHT
        screen = SCREEN

        # Reset effects and start state
        self.screen_effect.fade_complete = False
        self.screen_effect.fade_in_complete = False
        self.start_game = False

        scaled_bg, bg_pos = self.scale_and_center_background(self.background, SW, SH)
        start_btn_y = SH * 0.85 - 80
        start_btn = TextButton("Enter to begin", SW // 2, int(start_btn_y))

        credits_text = "Developed by Reon Dsouza & Ruben Saldanha"
        wrapped_credits = self.render_wrapped_text(credits_text, self.small_font, WHITE, SW * 0.9)

        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return -1
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN and self.screen_effect.fade_complete:
                        self.start_sfx.playSound()
                        self.start_game = True
                    if ev.key == pygame.K_ESCAPE:
                        return -1

            screen.fill(BACKGROUND_COLOR)
            screen.blit(scaled_bg, bg_pos)
            title_w, _ = self.title.get_size()
            screen.blit(self.title, ((SW * 0.5) - title_w / 2, SH * 0.1))

            start_btn.draw_pulsating(screen, pygame.time.get_ticks())

            total_height = len(wrapped_credits) * self.small_font.get_linesize()
            y_start = SH - total_height - 10
            for i, line_surf in enumerate(wrapped_credits):
                line_rect = line_surf.get_rect(center=(SW // 2, y_start + i * self.small_font.get_linesize()))
                screen.blit(line_surf, line_rect)

            if not self.screen_effect.fade_complete:
                self.screen_effect.FadeOut(screen, 5)

            if not self.screen_effect.fade_in_complete and self.start_game:
                self.screen_effect.FadeIn(screen, 5)

            if self.screen_effect.fade_in_complete:
                self.start_game = False
                return "play"

            pygame.display.flip()
            self.clock.tick(60)
