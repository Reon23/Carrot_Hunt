import pygame

class Animate:

    #Initalize Animate variables
    def __init__(self, sprite_sheet, x, y, width, height, frames, scale):
        self.sprite_sheet = pygame.image.load(str(sprite_sheet)).convert_alpha()
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scale = scale
        
        self.frames = frames
        self.frame = 0
        self.animation_list = []
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 50
        for i in range(self.frames):
            self.animation_list.append(self.getFrame(self.sprite_sheet, i, self.width, self.height, self.scale))

    # Fetch single frame from sprite sheet
    def getFrame(self, sprite_sheet, frame_no, width, height, scale):
        # Create empty frame
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        # Paste sprite_sheet onto frame
        frame.blit(sprite_sheet, (0,0), (int(frame_no * self.width), 0, self.width, self.height))
        frame = pygame.transform.scale(frame, (self.width * scale, self.height * scale))
        return frame

    def animate(self, screen, play):
        current_time = pygame.time.get_ticks() 

        if play:
            if current_time - self.last_update >= self.animation_cooldown:
                self.last_update = current_time
                self.frame += 1

                if self.frame >= self.frames:
                    self.frame = 0
            
            screen.blit(self.animation_list[self.frame], (self.x, self.y))
        else:
            screen.blit(self.animation_list[0], (self.x, self.y))