import pygame
pygame.mixer.init

class SFXplayer:
    def __init__(self, audio, volume = 0.7):
        self.audio = pygame.mixer.Sound(audio)
        self.audio.set_volume(volume)

    def stopSound(self):
        self.audio.stop()

    def playSound(self):
        self.audio.play()

class MusicPlayer:
    def __init__(self, fade_duration=1000):
        """
        Initialize the track list.
        """
        # Define the internal track list here (file path, volume)
        tracks = [
            ("./assets/audio/track1.ogg", 0.25),
            ("./assets/audio/track2.ogg", 0.25),
        ]

        self.tracks = {
            i + 1: {"track": filepath, "volume": volume}
            for i, (filepath, volume) in enumerate(tracks)
        }
        self.track_keys = list(self.tracks.keys())
        self.current_index = 0
        self.fade_duration = fade_duration
        self.is_playing = False
        self.next_ready = True

    def play(self):
        if not self.is_playing and self.next_ready:
            self._play_current_track()
            self.is_playing = True
            self.next_ready = False

    def stop(self):
        pygame.mixer.music.fadeout(self.fade_duration)
        self.is_playing = False
        self.next_ready = True

    def update(self):
        if not pygame.mixer.music.get_busy() and self.is_playing:
            self.current_index = (self.current_index + 1) % len(self.track_keys)
            self.is_playing = False
            self.next_ready = True
            self.play()

    def _play_current_track(self):
        key = self.track_keys[self.current_index]
        track_info = self.tracks[key]
        if track_info["track"]:
            pygame.mixer.music.load(track_info["track"])
            pygame.mixer.music.set_volume(track_info["volume"])
            pygame.mixer.music.play(fade_ms=self.fade_duration)