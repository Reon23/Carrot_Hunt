import pygame

class Animate:

    #Initalize Animate variables
    def __init__(self, sprite_sheet, x, y, width, height, frames, frame_row, scale, speed):
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
        self.animation_cooldown = speed
        self.last_angle = 0
        for i in range(self.frames):
            self.animation_list.append(self.getFrame(self.sprite_sheet, i, frame_row, self.width, self.height, self.scale))

    # Fetch single frame from sprite sheet
    def getFrame(self, sprite_sheet, xframe_no, yframe_no, width, height, scale):
        # Create empty frame
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        # Paste sprite_sheet onto frame
        frame.blit(sprite_sheet, (0,0), (int(xframe_no * self.width), int(yframe_no * self.height), self.width, self.height))
        frame = pygame.transform.scale(frame, (self.width * scale, self.height * scale))
        return frame

    def animate(self, screen, play, render_x, render_y, angle, flipped):
        current_time = pygame.time.get_ticks()

        if play:
            if current_time - self.last_update >= self.animation_cooldown:
                self.last_update = current_time
                self.frame = (self.frame + 1) % self.frames  # Loop animation frames

        rotated_image = pygame.transform.rotate(self.animation_list[self.frame], angle)

        # Flip the image if needed
        if flipped:
            rotated_image = pygame.transform.flip(rotated_image, True, False)
        new_rect = rotated_image.get_rect(center=(render_x, render_y))  # Keep correct positioning

        screen.blit(rotated_image, new_rect.topleft)
