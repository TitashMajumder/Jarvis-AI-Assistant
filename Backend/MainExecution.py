from Backend.IntentClassifier import detect_intent
from Backend.Automation import PlaySpotify, OpenApp, CloseApp, GoogleSearch, YoutubeSearch, Content, System, PlayYoutube, Automation
from Backend.SpotifyPlayer import play_song
from Backend.Chatbot import ChatBot
from Backend.UserMemory import remember, recall, forget
from Backend.System import System
from Backend.TextToSpeech import TextToSpeech
import string
import asyncio

APP_NAME_MAP = {
    "file explorer": "File Explorer",
    "whatsapp": "whatsapp",
    "spotify": "spotify"
}

async def ExecuteQuery(query: str) -> str:
     intents = detect_intent(query)
     query = query.lower().strip()
     print(f"🧠 Detected Intent: {intents} | Query: {query}")
     try:
          # MULTI-TASK INTENTS
          if isinstance(intents, list):
               responses = []
               for intent in intents:
                    if intent.startswith("open_app:"):
                         app_name = intent.split(":")[1].strip().replace(".", "")
                         success = OpenApp(app_name)
                         responses.append(f"{app_name.title()} launched." if success else f"Failed to open {app_name}.")
                    elif intent.startswith("close_app:"):
                         app_name = intent.split(":")[1].strip().replace(".", "").lower()
                         mapped_app = APP_NAME_MAP.get(app_name, app_name)
                         success = CloseApp(mapped_app)
                         display_name = app_name.replace("-", " ").title()
                         responses.append(f"{display_name} closed." if success else f"Failed to close {display_name}.")
                    else:
                         responses.append(f"Unknown intent: {intent}")
               return " & ".join(responses), "task"

          # SINGLE INTENT
          intent = intents
          if intent == "shutdown":
               System("shutdown")
               return "Shutting down the system.", "stop"

          elif intent == "restart":
               System("restart")
               return "Restarting the system.", "stop"

          elif intent == "lock":
               System("lock")
               return "Locking your device.", "stop"

          elif intent == "screenshot":
               response = System("screenshot")
               return response, "task"

          elif intent == "volume_up":
               System("volume up")
               return "Volume increased.", "task"

          elif intent == "volume_down":
               System("volume down")
               return "Volume decreased.", "task"
          
          elif intent == "get volume":
               response = System("get volume")
               return response, "task"

          elif intent == "set volume":
               response = System(query)  # pass full query so System() can extract %
               return response, "task"

          elif intent == "unmute":
               System("unmute")
               return "System unmuted.", "task"

          elif intent == "mute":
               System("mute")
               return "System muted.", "task"

          elif intent == "memory_update":
               key_value = query.replace("remember", "").strip().split(" is ")
               if len(key_value) == 2:
                    return remember(key_value[0].strip(), key_value[1].strip()), "task"
               return "Sorry, I didn't understand what to remember.", "task"

          elif intent == "memory_read":
               key = query.replace("what do you know about", "").replace("what did i tell you about", "").strip()
               return recall(key), "task"

          elif intent == "memory_forget":
               key = query.replace("forget", "").strip()
               return forget(key), "task"

          elif intent == "open_app":
               app_name = query.replace("open", "").strip()
               success = OpenApp(app_name)
               return (f"Opening {app_name}." if success else f"Couldn't open {app_name}."), "task"

          elif intent.startswith("close_app:"):
               app_name = intent.split(":")[1].strip().replace(".", "").lower()
               mapped_app = APP_NAME_MAP.get(app_name, app_name)
               success = CloseApp(app_name)
               display_name = app_name.replace("-", " ").title()
               return (f"{display_name} closed." if success else f"Failed to close {display_name}."), "task"

          elif intent == "play_spotify":
               song_name = query.replace("play", "").replace("on spotify", "").strip()
               return play_song(song_name), "task"

          elif intent == "play_music":
               song_name = query
               for phrase in ["play", "song", "music", "can you", "please", "for me", "a song", "the song"]:
                    song_name = song_name.replace(phrase, "")
               song_name = song_name.strip(" .?")
               PlayYoutube(song_name)
               return f"Playing {song_name} on YouTube.", "task"

          elif intent == "google_search":
               topic = query.replace("search", "").strip()
               GoogleSearch(topic)
               return f"Searching Google for '{topic}'...", "task"

          elif intent == "youtube_search":
               topic = query.replace("search", "").replace("youtube", "").strip()
               YoutubeSearch(topic)
               return f"Searching YouTube for '{topic}'...", "task"

          elif intent == "content":
               topic = query.replace("content", "").strip()
               Content(topic)
               return f"Generated content for '{topic}' and opened it in Notepad.", "task"

          elif intent == "stop":
               return "Going to sleep now. Say 'Jarvis' when you need me.", "stop"

          elif intent == "chat":
               return ChatBot(query), "chat"

          else:
               return ChatBot(query), "chat"

     except Exception as e:
          return f"An error occurred while executing your command: {e}", "task"