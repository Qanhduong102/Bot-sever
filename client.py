import tkinter as tk
from tkinter import scrolledtext
import socketio
import pyttsx3
import speech_recognition as sr
import sys
import io
import time
import threading
from PIL import Image, ImageTk
import webbrowser
from socketIO_client import SocketIO

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
        self.conversation_count = 0  # Biến đếm số cuộc hội thoại đã tạo
        self.conversations = []  # Danh sách lưu trữ các cuộc hội thoại
        self.current_conversation = []  # Cuộc hội thoại hiện tại
        self.is_connected = False  # Biến theo dõi kết nối
        self.current_conversation_index = None  # Ban đầu không có cuộc hội thoại nào được chọn
        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', height=20, width=60,
            bg='#2c2c3e', fg="#f0f0f0", font=('Roboto', 12),
            bd=0, highlightthickness=1, highlightbackground="#4CAF50"
        )
        self.chat_area.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Tải ảnh avatar
        avatar_image = Image.open("avatar.png")  # Đường dẫn đến ảnh avatar
        avatar_image = avatar_image.resize((50, 50), Image.Resampling.LANCZOS)  # Resize ảnh
        self.avatar_photo = ImageTk.PhotoImage(avatar_image)

        # Tạo widget Label hiển thị avatar
        self.avatar_label = tk.Label(
            root, image=self.avatar_photo, bg="#1e1e2f"
    )
        self.avatar_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")  # Đặt ở góc trái trên cùng

        # Tiêu đề (đẩy sang bên cạnh avatar)
        self.header = tk.Label(
        root, text="🎨 J.A.R.V.I.S 🎤",
        font=("Montserrat", 16, "bold"),
        fg="#ffffff", bg="#1e1e2f"
    )
        self.header.grid(row=0, column=0, columnspan=2, pady=(10, 0), sticky="n")

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

        # **Dòng bind phải nằm sau khi self.conversation_listbox được khởi tạo**
        self.conversation_listbox.bind("<<ListboxSelect>>", self.on_conversation_select)

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
    def get_next_conversation_number(self):
        """Lấy số thứ tự cuộc hội thoại tiếp theo dựa trên các cuộc hội thoại còn tồn tại."""
        # Kiểm tra các cuộc hội thoại hiện tại và tìm số thứ tự nhỏ nhất bị thiếu
        existing_numbers = [int(conv.split()[1]) for conv in self.conversation_listbox.get(0, tk.END)]
        next_number = 1  # Bắt đầu từ 1

        # Tìm số thứ tự tiếp theo mà chưa được sử dụng
        while next_number in existing_numbers:
            next_number += 1

        return next_number

    def new_conversation(self):
        """Tạo cuộc hội thoại mới và làm mới nội dung khung chat."""
        # Lấy số thứ tự cuộc hội thoại tiếp theo
        next_conversation_number = self.get_next_conversation_number()

        # Nếu có cuộc hội thoại hiện tại, lưu nội dung vào danh sách
        if self.current_conversation_index is not None:
            self.conversations[self.current_conversation_index] = self.chat_area.get("1.0", tk.END).strip().split("\n")

        # Tạo cuộc hội thoại mới
        conversation_name = f"Conversation {next_conversation_number}"
        self.conversations.append([])  # Thêm một danh sách trống cho cuộc hội thoại mới
        self.conversation_listbox.insert(tk.END, conversation_name)  # Hiển thị trong Listbox

        # Chuyển sang cuộc hội thoại mới
        self.current_conversation_index = len(self.conversations) - 1

        # Làm mới khung chat
        self.chat_area.config(state='normal')
        self.chat_area.delete("1.0", tk.END)  # Xóa nội dung cũ
        self.chat_area.insert(tk.END, "🆕 New conversation started. How can I assist you?\n")
        self.chat_area.config(state='disabled')  # Không cho chỉnh sửa trực tiếp
        self.chat_area.yview(tk.END)  # Cuộn xuống cuối cùng

        # Giữ kết nối server (nếu bị ngắt, thì kết nối lại)
        if not self.is_connected:
            self.connect_to_server()

        # Tắt tính năng TTS nếu đang bật
        self.tts_enabled = False

        # Đảm bảo giao diện phản ánh trạng thái mới
        self.chat_area.yview(tk.END)  # Cuộn xuống cuối cùng

    def delete_conversation(self):
        """Xóa cuộc hội thoại đã chọn khỏi Listbox và danh sách."""
        try:
            selected_index = self.conversation_listbox.curselection()
            if not selected_index:
                return  # Không có cuộc hội thoại nào được chọn

            selected_index = selected_index[0]

            # Xóa cuộc hội thoại khỏi danh sách
            del self.conversations[selected_index]
            self.conversation_listbox.delete(selected_index)

            # Cập nhật chỉ mục cuộc hội thoại hiện tại
            if len(self.conversations) == 0:
                self.current_conversation_index = None  # Không còn cuộc hội thoại nào
                self.chat_area.config(state='normal')
                self.chat_area.delete("1.0", tk.END)  # Làm trống khung chat
                self.chat_area.config(state='disabled')
            else:
                # Chuyển sang cuộc hội thoại đầu tiên trong danh sách (nếu còn)
                self.current_conversation_index = 0
                self.on_conversation_select(None)

        except Exception as e:
            print(f"Error deleting conversation: {e}")

    def refresh_conversations(self):
        """Cập nhật lại danh sách các cuộc hội thoại trong Listbox."""
        self.conversation_listbox.delete(0, tk.END)  # Xóa hết các mục cũ
        for conv in self.conversations:
            # Thêm vào danh sách với tên cuộc hội thoại
            self.conversation_listbox.insert(tk.END, f"Conversation {self.get_next_conversation_number()}")


    def display_conversation(self, index):
        """Hiển thị nội dung hội thoại được chọn."""
        if 0 <= index < len(self.conversations):
            self.current_conversation = self.conversations[index]
            self.chat_area.config(state='normal')
            self.chat_area.delete("1.0", tk.END)
            for message in self.current_conversation:
                self.chat_area.insert(tk.END, f"{message}\n")
            self.chat_area.config(state='disabled')
        else:
            self.chat_area.config(state='normal')
            self.chat_area.delete("1.0", tk.END)
            self.chat_area.insert(tk.END, "No conversation selected.\n")
            self.chat_area.config(state='disabled')

    def on_conversation_select(self, event):
        """Xử lý khi người dùng chọn một cuộc hội thoại từ Listbox."""
        # Lấy chỉ mục cuộc hội thoại được chọn
        selected_index = self.conversation_listbox.curselection()
        if not selected_index:
            return  # Không có cuộc hội thoại nào được chọn

        selected_index = selected_index[0]

        # Lưu nội dung cuộc hội thoại hiện tại trước khi chuyển
        if self.current_conversation_index is not None:
            self.conversations[self.current_conversation_index] = self.chat_area.get("1.0", tk.END).strip().split("\n")

        # Cập nhật chỉ mục cuộc hội thoại hiện tại
        self.current_conversation_index = selected_index

        # Làm mới khung chat với nội dung của cuộc hội thoại được chọn
        self.chat_area.config(state='normal')
        self.chat_area.delete("1.0", tk.END)  # Xóa nội dung cũ
        conversation_content = self.conversations[self.current_conversation_index]
        for line in conversation_content:
            self.chat_area.insert(tk.END, line + "\n")
        self.chat_area.config(state='disabled')  # Không cho chỉnh sửa trực tiếp
        self.chat_area.yview(tk.END)  # Cuộn xuống cuối cùng


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
            self.display_message("Jarvis: Connected to server.")

        @sio.event
        def disconnect():
            print("Ngắt kết nối từ server!")
            self.display_message("Jarvis: Disconnected from server.")

        @sio.on('message')
        def on_message(data):
            print(f"Phản hồi từ server: {data}")
            self.typing_effect(f"Jarvis: {data}")

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
                self.display_message("🎤 Jarvis: Listening...")
                audio = recognizer.listen(source, timeout=5)
                user_message = recognizer.recognize_google(audio, language="en-US")
                self.display_message(f"You: {user_message}")
                try:
                    sio.send(user_message)
                except Exception as e:
                    self.display_message(f"Error sending message: {e}")
            except sr.UnknownValueError:
                self.display_message("🎤 Jarvis: Couldn't understand. Please try again.")
            except sr.RequestError as e:
                self.display_message(f"🎤 Jarvis: Error connecting to service ({e})")
            except Exception as e:
                self.display_message(f"🎤 Jarvis: Error ({e})")

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
            if self.tts_enabled and message.startswith("Jarvis:"):
                bot_response = message[5:]  # Bỏ phần "Jarvis: " để đọc nội dung
                self.engine.say(bot_response)
                self.engine.runAndWait()

        # Tạo và chạy hai luồng đồng thời
        typing_thread = threading.Thread(target=type_text)
        tts_thread = threading.Thread(target=speak_text)

        typing_thread.start()
        tts_thread.start()
    # Kết nối với máy chủ
    def on_message_received(*args):
        message = args[0]
    
        if message == "open_youtube":
            webbrowser.open("https://www.youtube.com", new=2)
        elif message == "open_facebook":
            webbrowser.open("https://www.facebook.com", new=2)
        elif message.startswith("search_google"):
            query = message.replace("search_google", "").strip()
            search_url = f"https://www.google.com/search?q={query}"
            webbrowser.open(search_url, new=2)
        else:
            print("Received message:", message)

    # Kết nối với máy chủ WebSocket
    with SocketIO('127.0.0.1', 12345) as socketIO:
        socketIO.on('message', on_message_received)
        socketIO.wait()  # Đợi sự kiện
    def close_connection(self):
        sio.disconnect()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", client.close_connection)
    root.mainloop()
