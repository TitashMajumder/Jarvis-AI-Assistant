# Automation.py
import os
import subprocess
import requests
import asyncio
import keyboard
import webbrowser
from dotenv import dotenv_values
from AppOpener import close, open as appopen
from pywhatkit import search, playonyt
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
from Backend.SpotifyPlayer import play_song  # ✅ Make sure this path matches your structure

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = os.environ.get("Username", "Jarvis Assistant")

# Custom app URLs
custom_apps = {
     "facebook": "https://www.facebook.com",
     "instagram": "https://www.instagram.com",
     "whatsapp": "https://web.whatsapp.com",
     "youtube": "https://www.youtube.com"
}

# User-agent for scraping
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq API
client = Groq(api_key=GroqAPIKey)

# System message for LLM
messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {Username}, You're a content writer. You have to write content like letters, articles, etc."}]

# Ensure required folders exist
os.makedirs("Data", exist_ok=True)

# ----------------- FUNCTIONS -----------------
def GoogleSearch(topic):
     search(topic)
     return True

def PlayYoutube(query):
     try:
          playonyt(query)
          return f"Playing {query} on YouTube."
     except Exception as e:
          print(f"[ERROR] Couldn't play on YouTube: {e}")
          return "I couldn't play that song right now. Please try again later."


def YoutubeSearch(query):
     url = f"https://www.youtube.com/results?search_query={query}"
     webbrowser.open(url)
     return True

def Content(topic):
     def open_in_notepad(file_path):
          subprocess.Popen(['notepad.exe', file_path])

     def generate_content(prompt):
          messages.append({"role": "user", "content": prompt})
          completion = client.chat.completions.create(
               model="llama3-70b-8192",
               messages=SystemChatBot + messages,
               max_tokens=2048,
               temperature=0.7,
               top_p=1,
               stream=True
          )
          result = ""
          for chunk in completion:
               if chunk.choices[0].delta.content:
                    result += chunk.choices[0].delta.content
          result = result.replace("</s>", "")
          messages.append({"role": "assistant", "content": result})
          return result

     topic_clean = topic.replace("Content ", "").strip()
     content_text = generate_content(topic_clean)
     file_path = f"Data/{topic_clean.lower().replace(' ', '')}.txt"
     with open(file_path, "w", encoding="utf-8") as file:
          file.write(content_text)

     open_in_notepad(file_path)
     return True

def PlaySpotify(song):
     return play_song(song)

def OpenApp(app_name, sess=requests.session()):
     app_lower = app_name.strip().lower()
     try:
          appopen(app_lower, match_closest=True, output=True, throw_error=True)
          return True
     except:
          if app_lower in custom_apps:
               webbrowser.open(custom_apps[app_lower])
               return True

          if "website" in app_lower:
               app_lower = app_lower.replace("website", "").strip()

          for domain in [".com", ".org", ".net", ".ai", ".io"]:
               url = f"https://www.{app_lower.replace(' ', '')}{domain}"
               try:
                    if sess.get(url, timeout=4).status_code == 200:
                         webbrowser.open(url)
                         return True
               except:
                    continue

          fallback_url = f"https://www.google.com/search?q={app_name}"
          webbrowser.open(fallback_url)
          return True

def CloseApp(app_name):
     try:
          print(f"[DEBUG] Attempting to close: {app_name}")
          close(app_name, match_closest=True, output=True, throw_error=True)
          print(f"[DEBUG] Closed: {app_name}")
          return True
     except Exception as e:
          print(f"[WARNING] Exception during close: {e}")
          if "not running" in str(e).lower() or "no running instance" in str(e).lower():
               print(f"[INFO] {app_name} was already closed.")
               return True  # Consider already closed as success
          return False

def System(command):
     key_map = {
          "mute": "volume mute",
          "unmute": "volume mute",
          "volume up": "volume up",
          "volume down": "volume down"
     }
     if command in key_map:
          keyboard.press_and_release(key_map[command])
     return True

     # ----------------- COMMAND MAPPING -----------------
CommandMap = { 
     "open": OpenApp,
     "close": CloseApp,
     "play": PlayYoutube,         # Default YouTube play
     "content": Content,
     "google search": GoogleSearch,
     "youtube search": YoutubeSearch,
     "system": System,
     "spotify play": PlaySpotify
}

Aliases = {
     "yt": "youtube search",
     "search": "google search"
}

def match_command(command_lower):
     for prefix in CommandMap:
          if command_lower.startswith(prefix):
               return prefix, command_lower[len(prefix):].strip()
     for alias, real in Aliases.items():
          if command_lower.startswith(alias):
               return real, command_lower[len(alias):].strip()
     if "play" in command_lower and "on spotify" in command_lower:
          song = command_lower.replace("play", "").replace("on spotify", "").strip()
          return "spotify play", song
     if command_lower.startswith("spotify play"):
          return "spotify play", command_lower.replace("spotify play", "").strip()
     if command_lower.startswith("play"):
          return "play", command_lower[len("play"):].strip()
     if "search" in command_lower and "youtube" in command_lower:
          return "youtube search", command_lower.replace("youtube search", "").strip()
     if "search" in command_lower:
          return "google search", command_lower.replace("search", "").strip()
     return None, command_lower

# ----------------- ASYNC DISPATCHER -----------------
async def TranslateAndExecute(commands: list[str]):
     tasks = []
     for command in commands:
          command_lower = command.lower().strip()
          prefix, argument = match_command(command_lower)
          print(f"🧠 Matched: {prefix} | Argument: {argument}")
          if prefix and prefix in CommandMap:
               tasks.append(asyncio.to_thread(CommandMap[prefix], argument))
          else:
               print(f"[✗] No function mapped for: {command_lower}")
     results = await asyncio.gather(*tasks)
     for result in results:
          print(f"[✓] Command {'succeeded' if result else 'failed'}")
          yield result

async def Automation(intent_list):
     for task in intent_list:
          if ":" in task:
               action, app = task.split(":")
               app = app.strip().lower()

               if action == "open_app":
                    success = OpenApp(app)
                    print(f"[Automation] Opened {app}: {success}")

               elif action == "close_app":
                    success = CloseApp(app)
                    print(f"[Automation] Closed {app}: {success}")
