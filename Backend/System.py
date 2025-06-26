import os
import ctypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import comtypes.client
import time
import re
import pyautogui
import datetime

def System(command):
     command = command.lower()

     if command == "shutdown":
          os.system("shutdown /s /t 1")

     elif command == "restart":
          os.system("shutdown /r /t 1")

     elif command == "lock":
          ctypes.windll.user32.LockWorkStation()

     elif command == "volume up":
          _change_volume(0.1)

     elif command == "volume down":
          _change_volume(-0.1)

     elif command in ["mute", "unmute"]:
          try:
               devices = AudioUtilities.GetSpeakers()
               interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
               volume = interface.QueryInterface(IAudioEndpointVolume)
               volume.SetMute(1 if command == "mute" else 0, None)
          except Exception as e:
               print(f"[Audio ERROR] {e}")

     elif command == "get volume":
          try:
               devices = AudioUtilities.GetSpeakers()
               interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
               volume = interface.QueryInterface(IAudioEndpointVolume)
               current = volume.GetMasterVolumeLevelScalar()  # returns 0.0–1.0
               percent = int(current * 100)
               return f"Current volume is {percent} percent."
          except Exception as e:
               return f"Couldn't get volume: {e}"

     elif "set volume to" in command:
          try:
               match = re.search(r"set volume to (\d+)", command)
               if match:
                    vol_value = int(match.group(1))
                    vol_value = min(max(vol_value, 0), 100)  # clamp between 0–100
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = interface.QueryInterface(IAudioEndpointVolume)
                    volume.SetMasterVolumeLevelScalar(vol_value / 100.0, None)
                    return f"Volume set to {vol_value} percent."
               else:
                    return "Sorry, I couldn't find a valid number in your volume command."
          except Exception as e:
               return f"Failed to set volume: {e}"

     elif command == "screenshot":
          try:
               timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
               filename = f"Screenshot_{timestamp}.png"
               path = os.path.join(os.getcwd(), "Screenshots")
               os.makedirs(path, exist_ok=True)
               full_path = os.path.join(path, filename)
               screenshot = pyautogui.screenshot()
               screenshot.save(full_path)
               return f"Screenshot saved as {filename}."
          except Exception as e:
               return f"Failed to take screenshot: {e}"

def _change_volume(delta):
     devices = AudioUtilities.GetSpeakers()
     interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
     volume = interface.QueryInterface(IAudioEndpointVolume)
     current_volume = volume.GetMasterVolumeLevelScalar()
     volume.SetMasterVolumeLevelScalar(min(max(0.0, current_volume + delta), 1.0), None)