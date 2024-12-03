import tkinter as tk
from tkinter import scrolledtext
import socketio
import pyttsx3
import speech_recognition as sr
import sys
import io
import time

# Thiết lập mã hóa UTF-8 cho console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Địa chỉ server WebSocket
SERVER_URL = "https://bot-sever-aice.onrender.com"

# Tạo client WebSocket
sio = socketio.Client()

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot Client")
        self.root.geometry("600x600")
        self.root.configure(bg="#1e1e2f")
        
        self.center_window(600, 600)

        self.header = tk.Label(
            root, text="🎨 Chatbot Client 🎤",
            font=("Montserrat", 16, "bold"),
            fg="#ffffff", bg="#1e1e2f"
        )
        self.header.grid(row=0, column=0, columnspan=3, pady=(10, 0))

        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', height=20, width=50,
            bg='#2c2c3e', fg="#f0f0f0", font=('Roboto', 12),
            bd=0, highlightthickness=1, highlightbackground="#4CAF50"
        )
        self.chat_area.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.entry = tk.Entry(
            root, width=40, font=('Roboto', 12),
            bg="#2c2c3e", fg="#ffffff", insertbackground="#ffffff",
            bd=0, highlightthickness=1, highlightbackground="#4CAF50"
        )
        self.entry.grid(row=2, column=0, padx=10, pady=10)
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = tk.Button(
            root, text="Send",
            command=self.send_message,
            bg='#4CAF50', fg='white', font=('Roboto', 12, 'bold'),
            relief='flat', activebackground="#45a049", activeforeground="white",
            cursor="hand2"
        )
        self.send_button.grid(row=2, column=1, padx=10, pady=10)

        self.voice_button = tk.Button(
            root, text="🎤 Speak",
            command=self.speak_message,
            bg='#2196F3', fg='white', font=('Roboto', 12, 'bold'),
            relief='flat', activebackground="#1976D2", activeforeground="white",
            cursor="hand2"
        )
        self.voice_button.grid(row=2, column=2, padx=10, pady=10)

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        # Biến cờ để kiểm soát việc bot sử dụng TTS
        self.tts_enabled = False

        self.connect_to_server()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def connect_to_server(self):
        @sio.event
        def connect():
            print("Kết nối thành công tới server!")
            self.display_message("Bot: Connected to server.")

        @sio.event
        def disconnect():
            print("Ngắt kết nối từ server!")
            self.display_message("Bot: Disconnected from server.")

        @sio.on('message')
        def on_message(data):
            print(f"Phản hồi từ server: {data}")
            self.typing_effect(f"Bot: {data}")

        try:
            sio.connect(SERVER_URL)
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.display_message(f"Error connecting to server: {e}")

    def send_message(self):
        self.tts_enabled = False  # Tắt TTS khi gửi tin nhắn qua entry
        user_message = self.entry.get()
        if user_message.strip():
            self.display_message(f"You: {user_message}")
            try:
                sio.send(user_message)
            except Exception as e:
                self.display_message(f"Error sending message: {e}")
            self.entry.delete(0, tk.END)

    def speak_message(self):
        self.tts_enabled = True  # Bật TTS khi sử dụng nút Speak
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                self.display_message("🎤 Bot: Listening...")
                audio = recognizer.listen(source, timeout=5)
                user_message = recognizer.recognize_google(audio, language="en-US")
                self.display_message(f"You: {user_message}")
                try:
                    sio.send(user_message)
                except Exception as e:
                    self.display_message(f"Error sending message: {e}")
            except sr.UnknownValueError:
                self.display_message("🎤 Bot: Couldn't understand. Please try again.")
            except sr.RequestError as e:
                self.display_message(f"🎤 Bot: Error connecting to service ({e})")
            except Exception as e:
                self.display_message(f"🎤 Bot: Error ({e})")

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def typing_effect(self, message):
        self.chat_area.config(state='normal')
        for char in message:
            self.chat_area.insert(tk.END, char)
            self.chat_area.see(tk.END)
            self.chat_area.update()
            time.sleep(0.05)
        self.chat_area.insert(tk.END, "\n")
        self.chat_area.config(state='disabled')

        # Chỉ đọc tin nhắn của bot nếu TTS được bật
        if self.tts_enabled and message.startswith("Bot:"):
            bot_response = message[5:]
            self.engine.say(bot_response)
            self.engine.runAndWait()

    def close_connection(self):
        sio.disconnect()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", client.close_connection)
    root.mainloop()
