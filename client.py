import tkinter as tk
from tkinter import scrolledtext
import socketio
import pyttsx3
import speech_recognition as sr
import sys
import io
import time
import threading

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
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e2f")
        self.center_window(800, 600)
        self.conversations = []  # Danh sách lưu trữ các cuộc hội thoại
        self.current_conversation = []  # Cuộc hội thoại hiện tại
        self.is_connected = False  # Biến theo dõi kết nối
        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', height=20, width=60,
            bg='#2c2c3e', fg="#f0f0f0", font=('Roboto', 12),
            bd=0, highlightthickness=1, highlightbackground="#4CAF50"
        )
        self.chat_area.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Tiêu đề
        self.header = tk.Label(
            root, text="🎨 Voice-Chat Bot 🎤",
            font=("Montserrat", 16, "bold"),
            fg="#ffffff", bg="#1e1e2f"
        )
        self.header.grid(row=0, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        # Khung bên trái cho các nút quản lý hội thoại
        self.left_panel = tk.Frame(
            root, width=150, bg="#2c2c3e", highlightthickness=1, highlightbackground="#4CAF50"
        )
        self.left_panel.grid(row=1, column=0, rowspan=2, padx=10, pady=10, sticky="ns")

        # Listbox để hiển thị các cuộc hội thoại
        self.conversation_listbox = tk.Listbox(
            self.left_panel, bg="#2c2c3e", fg="#f0f0f0", font=("Roboto", 12),
            bd=0, selectbackground="#4CAF50", highlightthickness=1, highlightbackground="#4CAF50",
            height=15
        )
        self.conversation_listbox.pack(padx=10, pady=10, fill="y")

        # Tạo khung chứa các nút
        self.button_frame = tk.Frame(
            self.left_panel, bg="#2c2c3e", highlightthickness=1, highlightbackground="#4CAF50", padx=10, pady=10
        )
        self.button_frame.pack(side="bottom", pady=(10, 0), fill="x")  # Đặt ở dưới cùng và căng ngang

        # Nút New Conversation
        self.new_conv_button = tk.Button(
            self.button_frame, text="New Conversation",
            command=self.new_conversation,
            bg="#4CAF50", fg="white", font=("Roboto", 10, "bold"),
            relief="flat", activebackground="#45a049", activeforeground="white",
            cursor="hand2"
        )
        self.new_conv_button.pack(pady=(10, 5), padx=10, fill="x")

        # Nút Delete Conversation
        self.delete_conv_button = tk.Button(
            self.button_frame, text="Delete Conversation",
            command=self.delete_conversation,
            bg="#F44336", fg="white", font=("Roboto", 10, "bold"),
            relief="flat", activebackground="#D32F2F", activeforeground="white",
            cursor="hand2"
        )
        self.delete_conv_button.pack(pady=(5, 10), padx=10, fill="x")

        # Khung hiển thị hội thoại (Lịch sử hội thoại)
        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', height=20, width=60,
            bg='#2c2c3e', fg="#f0f0f0", font=('Roboto', 12),
            bd=0, highlightthickness=1, highlightbackground="#4CAF50"
        )
        self.chat_area.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Khung nhập tin nhắn và nút gửi
        self.bottom_panel = tk.Frame(root, bg="#1e1e2f")
        self.bottom_panel.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.entry = tk.Entry(
            self.bottom_panel, width=40, font=('Roboto', 12),
            bg="#2c2c3e", fg="#ffffff", insertbackground="#ffffff",
            bd=0, highlightthickness=1, highlightbackground="#4CAF50"
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = tk.Button(
            self.bottom_panel, text="Send",
            command=self.send_message,
            bg='#4CAF50', fg='white', font=('Roboto', 12, 'bold'),
            relief='flat', activebackground="#45a049", activeforeground="white",
            cursor="hand2"
        )
        self.send_button.pack(side="left", padx=(0, 10))

        self.voice_button = tk.Button(
            self.bottom_panel, text="🎤 Speak",
            command=self.speak_message,
            bg='#2196F3', fg='white', font=('Roboto', 12, 'bold'),
            relief='flat', activebackground="#1976D2", activeforeground="white",
            cursor="hand2"
        )
        self.voice_button.pack(side="left")

        # Thiết lập engine TTS
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.tts_enabled = False

        # Danh sách lưu trữ lịch sử hội thoại
        self.conversations = []
        self.current_conversation = []

        self.connect_to_server()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def new_conversation(self):
        """Xử lý bắt đầu hội thoại mới và lưu lại hội thoại hiện tại."""
        if self.current_conversation:
            # Lưu lại cuộc hội thoại hiện tại vào danh sách các cuộc hội thoại
            self.conversations.append(self.current_conversation)

        # Tạo tên cuộc hội thoại mới
        conversation_name = f"Conversation {len(self.conversations) + 1}"

        # Cập nhật danh sách cuộc hội thoại trong khung bên trái mà không xóa các cuộc hội thoại cũ
        self.conversation_listbox.insert(tk.END, conversation_name)

        # Tạo cuộc hội thoại mới
        self.current_conversation = []  # Xóa danh sách cuộc hội thoại hiện tại

        # Cập nhật giao diện: Xóa lịch sử hội thoại hiện tại và thông báo người dùng
        self.chat_area.config(state='normal')
        self.chat_area.delete("1.0", tk.END)  # Xóa nội dung cũ
        self.chat_area.insert(tk.END, "New conversation started. How can I assist you?\n")
        self.chat_area.config(state='disabled')

        # Dừng việc nhận diện giọng nói trước đó và sẵn sàng cho cuộc hội thoại mới
        self.tts_enabled = False
        self.engine.say("Starting a new conversation. How can I assist you?")
        self.engine.runAndWait()

        # Ngắt kết nối cũ (nếu có) và kết nối lại
        self.disconnect_from_server()  # Ngắt kết nối trước nếu đang kết nối
        self.connect_to_server()  # Kết nối lại cho cuộc hội thoại mới

    def delete_conversation(self):
        """Xử lý xóa hội thoại hiện tại."""
        if self.conversations:
            # Xóa hội thoại hiện tại khỏi danh sách các cuộc hội thoại
            self.conversations.pop()

            # Cập nhật lại danh sách các cuộc hội thoại trên giao diện
            self.conversation_listbox.delete(tk.END)  # Xóa cuộc hội thoại đã xóa

            # Cập nhật nội dung hội thoại trên giao diện
            self.chat_area.config(state='normal')
            self.chat_area.delete("1.0", tk.END)  # Xóa nội dung hiện tại
            self.chat_area.insert(tk.END, "Conversation deleted.\n")
            self.chat_area.config(state='disabled')

            # Nếu không còn cuộc hội thoại nào, khôi phục lại giao diện như lúc ban đầu
        if not self.conversations:
            self.chat_area.config(state='normal')
            self.chat_area.delete("1.0", tk.END)
            self.chat_area.insert(tk.END, "No conversations available.\n")
            self.chat_area.config(state='disabled')

    def on_conversation_select(self, event):
        """Xử lý khi người dùng chọn cuộc hội thoại trong danh sách."""
        selection = self.conversation_listbox.curselection()
        if selection:
            conversation_index = selection[0]  # Lấy index của cuộc hội thoại được chọn
            self.display_conversation(conversation_index)  # Hiển thị cuộc hội thoại đó

    def connect_to_server(self):
        """Kết nối tới server (giả sử là server chat)."""
        try:
            # Logic kết nối tới server
            self.is_connected = True
        except Exception as e:
            print(f"Error connecting to server: {e}")

    def disconnect_from_server(self):
        """Ngắt kết nối khỏi server (nếu có)."""
        self.is_connected = False

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
            print(f": {e}")
            self.display_message(f"{e}")

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
        def type_text():
            self.chat_area.config(state='normal')
            for char in message:
                self.chat_area.insert(tk.END, char)
                self.chat_area.see(tk.END)
                self.chat_area.update()
                time.sleep(0.05)  # Hiệu ứng gõ
            self.chat_area.insert(tk.END, "\n")
            self.chat_area.config(state='disabled')

        def speak_text():
            if self.tts_enabled and message.startswith("Bot:"):
                bot_response = message[5:]  # Bỏ phần "Bot: " để đọc nội dung
                self.engine.say(bot_response)
                self.engine.runAndWait()

        # Tạo và chạy hai luồng đồng thời
        typing_thread = threading.Thread(target=type_text)
        tts_thread = threading.Thread(target=speak_text)

        typing_thread.start()
        tts_thread.start()

    def close_connection(self):
        sio.disconnect()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", client.close_connection)
    root.mainloop()
