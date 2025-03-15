import pygame

class Animate:
    sprite_cache = {}  # Dictionary to store loaded sprite sheets

    def __init__(self, sprite_sheet_path, x, y, width, height, frames, frame_row, scale, speed):
        if sprite_sheet_path not in Animate.sprite_cache:
            Animate.sprite_cache[sprite_sheet_path] = pygame.image.load(str(sprite_sheet_path)).convert_alpha()
        
        self.sprite_sheet = Animate.sprite_cache[sprite_sheet_path]  # Use cached image
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scale = scale
        self.frames = frames
        self.frame = 0
        self.animation_list = []           # Original frames
        self.flipped_animation_list = []   # Precomputed flipped frames
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = speed

        for i in range(self.frames):
            # Get the original frame
            frame = self.getFrame(self.sprite_sheet, i, frame_row, self.width, self.height, self.scale)
            self.animation_list.append(frame)
            # Precompute and cache the flipped frame
            self.flipped_animation_list.append(pygame.transform.flip(frame, True, False))

    # Fetch a single frame from the sprite sheet
    def getFrame(self, sprite_sheet, xframe_no, yframe_no, width, height, scale):
        frame = sprite_sheet.subsurface(pygame.Rect(
            xframe_no * width, yframe_no * height, width, height
        ))
        return pygame.transform.scale(frame, (width * scale, height * scale))

    def animate_old(self, screen, render_x, render_y, flipped=False):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update >= self.animation_cooldown:
            self.last_update = current_time  # Reset last update time
            self.frame = (self.frame + 1) % self.frames  # Cycle frames

        # Use precomputed images based on the flipped flag
        if flipped:
            image = self.flipped_animation_list[self.frame]
        else:
            image = self.animation_list[self.frame]
        
        screen.blit(image, (render_x, render_y))


    def animate(self, screen, play, render_x, render_y, angle, flipped):
        current_time = pygame.time.get_ticks()

        if play:
            if current_time - self.last_update >= self.animation_cooldown:
                self.last_update = current_time
                self.frame = (self.frame + 1) % self.frames  # Loop animation frames

        original_image = self.animation_list[self.frame]
        rotated_image = pygame.transform.rotate(original_image, angle)
        
        # Store original size before flipping
        original_width = rotated_image.get_width()

        # Flip the image if needed
        if flipped:
            rotated_image = pygame.transform.flip(rotated_image, True, False)

        # Compute the offset difference after flipping
        flipped_width = rotated_image.get_width()
        offset_x = (flipped_width - original_width) if flipped else 0

        # Maintain correct positioning
        new_rect = rotated_image.get_rect(center=(render_x - offset_x, render_y))

        screen.blit(rotated_image, new_rect.topleft)

