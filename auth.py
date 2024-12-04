import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
from PIL import Image, ImageTk
import pyttsx3
import speech_recognition as sr

SERVER_URL = "https://bot-sever-1-m5e4.onrender.com"  # Địa chỉ WebSocket server

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Đăng nhập/Đăng ký & Chatbot")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Màu nền
        self.bg_color = "#1e1e2f"
        self.panel_color = "#2c2c3e"
        self.highlight_color = "#4CAF50"
        self.text_color = "#f0f0f0"

        # Khởi tạo các frame
        self.login_frame = None
        self.register_frame = None
        self.chat_frame = None

        # Hiển thị frame đăng nhập đầu tiên
        self.create_login_frame()

    def create_login_frame(self):
        if self.chat_frame:
            self.chat_frame.pack_forget()
        self.login_frame = tk.Frame(self.root, bg=self.panel_color)
        self.login_frame.pack(expand=True, fill="both")

        # Tiêu đề
        tk.Label(
            self.login_frame, text="Đăng nhập", font=("Arial", 20, "bold"),
            bg=self.panel_color, fg=self.text_color
        ).pack(pady=20)

        # Email
        tk.Label(
            self.login_frame, text="Email:", font=("Arial", 12),
            bg=self.panel_color, fg=self.text_color
        ).pack(anchor="w", padx=50)
        self.email_entry = tk.Entry(self.login_frame, width=30, font=("Arial", 12))
        self.email_entry.pack(padx=50, pady=5)

        # Mật khẩu
        tk.Label(
            self.login_frame, text="Mật khẩu:", font=("Arial", 12),
            bg=self.panel_color, fg=self.text_color
        ).pack(anchor="w", padx=50)
        self.password_entry = tk.Entry(self.login_frame, show="*", width=30, font=("Arial", 12))
        self.password_entry.pack(padx=50, pady=5)

        # Nút đăng nhập
        tk.Button(
            self.login_frame, text="Đăng nhập", command=self.login,
            bg=self.highlight_color, fg="white", font=("Arial", 12, "bold"),
            relief="flat", cursor="hand2"
        ).pack(pady=15)

        # Chuyển đến đăng ký
        tk.Button(
            self.login_frame, text="Chưa có tài khoản? Đăng ký", command=self.create_register_frame,
            bg="#6C63FF", fg="white", font=("Arial", 12, "bold"),
            relief="flat", cursor="hand2"
        ).pack()

    def create_register_frame(self):
        self.login_frame.pack_forget()
        self.register_frame = tk.Frame(self.root, bg=self.panel_color)
        self.register_frame.pack(expand=True, fill="both")

        # Tiêu đề
        tk.Label(
            self.register_frame, text="Đăng ký", font=("Arial", 20, "bold"),
            bg=self.panel_color, fg=self.text_color
        ).pack(pady=20)

        # Email
        tk.Label(
            self.register_frame, text="Email:", font=("Arial", 12),
            bg=self.panel_color, fg=self.text_color
        ).pack(anchor="w", padx=50)
        self.reg_email_entry = tk.Entry(self.register_frame, width=30, font=("Arial", 12))
        self.reg_email_entry.pack(padx=50, pady=5)

        # Mật khẩu
        tk.Label(
            self.register_frame, text="Mật khẩu:", font=("Arial", 12),
            bg=self.panel_color, fg=self.text_color
        ).pack(anchor="w", padx=50)
        self.reg_password_entry = tk.Entry(self.register_frame, show="*", width=30, font=("Arial", 12))
        self.reg_password_entry.pack(padx=50, pady=5)

        # Xác nhận mật khẩu
        tk.Label(
            self.register_frame, text="Xác nhận mật khẩu:", font=("Arial", 12),
            bg=self.panel_color, fg=self.text_color
        ).pack(anchor="w", padx=50)
        self.reg_confirm_entry = tk.Entry(self.register_frame, show="*", width=30, font=("Arial", 12))
        self.reg_confirm_entry.pack(padx=50, pady=5)

        # Nút hoàn tất
        tk.Button(
            self.register_frame, text="Hoàn tất", command=self.register,
            bg=self.highlight_color, fg="white", font=("Arial", 12, "bold"),
            relief="flat", cursor="hand2"
        ).pack(pady=15)

        # Quay lại
        tk.Button(
            self.register_frame, text="Quay lại", command=self.create_login_frame,
            bg="#6C63FF", fg="white", font=("Arial", 12, "bold"),
            relief="flat", cursor="hand2"
        ).pack()

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        # Gửi yêu cầu đăng nhập
        try:
            response = requests.post(f"{SERVER_URL}/login", json={"email": email, "password": password})
            if response.status_code == 200:
                messagebox.showinfo("Thành công", "Đăng nhập thành công!")
                self.create_chat_frame()
            else:
                messagebox.showerror("Lỗi", response.json().get("message", "Đăng nhập thất bại!"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Lỗi", "Không thể kết nối đến server!")

    def register(self):
        email = self.reg_email_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_entry.get()

        if not email or not password or not confirm_password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        if password != confirm_password:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        # Gửi yêu cầu đăng ký
        try:
            response = requests.post(f"{SERVER_URL}/register", json={"email": email, "password": password})
            if response.status_code == 201:
                messagebox.showinfo("Thành công", "Đăng ký thành công!")
                self.create_login_frame()
            else:
                messagebox.showerror("Lỗi", response.json().get("message", "Đăng ký thất bại!"))
        except requests.exceptions.RequestException:
            messagebox.showerror("Lỗi", "Không thể kết nối đến server!")

    def create_chat_frame(self):
        if self.login_frame:
            self.login_frame.pack_forget()
        if self.register_frame:
            self.register_frame.pack_forget()
        self.chat_frame = tk.Frame(self.root, bg=self.bg_color)
        self.chat_frame.pack(expand=True, fill="both")

        # Khung chat
        self.chat_area = scrolledtext.ScrolledText(
            self.chat_frame, wrap=tk.WORD, state='disabled',
            bg=self.panel_color, fg=self.text_color, font=("Arial", 12),
            bd=0, highlightthickness=1, highlightbackground=self.highlight_color
        )
        self.chat_area.pack(padx=10, pady=10, fill="both", expand=True)

        # Khung nhập tin nhắn
        bottom_panel = tk.Frame(self.chat_frame, bg=self.bg_color)
        bottom_panel.pack(fill="x", padx=10, pady=10)

        self.entry = tk.Entry(
            bottom_panel, width=60, font=("Arial", 12),
            bg=self.panel_color, fg=self.text_color, insertbackground=self.text_color,
            bd=0, highlightthickness=1, highlightbackground=self.highlight_color
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Button(
            bottom_panel, text="Gửi", command=self.send_message,
            bg=self.highlight_color, fg="white", font=("Arial", 12, "bold"),
            relief="flat", cursor="hand2"
        ).pack(side="left")

    def send_message(self):
        message = self.entry.get()
        if message:
            self.chat_area.config(state="normal")
            self.chat_area.insert("end", f"Bạn: {message}\n")
            self.chat_area.config(state="disabled")
            self.entry.delete(0, "end")
            # Xử lý gửi tin nhắn đến server hoặc AI tại đây


root = tk.Tk()
app = ChatApp(root)
root.mainloop()
