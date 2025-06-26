# Import necessary libraries
from groq import Groq                   # For Groq AI API interaction
from json import load, dump             # For handling JSON data
import datetime                         # For real-time date and time
from dotenv import dotenv_values        # For loading environment variables from .env file
import os

# Load environment variables from .env
env_vars = dotenv_values(".env")

# Retrieve credentials and custom names from .env
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq API client
client = Groq(api_key=GroqAPIKey)

# Initialize chat message list
messages = []

# System prompt for defining chatbot's behavior
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# List containing the system message
SystemChatBot = [
     {"role": "system", "content": System}
]

# Load existing chat history from file or create new if not found
try:
     with open(r"Data\ChatLog.json", "r") as f:
          messages = load(f)
except FileNotFoundError:
     with open(r"Data\ChatLog.json", "w") as f:
          dump([], f)

# Function to return real-time information (used in prompt context)
def RealtimeInformation():
     current_date_time = datetime.datetime.now()
     day = current_date_time.strftime("%A")
     date = current_date_time.strftime("%d")
     month = current_date_time.strftime("%B")
     year = current_date_time.strftime("%Y")
     hour = current_date_time.strftime("%H")
     minute = current_date_time.strftime("%M")
     second = current_date_time.strftime("%S")

     data = f"Please use this real-time information if needed, \n"
     data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
     data += f"Time: {hour} hours :{minute} minute :{second} seconds.\n"
     return data  # <-- You missed returning the data string, fixed here

# Function to remove empty lines from the AI's response
def AnswerModifier(Answer):
     lines = Answer.split('\n')
     non_empty_lines = [line for line in lines if line.strip()]
     modified_answer = '\n'.join(non_empty_lines)
     return modified_answer

# Core chatbot function
def ChatBot(Query):
     """ This function sends the user's query to the chatbot and returns the AI's response. """

     try:
          # Load previous chat log
          with open(r"Data\ChatLog.json", "r") as f:
               messages = load(f)

          # Append current user query
          messages.append({"role": "user", "content": f"{Query}"})

          # Generate response using Groq client
          completion = client.chat.completions.create(
               model="llama3-70b-8192",
               messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
               max_tokens=1024,
               temperature=0.7,
               top_p=1,
               stream=True,
               stop=None
          )

          Answer = ""

          # Read the streamed output
          for chunk in completion:
               if chunk.choices[0].delta.content:
                    Answer += chunk.choices[0].delta.content

          Answer = Answer.replace("</s>", "")

          # Save AI response to message log
          messages.append({"role": "assistant", "content": Answer})

          # Save updated chat log
          with open(r"Data\ChatLog.json", "w") as f:
               dump(messages, f, indent=4)

          return AnswerModifier(Answer)  # Clean up the response before returning

     except Exception as e:
          print(f"Error: {e}")
          # Reset chat log if an error occurs
          with open(r"Data\ChatLog.json", "w") as f:
               dump([], f, indent=4)
          return ChatBot(Query)  # Retry the same query

# Entry point
if __name__ == "__main__":
     while True:
          user_input = input("Enter Your Question: ")
          print(ChatBot(user_input))