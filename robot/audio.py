import pygame
from pygame import mixer
import random

class AudioManager:
    def __init__(self):
        self.AUDIO_ENABLED = True
        self.audio_dict = {}

        if self.AUDIO_ENABLED:
            mixer.init()
            audio_folder = '/Resources/Sounds/'
            
            # Load audio files
            self.startup1 = pygame.mixer.Sound(audio_folder + 'Other/startup_1.mp3')
            self.startup2 = pygame.mixer.Sound(audio_folder + 'Other/startup_2.mp3')
            self.error = pygame.mixer.Sound(audio_folder + 'Other/error.mp3')
            self.pause = pygame.mixer.Sound(audio_folder + 'Other/pause.mp3')
            self.startMLSound = pygame.mixer.Sound(audio_folder + 'Other/starting_ML.mp3')
            self.stopMLSound = pygame.mixer.Sound(audio_folder + 'Other/stopping_ML.mp3')

            self.walkMode = pygame.mixer.Sound(audio_folder + 'Mode_Switch/walking.mp3')
            self.pushUpsMode = pygame.mixer.Sound(audio_folder + 'Mode_Switch/push_ups.mp3')
            self.legControlMode = pygame.mixer.Sound(audio_folder + 'Mode_Switch/leg_control.mp3')
            self.gyroMode = pygame.mixer.Sound(audio_folder + 'Mode_Switch/gyro.mp3')
            self.machineLearningMode = pygame.mixer.Sound(audio_folder + 'Mode_Switch/machine_learning.mp3')
            self.danceMode = pygame.mixer.Sound(audio_folder + 'Mode_Switch/dance_mode.mp3')

            self.song1 = pygame.mixer.Sound(audio_folder + 'Songs/mayahe.mp3')
            self.song2 = pygame.mixer.Sound(audio_folder + 'Songs/WhoLetTheDogsOut.mp3')
            self.song3 = pygame.mixer.Sound(audio_folder + 'Songs/Crazy_La_Paint.mp3')
            self.song4 = pygame.mixer.Sound(audio_folder + 'Songs/Party_Rock.mp3')

            # Set volumes
            self.startup1.set_volume(0.2)
            self.startup2.set_volume(0.125)
            self.pause.set_volume(0.4)
            self.error.set_volume(0.25)
            self.startMLSound.set_volume(0.4)
            self.stopMLSound.set_volume(0.4)

            self.walkMode.set_volume(0.5)
            self.pushUpsMode.set_volume(0.5)
            self.legControlMode.set_volume(0.5)
            self.gyroMode.set_volume(0.5)
            self.machineLearningMode.set_volume(0.5)
            self.danceMode.set_volume(0.45)

            self.song1.set_volume(0.25)  # Mayahe
            self.song2.set_volume(0.2)   # Who Let The Dogs Out
            self.song3.set_volume(0.2)   # Crazy La Paint
            self.song4.set_volume(0.25)  # Party Rock

            # Dictionary to map sound names to sound objects
            self.audio_dict = {
                "startMLSound": self.startMLSound,
                "stopMLSound": self.stopMLSound,
                "walkMode": self.walkMode,
                "pushUpsMode": self.pushUpsMode,
                "legControlMode": self.legControlMode,
                "gyroMode": self.gyroMode,
                "machineLearningMode": self.machineLearningMode,
                "danceMode": self.danceMode,
                "song1": self.song1,
                "song2": self.song2,
                "song3": self.song3,
                "song4": self.song4,
                "startup1": self.startup1,
                "startup2": self.startup2,
                "pause": self.pause,
                "error": self.error
            }
            
# If audio is enabled, and this function is called, audio will play sound_key
    def play_sound(self, sound_key):
        if self.AUDIO_ENABLED and sound_key in self.audio_dict:
            pygame.mixer.Sound.play(self.audio_dict[sound_key])
            
    def play_mode_sounds(self, mode):
        # Map modes to sound keys
        mode_sounds = {
            0: "walkMode",
            1: "pushUpsMode",
            2: "legControlMode",
            3: "gyroMode",
            4: "machineLearningMode",
            5: "danceMode"
        }
        sound_key = mode_sounds.get(mode)
        if sound_key:
            self.play_sound(sound_key)

    # Takes in the song name, calls play_sound
    def play_songs(self, song):
        if song == -1:
            # Play a random song
            self.play_sound(random.choice(["song1", "song2", "song3", "song4"]))
        else:
            song_key = f"song{song}"
            self.play_sound(song_key)
