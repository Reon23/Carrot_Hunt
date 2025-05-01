import pygame
import math
from display import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCREEN
from audio import SFXplayer
from effects import ScreenEffects

pygame.init()
font = pygame.font.Font('./assets/font/VeniceClassic.ttf', 100)
background = pygame.image.load('./assets/bg.png')
title = pygame.image.load('./assets/title.png')
small_font = pygame.font.Font('./assets/font/VeniceClassic.ttf', 24)
clock = pygame.time.Clock()
screen_effect = ScreenEffects()
start_game = False
start_sfx = SFXplayer('./assets/audio/select.ogg')

WHITE = (255, 255, 255)
BACKGROUND_COLOR = (0, 0, 0)



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



def scale_and_center_background(image, screen_w, screen_h, scale_offset=-0.75):
    """
    1) Compute the minimal integer ceil-scale to cover the screen.
    2) Add scale_offset to tune it up or down (but at least 1).
    3) Scale with nearest-neighbor, center, and allow cropping.
    """
    img_w, img_h = image.get_size()

    # 1) ceil-div for each axis

    scale_x = (screen_w + img_w - 1) // img_w
    scale_y = (screen_h + img_h - 1) // img_h
    auto_scale = max(scale_x, scale_y)

    # 2) apply offset, enforce minimum of 1

    scale = max(1, auto_scale + scale_offset)

    # 3) pixel-perfect nearest-neighbor upscale
    if scale != 1:
        scaled = pygame.transform.scale(image, (img_w * scale, img_h * scale))
    else:
        scaled = image

    new_w, new_h = scaled.get_size()
    # center (negative offsets crop off edges)
    x = (screen_w - new_w) // 2
    y = (screen_h - new_h) // 2
    return scaled, (x, y)


def render_wrapped_text(text, font, color, max_width):
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


def show_title_screen():
    SW, SH = DISPLAY_WIDTH, DISPLAY_HEIGHT
    global start_game
    screen = SCREEN

    scaled_bg, bg_pos = scale_and_center_background(
        background, SW, SH
    )

    # Start button positioned above the credits
    start_btn_y = SH * 0.85 - 80
    start_btn = TextButton("Enter to begin", SW // 2, int(start_btn_y))

    credits_text = "Developed by Reon Dsouza & Ruben Saldanha"
    wrapped_credits = render_wrapped_text(credits_text, small_font, WHITE, SW * 0.9)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return -1
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and screen_effect.fade_complete:
                    start_sfx.playSound()
                    start_game = True
                if ev.key == pygame.K_ESCAPE:
                    return -1

        screen.fill(BACKGROUND_COLOR)
        screen.blit(scaled_bg, bg_pos)
        title_w, _ = title.get_size()
        screen.blit(title, ((SW * 0.5) - title_w / 2, SH * 0.1))

        start_btn.draw_pulsating(screen, pygame.time.get_ticks())


        # Draw credits centered at bottom with wrapped lines
        total_height = len(wrapped_credits) * small_font.get_linesize()
        y_start = SH - total_height - 10
        for i, line_surf in enumerate(wrapped_credits):
            line_rect = line_surf.get_rect(center=(SW // 2, y_start + i * small_font.get_linesize()))
            screen.blit(line_surf, line_rect)

        if not screen_effect.fade_complete:
            screen_effect.FadeOut(screen, 5)

        if not screen_effect.fade_in_complete and start_game:
            screen_effect.FadeIn(screen, 5)

        if screen_effect.fade_in_complete:
            return "play"

        pygame.display.flip()
        clock.tick(60)
