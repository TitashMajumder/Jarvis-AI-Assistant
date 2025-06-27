import subprocess
import pyautogui
import pygetwindow as gw
import shutil
import time
import os

def focus_vscode_window():
     for window in gw.getWindowsWithTitle("Visual Studio Code"):
          if not window.isMinimized:  # ✅ this works
               window.activate()
               time.sleep(0.5)
               return True
     return False

def open_terminal_in_vscode():
     if focus_vscode_window():
          pyautogui.hotkey("ctrl", "`")  # VS Code terminal shortcut
          return "Opening terminal in VS Code"
     else:
          return "VS Code window not found. Please make sure VS Code is open."
     
def open_file_in_vscode(file_path: str):
    full_path = os.path.abspath(file_path)
    if not shutil.which("code"):
        raise EnvironmentError("VS Code command-line tool 'code' is not found in PATH.")
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File '{file_path}' not found at '{full_path}'")
    subprocess.Popen(["code", full_path], shell=True)
    return f"Opening file: {file_path}"

def create_and_open_file(filename):
     try:
          path = os.path.join(os.getcwd(), filename)
          with open(path, 'w') as f:
               f.write("")  # Create empty file
          try:
               subprocess.Popen(["code", path], shell=True)
               return f"I've created and opened {filename} in VS Code!"
          except FileNotFoundError:
               return f"Created {filename}, but couldn't open it — is VS Code installed?"
     except Exception as e:
          return f"Failed to create {filename}: {e}"

def run_file_based_on_extension(extension):
     pyautogui.hotkey("ctrl", "1")     # Focus editor
     time.sleep(0.3)
     pyautogui.press("enter")          # Activate the file
     time.sleep(0.3)
     pyautogui.hotkey("ctrl", "shift", "p")
     time.sleep(0.8)
     
     if extension == "py":
          pyautogui.write("Run Python File in Terminal", interval=0.05)
     elif extension == "cpp":
          pyautogui.write("C/C++: Run", interval=0.05)
     elif extension == "java":
          pyautogui.write("Java: Run", interval=0.05)
     elif extension == "html":
          pyautogui.write("Live Server: Open with Live Server", interval=0.05)
     elif extension == "js":
          pyautogui.write("Run Code", interval=0.05)
     else:
          pyautogui.write("Run Code", interval=0.05)

     time.sleep(0.3)
     pyautogui.press("enter")
     return f"Executed run command for .{extension} file."


def open_and_run_file(file_path: str):
     response = open_file_in_vscode(file_path)
     extension = file_path.split('.')[-1].lower()
     time.sleep(2.0)  # Give VS Code time to open the file
     
     if focus_vscode_window():  # ✅ Only run if window was focused
         run_response = run_file_based_on_extension(extension)
     else:
         run_response = "VS Code not found or couldn't be focused."
     
     return f"{response}. {run_response}"
