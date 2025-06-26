# UserMemory.py

import json
import os

MEMORY_FILE = "Data/memory.json"

# Ensure memory file exists
if not os.path.exists(MEMORY_FILE):
     with open(MEMORY_FILE, "w") as f:
          json.dump({}, f)

# Store a memory key-value pair
def remember(key, value):
     with open(MEMORY_FILE, "r") as f:
          data = json.load(f)
     data[key.lower()] = value
     with open(MEMORY_FILE, "w") as f:
          json.dump(data, f, indent=4)
     return f"Okay, I’ll remember that {key} is {value}."

# Retrieve a memory by key
def recall(key):
     with open(MEMORY_FILE, "r") as f:
          data = json.load(f)
     return data.get(key.lower(), f"I don’t remember anything about {key}.")

# Forget a memory key
def forget(key):
     with open(MEMORY_FILE, "r") as f:
          data = json.load(f)
     if key.lower() in data:
          del data[key.lower()]
          with open(MEMORY_FILE, "w") as f:
               json.dump(data, f, indent=4)
          return f"Okay, I’ve forgotten about {key}."
     else:
          return f"I wasn’t remembering anything about {key}."
