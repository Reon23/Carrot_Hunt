import pygame

class Animate:

    #Initalize Animate variables
    def __init__(self, sprite_sheet, x, y, width, height):
        self.sprite_sheet = pygame.image.load(str(sprite_sheet)).convert_alpha()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    # Fetch single frame from sprite sheet
    def getFrame(self, sprite_sheet, width, height):
        # Create empty frame
        frame = pygame.Surface((width, height)).convert_alpha()
        # Paste sprite_sheet onto frame
        frame.blit(sprite_sheet, (0,0), (0, 0, self.width, self.height))
        return frame

    def animate(self, screen, scale):
        frame = self.getFrame(self.sprite_sheet, self.width, self.height)
        frame = pygame.transform.scale(frame, (self.width * scale, self.height * scale))
        screen.blit(frame, (self.x, self.y))