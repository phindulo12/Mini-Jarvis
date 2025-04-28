# Jarvis Assistant

Jarvis Assistant is a desktop-based voice assistant built using Python. It listens for voice commands and responds or acts accordingly.

---

## Features
- Voice Recognition (Speech-to-Text)
- Voice Command Handling
- GUI Interface with a logo and header (built using Tkinter)
- Continuous Listening Mode
- Robust error handling for silent environments

---

## Requirements

Install the following Python libraries before running the application:

```bash
pip install speechrecognition
pip install pyttsx3
pip install pyaudio
pip install tkinter (usually comes pre-installed with Python)
```

If you encounter issues installing PyAudio, use:
```bash
pip install pipwin
pipwin install pyaudio
```

---

## How to Run

1. Clone or download the project files.
2. Ensure you have a working microphone.
3. Open the terminal in the project directory.
4. Run the Python script:

```bash
python jarvis_assistant.py
```

5. Jarvis will start and display a GUI.
6. Speak your commands once you see "Listening..." in the console.

---

## Troubleshooting

- **WaitTimeoutError**:
  - Occurs when no speech is detected in the timeout window.
  - The assistant now handles this gracefully and keeps listening.

- **Microphone Not Found**:
  - Ensure your microphone is connected and enabled.

- **Speech Recognition Service Error**:
  - Ensure you have an active internet connection for Google Speech Recognition.

---

## Notes
- The UI uses a simple dark theme with a centered logo and title.
- Listening is continuous and non-blocking.
- Make sure to speak clearly into the microphone.

---

## Credits
- Built with Python.
- Uses `speech_recognition` for capturing audio.
- `pyttsx3` can be added for text-to-speech responses (optional enhancement).

---

## License
This project is open-source for personal and educational use.

