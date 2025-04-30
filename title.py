import pygame
from display import DISPLAY_WIDTH, DISPLAY_HEIGHT, SCREEN

pygame.init()
font = pygame.font.Font('./assets/font/VeniceClassic.ttf', 50)
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
BACKGROUND_COLOR = (30, 30, 30)


class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.hover_color = DARK_GRAY
        self.text_surf = font.render(text, True, WHITE)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, self.hover_color if is_hovered else self.color, self.rect, border_radius=10)
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

def show_title_screen():
    SCREEN_WIDTH, SCREEN_HEIGHT = DISPLAY_WIDTH, DISPLAY_HEIGHT
    screen = SCREEN

    play_button = Button("Play", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 60, 200, 60)
    quit_button = Button("Quit", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20, 200, 60)

    while True:
        screen.fill(BACKGROUND_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
            elif play_button.is_clicked(event):
                return "play"
            elif quit_button.is_clicked(event):
                return -1

        play_button.draw(screen)
        quit_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)
