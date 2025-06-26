# Importing necessary modules
from selenium import webdriver                              # For controlling the browser
from selenium.webdriver.common.by import By                 # For locating elements
from selenium.webdriver.chrome.service import Service       # To manage ChromeDriver service
from selenium.webdriver.chrome.options import Options       # For setting browser options
from webdriver_manager.chrome import ChromeDriverManager    # Auto-installs ChromeDriver
from dotenv import dotenv_values                            # To load environment variables from .env file
import os                                                   # Provides a way of using operating system-dependent functionality
import mtranslate as mt                                     # For translating text using mtranslate module

# Load environment variables from .env file
env_vars = dotenv_values(".env")

# Get the input language specified in .env
InputLanguage = env_vars.get("InputLanguage")

# Define the HTML code for speech recognition frontend
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Inject the selected language into the HTML script
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the HTML file to disk
with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)

# Get current working directory
current_dir = os.getcwd()

# Create full path to the HTML file
Link = f"{current_dir}/Data/Voice.html"

# Configure Chrome browser options for Selenium
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')  # Set user agent
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Auto-allow mic access
chrome_options.add_argument("--use-fake-device-for-media-stream")  # Use fake mic input
# chrome_options.add_argument("--headless=new")  # Run browser in headless mode

# Set up Chrome WebDriver using WebDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define path to status file for assistant state
TempDirPath = rf"{current_dir}/Frontend/Files"

# Function to update assistant status
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

# Function to modify and format the spoken query
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    # If it's a question, ensure it ends with '?'
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Else, ensure it ends with '.'
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()  # Capitalize first letter

# Function to translate any non-English input to English
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")  # Translate from auto-detected language to English
    return english_translation.capitalize()

# Main speech recognition function using Selenium and HTML interface
def SpeechRecognition():
    # Open the HTML file in browser
    driver.get("file:///" + Link)

    # Click the "Start Recognition" button
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            # Get transcribed text from page
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                # If text is captured, stop recognition
                driver.find_element(by=By.ID, value="end").click()

                # If language is English, return modified query
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    # If not, translate and then return
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            pass  # Ignore errors silently

# If run directly, loop and keep recognizing
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)