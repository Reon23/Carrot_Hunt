import pygame

class Player:
    
    #Initalize player variables
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def render(self, screen):
        pygame.draw.rect(screen, "blue", (self.x, self.y, self.width, self.height))