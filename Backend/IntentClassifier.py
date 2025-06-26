def detect_intent(query: str):
     query = query.lower().strip()

     # SYSTEM CONTROL
     if "shutdown" in query or "turn off" in query:
          return "shutdown"
     elif "restart" in query or "reboot" in query:
          return "restart"
     elif "lock screen" in query or "lock system" in query:
          return "lock"
     elif "screenshot" in query or "take a screenshot" in query:
          return "screenshot"
     elif "volume up" in query:
          return "volume_up"
     elif "volume down" in query:
          return "volume_down"
     elif "get volume" in query:
          return "get volume"
     elif "set volume to" in query:
          return "set volume"
     elif "unmute" in query:
          return "unmute"
     elif "mute" in query:
          return "mute"

     # MEMORY CONTROL
     elif "remember" in query:
          return "memory_update"
     elif "what do you know about" in query or "what did i tell" in query:
          return "memory_read"
     elif "forget" in query:
          return "memory_forget"

     # MULTI-APP HANDLING (open / close)
     elif "open" in query:
          apps = query.replace("open", "").strip().split(" and ")
          return [f"open_app:{app.strip()}" for app in apps if app.strip()]
     
     elif "close" in query:
          apps = query.replace("close", "").strip().split(" and ")
          return [f"close_app:{app.strip()}" for app in apps if app.strip()]

     # MUSIC PLAYBACK
     elif "play" in query:
          if "spotify" in query:
               return "play_spotify"
          else:
               return "play_music"

     # CLIPBOARD
     elif "clipboard" in query or "copy" in query or "paste" in query:
          return "clipboard"

     # CHAT
     elif "stop" in query or "exit" in query or "go to sleep" in query:
          return "stop"
     elif any(phrase in query for phrase in ["who is", "what is", "define", "tell me about", "how to"]):
          return "chat"

     # FALLBACK
     else:
          return "chat"
