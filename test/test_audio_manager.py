import sys
import os

# Ensure the parent directory is in sys.path so that the 'robot' package is found.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import unittest
import logging
from unittest.mock import patch

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestAudioManager")

# --- Dummy Sound Class for Testing ---
class DummySound:
    def __init__(self, filename):
        self.filename = filename
        self.play_called = False
        self.volume = None

    def play(self):
        self.play_called = True
        logger.info(f"DummySound: Playing sound from '{self.filename}'.")

    def set_volume(self, volume):
        self.volume = volume
        logger.info(f"DummySound: Setting volume for '{self.filename}' to {volume}.")

# Function that returns a DummySound when pygame.mixer.Sound is called.
def dummy_sound_constructor(filename):
    return DummySound(filename)

# --- Test Cases for AudioManager ---
# Patch the mixer initialization and Sound creation.
@patch('pygame.mixer.init')
@patch('pygame.mixer.Sound', side_effect=dummy_sound_constructor)
class TestAudioManager(unittest.TestCase):
    
    def setUp(self, *args, **kwargs):
        logger.info("Setting up AudioManager instance for tests.")
        from robot.audio_manager import AudioManager  # Adjusted import with sys.path set up above.
        self.audio_manager = AudioManager()

    def test_play_sound_valid(self, mock_sound, mock_init):
        logger.info("Test: play_sound with a valid key 'startup1'.")
        self.audio_manager.audio_dict["startup1"].play_called = False
        self.audio_manager.play_sound("startup1")
        self.assertTrue(
            self.audio_manager.audio_dict["startup1"].play_called,
            "The 'startup1' sound should have been played."
        )

    def test_play_sound_invalid(self, mock_sound, mock_init):
        logger.info("Test: play_sound with an invalid key (should not play any sound).")
        for sound in self.audio_manager.audio_dict.values():
            sound.play_called = False
        self.audio_manager.play_sound("non_existent_sound")
        for key, sound in self.audio_manager.audio_dict.items():
            self.assertFalse(
                sound.play_called,
                f"Sound '{key}' should not have been played for an invalid key."
            )

    def test_play_mode_sounds(self, mock_sound, mock_init):
        logger.info("Test: play_mode_sounds for each mode.")
        mode_mapping = {
            0: "walkMode",
            1: "pushUpsMode",
            2: "legControlMode",
            3: "gyroMode",
            4: "machineLearningMode",
            5: "danceMode"
        }
        for mode, expected_sound in mode_mapping.items():
            self.audio_manager.audio_dict[expected_sound].play_called = False
            logger.info(f"  Testing mode {mode} (expecting '{expected_sound}').")
            self.audio_manager.play_mode_sounds(mode)
            self.assertTrue(
                self.audio_manager.audio_dict[expected_sound].play_called,
                f"Sound '{expected_sound}' should have been played for mode {mode}."
            )

    def test_play_songs_random(self, mock_sound, mock_init):
        logger.info("Test: play_songs with -1 (should play one random song).")
        song_keys = ["song1", "song2", "song3", "song4"]
        for key in song_keys:
            self.audio_manager.audio_dict[key].play_called = False
        self.audio_manager.play_songs(-1)
        played = [key for key in song_keys if self.audio_manager.audio_dict[key].play_called]
        logger.info(f"  Random song played: {played}")
        self.assertEqual(
            len(played), 1,
            "Exactly one random song should have been played when song parameter is -1."
        )

    def test_play_songs_specific(self, mock_sound, mock_init):
        logger.info("Test: play_songs with a specific song number (e.g., 2).")
        self.audio_manager.audio_dict["song2"].play_called = False
        self.audio_manager.play_songs(2)
        self.assertTrue(
            self.audio_manager.audio_dict["song2"].play_called,
            "The 'song2' sound should have been played for song parameter 2."
        )

if __name__ == '__main__':
    unittest.main()
