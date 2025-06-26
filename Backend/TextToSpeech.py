import os
import uuid
import random
from gtts import gTTS
import pygame
from time import sleep
import pyaudio

# Ensure SDL uses the right audio driver on Windows
os.environ["SDL_AUDIODRIVER"] = "directsound"

# Optional headphone detection (used only for debug/logging)
def detect_headphone_name(show=False):
     p = pyaudio.PyAudio()
     preferred = None
     for i in range(p.get_device_count()):
          info = p.get_device_info_by_index(i)
          name = info.get('name', '').lower()
          max_out = info.get('maxOutputChannels', 0)

          if show:
               print(f"🔈 [{i}] {info['name']} - Out: {max_out}")
          if max_out > 0 and ("headphones" in name or "boult" in name):
               preferred = info['name']
               break
     p.terminate()
     if show and preferred:
          print(f"🎧 Preferred output device found: {preferred}")
     return preferred

# Core TTS function
def TTS(text, func=lambda r=None: True):
     temp_filename = f"Data/{uuid.uuid4().hex}.mp3"
     try:
          # Generate speech with gTTS
          tts = gTTS(text)
          tts.save(temp_filename)
          # Play the MP3
          if not pygame.mixer.get_init():
               pygame.mixer.init()
          pygame.mixer.music.load(temp_filename)
          pygame.mixer.music.play()

          while pygame.mixer.music.get_busy():
               if func() is False:
                    break
               pygame.time.Clock().tick(10)

     except Exception as e:
          print(f"[TTS ERROR] {e}")

     finally:
          try:
               pygame.mixer.music.stop()
               pygame.mixer.quit()
          except:
               pass
          try:
               if os.path.exists(temp_filename):
                    os.remove(temp_filename)
          except Exception as e:
               print(f"[TTS CLEANUP ERROR] Couldn't delete temp file: {e}")

# Smart speech control with summarization
def TextToSpeech(text, func=lambda r=None: True, gui_callback=None):
     print(f"[TTS DEBUG] Input: {text}")

     if gui_callback:
          gui_callback(text, "Blue")  # 👈 Always show full message
     TTS(text, func)                # 👈 Always speak full message
