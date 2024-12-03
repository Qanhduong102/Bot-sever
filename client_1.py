import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import pyttsx3


HOST = '127.0.0.1'
PORT = 12345


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot Client")
        self.root.geometry("600x600")
        self.root.configure(bg="#1e1e2f")  # Màu nền hiện đại

        # Header
        self.header = tk.Label(
            root, text="🎨 Chatbot Client 🎤",
            font=("Montserrat", 16, "bold"),
            fg="#ffffff", bg="#1e1e2f"
        )
        self.header.grid(row=0, column=0, columnspan=3, pady=(10, 0))

        # Khu vực hiển thị tin nhắn
        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', height=20, width=50,
            bg='#2c2c3e', fg="#f0f0f0", font=('Roboto', 12),
            bd=0, highlightthickness=1, highlightbackground="#4CAF50"
        )
        self.chat_area.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Entry và nút bấm
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

        # Kết nối server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((HOST, PORT))
            print("Connected to the server.")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.display_message(f"Error connecting to server: {e}")

        # TTS
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        # Nhận tin nhắn từ server
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self):
        user_message = self.entry.get()
        if user_message.strip():
            self.display_message(f"You: {user_message}")
            try:
                self.client_socket.send(user_message.encode('utf-8'))
            except Exception as e:
                self.display_message(f"Error sending message: {e}")
            self.entry.delete(0, tk.END)

    def speak_message(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                self.display_message("🎤 Bot: Listening...")
                audio = recognizer.listen(source, timeout=5)
                user_message = recognizer.recognize_google(audio, language="en-US")
                self.display_message(f"You: {user_message}")
                try:
                    self.client_socket.send(user_message.encode('utf-8'))
                except Exception as e:
                    self.display_message(f"Error sending message: {e}")
            except sr.UnknownValueError:
                self.display_message("🎤 Bot: Couldn't understand. Please try again.")
            except sr.RequestError as e:
                self.display_message(f"🎤 Bot: Error connecting to service ({e})")
            except Exception as e:
                self.display_message(f"🎤 Bot: Error ({e})")

    def receive_messages(self):
        while True:
            try:
                response = self.client_socket.recv(1024).decode('utf-8')
                if response:
                    self.display_message(response)
                    self.engine.say(response)
                    self.engine.runAndWait()
                else:
                    self.display_message("Bot: No response received.")
            except Exception as e:
                self.display_message(f"Bot: Error receiving message: {e}")
                break

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
