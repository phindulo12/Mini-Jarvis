import tkinter as tk
from tkinter import scrolledtext
from threading import Thread, Event
from queue import Queue
import requests
import speech_recognition as sr
import pyttsx3
import webbrowser
import schedule
import time
from datetime import datetime

# --- Constants ---
OPENWEATHER_API_KEY = "30a21fb07e103185e3f61b9fb14c6f91"
NEWS_API_KEY = "83605885411244869e7434a4312e55c1"

# --- Speech Manager ---
class SpeechManager:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.speaking_thread = None
        self.stop_speaking = Event()

    def speak(self, text):
        """Speak text, allowing interruption."""
        self.stop()

        def _speak():
            self.engine.say(text)
            self.engine.runAndWait()

        self.stop_speaking.clear()
        self.speaking_thread = Thread(target=_speak)
        self.speaking_thread.start()
        return text

    def stop(self):
        """Stop speaking immediately."""
        if self.speaking_thread and self.speaking_thread.is_alive():
            self.engine.stop()
            self.stop_speaking.set()

# Initialize speech manager globally
speech_manager = SpeechManager()

def speak(text):
    return speech_manager.speak(text)

# --- Helper Functions ---
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source, timeout=5)
    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except (sr.UnknownValueError, sr.RequestError):
        return ""

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data.get('cod') != 200:
        return "City not found."
    weather = data['weather'][0]['description']
    temperature = data['main']['temp']
    return f"Weather in {city}: {weather}, {temperature}°C."

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get('articles', [])
    if not articles:
        return "No news found."
    return "Top News: " + " | ".join([article['title'] for article in articles[:3]])

def set_reminder(task, time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
        schedule.every().day.at(time_str).do(lambda: speak(f"Reminder: {task}"))
        return f"Reminder set for {task} at {time_str}."
    except ValueError:
        return "Invalid time format (use HH:MM)."

def ask_groq(prompt):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def handle_command(command, gui_queue):
    if not command:
        return

    gui_queue.put(("user", f"You: {command}\n", "neutral"))

    if "open youtube" in command:
        webbrowser.open("https://youtube.com")
        response = speak("Opening YouTube.")
        emotion = "happy"
    elif "open google" in command:
        webbrowser.open("https://google.com")
        response = speak("Opening Google.")
        emotion = "happy"
    elif "weather" in command:
        response = speak("Which city?")
        city = listen_command()
        if city:
            response += "\n" + speak(get_weather(city))
            emotion = "thinking"
        else:
            response = speak("City not provided.")
            emotion = "sad"
    elif "news" in command:
        response = speak(get_news())
        emotion = "thinking"
    elif "set reminder" in command:
        response = speak("What should I remind you about?")
        task = listen_command()
        response += "\n" + speak("At what time (HH:MM)?")
        time_str = listen_command()
        response += "\n" + speak(set_reminder(task, time_str))
        emotion = "happy"
    else:
        response = speak(ask_groq(command))
        emotion = "thinking"

    gui_queue.put(("jarvis", f"Jarvis: {response}\n", emotion))

# --- GUI Class ---
class JarvisGUI:
    def __init__(self, root):
        self.root = root
        root.title("Jarvis Assistant")
        root.geometry("600x550")
        root.configure(bg="#1e1e1e")

        # Jarvis Face
        self.face_label = tk.Label(root, text="🤖", font=("Helvetica", 60), bg="#1e1e1e", fg="white")
        self.face_label.pack(pady=5)

        # Title
        tk.Label(root, text="Jarvis Assistant", font=("Helvetica", 20, "bold"), fg="cyan", bg="#1e1e1e").pack(pady=5)

        # Chat Area
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#121212", fg="white", font=("Consolas", 12))
        self.chat_area.pack(expand=True, fill="both", padx=10, pady=10)
        self.chat_area.config(state=tk.DISABLED)

        # Button Frame
        button_frame = tk.Frame(root, bg="#1e1e1e")
        button_frame.pack(pady=10)

        # Start Button
        self.start_button = tk.Button(
            button_frame,
            text="Start Listening",
            command=self.start_listening,
            bg="green",
            fg="white",
            font=("Helvetica", 12)
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Stop Button
        self.stop_button = tk.Button(
            button_frame,
            text="Stop Listening",
            command=self.stop_listening,
            bg="red",
            fg="white",
            font=("Helvetica", 12),
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Thread Control
        self.command_queue = Queue()
        self.stop_event = Event()
        self.listening_thread = None

    def start_listening(self):
        """Start the voice command listener thread."""
        self.stop_event.clear()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.listening_thread = Thread(target=self.listen_loop, daemon=True)
        self.listening_thread.start()
        self.root.after(100, self.update_gui)

    def stop_listening(self):
        """Stop the voice command listener."""
        self.stop_event.set()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def listen_loop(self):
        """Background thread for listening to commands."""
        while not self.stop_event.is_set():
            command = listen_command()
            if command:
                if "stop" in command or "exit" in command:
                    self.command_queue.put(("jarvis", "Jarvis: Goodbye!\n", "sad"))
                    self.stop_listening()
                    break
                handle_command(command, self.command_queue)
            schedule.run_pending()
            time.sleep(1)

    def update_gui(self):
        """Update the GUI with new messages."""
        while not self.command_queue.empty():
            sender, message, emotion = self.command_queue.get()
            self.chat_area.config(state=tk.NORMAL)
            tag = "user" if sender == "user" else "jarvis"
            self.chat_area.insert(tk.END, message, tag)
            self.chat_area.config(state=tk.DISABLED)
            self.chat_area.see(tk.END)
            self.update_face(emotion)

        self.chat_area.tag_config("user", foreground="lightblue")
        self.chat_area.tag_config("jarvis", foreground="lightgreen")
        self.root.after(100, self.update_gui)

    def update_face(self, emotion):
        """Update Jarvis's face based on emotion."""
        faces = {
            "thinking": "🧠",
            "happy": "😄",
            "sad": "😔",
            "neutral": "🤖"
        }
        self.face_label.config(text=faces.get(emotion, "🤖"))

# --- Main ---
if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisGUI(root)
    app.start_listening()  # <-- ADD THIS!
    root.mainloop()
