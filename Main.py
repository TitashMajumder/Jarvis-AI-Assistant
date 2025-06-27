# -------------------- IMPORTS --------------------

from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.WakeWord import WakeWordDetector
from Backend.MainExecution import ExecuteQuery
from Backend.IntentClassifier import detect_intent
from PyQt5.QtWidgets import QApplication
from dotenv import dotenv_values
from Frontend.GUI import MainWindow
from time import sleep
import subprocess
import threading
import json
import asyncio
import sys
import time

# -------------------- CONFIGS --------------------
env_vars = dotenv_values(".env")
EnableImageGeneration = env_vars.get("EnableImageGeneration", "True") == "True"
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")
current_mode = "wake"
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''
subprocesses = []

# -------------------- GUI HANDLING --------------------
def ShowDefaultChatIfNoChats():
     with open(r'Data\ChatLog.json', "r", encoding='utf-8') as f:
          if len(f.read()) < 5:
               with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                    file.write("")
               with open(TempDirectoryPath('Response.data'), 'w', encoding='utf-8') as file:
                    file.write(DefaultMessage)

def ReadChatLogJson():
     with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
          return json.load(file)

def ChatLogIntegration():
     data = ReadChatLogJson()
     formatted = ""
     for entry in data:
          role = Username if entry["role"] == "user" else Assistantname
          formatted += f"{role}: {entry['content']}\n"
     with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
          file.write(AnswerModifier(formatted))

def ShowChatsOnGUI():
     with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
          result = '\n'.join(file.read().split('\n'))
     with open(TempDirectoryPath('Response.data'), 'w', encoding='utf-8') as f:
          f.write(result)

def InitialExecution():
     SetMicrophoneStatus("False")
     ShowTextToScreen("")
     ShowDefaultChatIfNoChats()
     ChatLogIntegration()
     ShowChatsOnGUI()

# -------------------- MAIN LOGIC --------------------
async def MainExecution(window):
     query = ""  # ← define in advance
     try:
               SetAssistantStatus("Listening...")
               query = SpeechRecognition()
               print(f"[DEBUG] Query received: {query}")
               # ✅ Update chat with user query
               chat_section = window.message_screen.get_chat_section()
               chat_section.add_message_signal.emit(f"{Username} : {query}", "White")
               ShowTextToScreen(f"{Username} : {query}")
               SetAssistantStatus("Thinking...")
               answer, intent_type = await ExecuteQuery(query)
               print(f"🧠 [DEBUG] JARVIS Answer: {answer}")

               if answer and isinstance(answer, str) and answer.strip():
                    ShowTextToScreen(f"{Assistantname} : {answer}")
                    print("[DEBUG] Speaking response...")
                    TextToSpeech(answer, gui_callback=chat_section.add_message_signal.emit)
               else:
                    fallback = "I'm not sure what to say."
                    ShowTextToScreen(f"{Assistantname} : {fallback}")
                    TextToSpeech(fallback, gui_callback=chat_section._addMessage)
     except Exception as e:
               print(f"[MainExecution ERROR] {e}")
     finally:
               SetAssistantStatus("Waiting for 'Jarvis'...")
               print("[DEBUG] Resetting assistant status...")
               return intent_type  # e.g., "chat", "task", or "stop"

# -------------------- WRAPPER FOR AWAIT --------------------
def MainExecutionWrapper(window):
     global current_mode
     try:
          loop = asyncio.new_event_loop()
          asyncio.set_event_loop(loop)
          while current_mode == "conversation":
               intent = loop.run_until_complete(MainExecution(window))
               if intent in ["stop", "task"]:
                    current_mode = "wake"
                    SetAssistantStatus("Waiting for 'Jarvis'...")  # ✅ reset status
                    threading.Thread(target=lambda: StartWakeWord(window), daemon=True).start()  # ✅ restart wake word
                    break
               time.sleep(1)
     except Exception as e:
          print(f"[MainExecutionWrapper ERROR] {e}")

# -------------------- WAKE WORD LISTENER --------------------
def StartWakeWord(window):
     global current_mode
     def start_conversation():
          global current_mode
          if current_mode == "wake":
               current_mode = "conversation"
               print("🧠 Switching to conversation mode")
               MainExecutionWrapper(window)  # No loop
     detector = WakeWordDetector(callback=start_conversation)
     detector.start_listening()

# -------------------- PROGRAM ENTRY --------------------
if __name__ == "__main__":
     InitialExecution()
     app = QApplication(sys.argv)
     window = MainWindow()
     window.show()
     threading.Thread(target=lambda: StartWakeWord(window), daemon=True).start()
     SetAssistantStatus("Waiting for 'Jarvis'...")
     sys.exit(app.exec_())