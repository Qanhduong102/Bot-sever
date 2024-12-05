import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
import hashlib
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import json
DATABASE_NAME = "users.db"  # Tên cơ sở dữ liệu SQLite

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Đăng nhập/Đăng ký & Chatbot")
        self.root.geometry("800x600")  # Kích thước cửa sổ
        self.root.resizable(False, False)

        # Màu nền
        self.bg_color = "#1e1e2f"
        self.panel_color = "#2c2c3e"
        self.highlight_color = "#4CAF50"
        self.text_color = "#f0f0f0"

        # Khởi tạo cơ sở dữ liệu
        self.init_database()

        # Khởi tạo các frame
        self.login_frame = None
        self.register_frame = None
        self.chat_frame = None

        # Hiển thị frame đăng nhập đầu tiên
        self.create_login_frame()

    def init_database(self):
        """Khởi tạo cơ sở dữ liệu SQLite."""
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        # Tạo bảng nếu chưa tồn tại
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Hàm băm mật khẩu."""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_login_frame(self):
        if self.register_frame:
            self.register_frame.destroy()
        if self.chat_frame:
            self.chat_frame.destroy()

        self.login_frame = tk.Frame(self.root, bg=self.panel_color)
        self.login_frame.pack(expand=True, fill="both")

        tk.Label(
            self.login_frame, text="Đăng nhập", font=("Arial", 24, "bold"),
            bg=self.panel_color, fg=self.text_color
        ).pack(pady=(50, 20))  # Tăng khoảng cách phía trên

        tk.Label(
            self.login_frame, text="Email:", font=("Arial", 14),
            bg=self.panel_color, fg=self.text_color
        ).pack(anchor="w", padx=150, pady=(10, 5))  # Căn lề trái và khoảng cách nhỏ hơn
        self.email_entry = tk.Entry(self.login_frame, width=40, font=("Arial", 14))
        self.email_entry.pack(padx=150, pady=(0, 10))

        tk.Label(
            self.login_frame, text="Mật khẩu:", font=("Arial", 14),
            bg=self.panel_color, fg=self.text_color
        ).pack(anchor="w", padx=150, pady=(10, 5))
        self.password_entry = tk.Entry(self.login_frame, show="*", width=40, font=("Arial", 14))
        self.password_entry.pack(padx=150, pady=(0, 20))

        tk.Button(
            self.login_frame, text="Đăng nhập", command=self.login,
            bg=self.highlight_color, fg="white", font=("Arial", 14, "bold"),
            relief="flat", cursor="hand2", width=20, height=2
        ).pack(pady=(10, 20))

        tk.Button(
            self.login_frame, text="Chưa có tài khoản? Đăng ký", command=self.create_register_frame,
            bg="#6C63FF", fg="white", font=("Arial", 12, "bold"),
            relief="flat", cursor="hand2", width=25, height=2, wraplength=250
        ).pack(pady=(10, 20))

    def create_register_frame(self):
        if self.login_frame:
            self.login_frame.destroy()
        if self.chat_frame:
            self.chat_frame.destroy()

        self.register_frame = tk.Frame(self.root, bg=self.panel_color)
        self.register_frame.pack(expand=True, fill="both")

        tk.Label(
            self.register_frame, text="Đăng ký", font=("Arial", 24, "bold"),
            bg=self.panel_color, fg=self.text_color
        ).pack(pady=(50, 20))

        tk.Label(
            self.register_frame, text="Email:", font=("Arial", 14),
            bg=self.panel_color, fg=self.text_color
        ).pack(anchor="w", padx=150, pady=(10, 5))
        self.reg_email_entry = tk.Entry(self.register_frame, width=40, font=("Arial", 14))
        self.reg_email_entry.pack(padx=150, pady=(0, 10))

        tk.Label(
            self.register_frame, text="Mật khẩu:", font=("Arial", 14),
            bg=self.panel_color, fg=self.text_color
        ).pack(anchor="w", padx=150, pady=(10, 5))
        self.reg_password_entry = tk.Entry(self.register_frame, show="*", width=40, font=("Arial", 14))
        self.reg_password_entry.pack(padx=150, pady=(0, 10))

        tk.Label(
            self.register_frame, text="Xác nhận mật khẩu:", font=("Arial", 14),
            bg=self.panel_color, fg=self.text_color
        ).pack(anchor="w", padx=150, pady=(10, 5))
        self.reg_confirm_entry = tk.Entry(self.register_frame, show="*", width=40, font=("Arial", 14))
        self.reg_confirm_entry.pack(padx=150, pady=(0, 20))

        tk.Button(
            self.register_frame, text="Hoàn tất", command=self.register,
            bg=self.highlight_color, fg="white", font=("Arial", 14, "bold"),
            relief="flat", cursor="hand2", width=20, height=2
        ).pack(pady=(10, 20))

        tk.Button(
            self.register_frame, text="Quay lại", command=self.create_login_frame,
            bg="#6C63FF", fg="white", font=("Arial", 12, "bold"),
            relief="flat", cursor="hand2", width=20, height=2
        ).pack()

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        hashed_password = self.hash_password(password)

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
        user = cursor.fetchone()

        conn.close()

        if user:
            messagebox.showinfo("Thành công", "Đăng nhập thành công!")
            with open("current_user.json", "w") as f:
                json.dump({"email": email}, f)
        
            # Đóng cửa sổ đăng nhập và mở client.py
            self.root.quit()  # Đóng cửa sổ Tkinter hiện tại
            subprocess.Popen(["python", "client.py"])  # Chạy client.py
        
        else:
            messagebox.showerror("Lỗi", "Thông tin đăng nhập không đúng!")

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

        hashed_password = self.hash_password(password)

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
            conn.commit()
            messagebox.showinfo("Thành công", "Đăng ký thành công!")
            self.create_login_frame()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Email đã tồn tại!")
        finally:
            conn.close()
    def forgot_password(self):
        email = self.email_entry.get()

        if not email:
            messagebox.showerror("Lỗi", "Vui lòng nhập email để lấy lại mật khẩu!")
            return

        # Tạo mật khẩu tạm thời
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Băm mật khẩu tạm thời
        hashed_password = self.hash_password(temp_password)

        # Cập nhật lại mật khẩu trong cơ sở dữ liệu
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
            conn.commit()
            conn.close()

            # Gửi email với mật khẩu mới
            self.send_reset_email(email, temp_password)

            messagebox.showinfo("Thành công", "Mật khẩu mới đã được gửi đến email của bạn!")
        else:
            conn.close()
            messagebox.showerror("Lỗi", "Email không tồn tại trong hệ thống!")

    def create_chat_frame(self):
        if self.login_frame:
            self.login_frame.destroy()
        if self.register_frame:
            self.register_frame.destroy()

        self.chat_frame = tk.Frame(self.root, bg=self.bg_color)
        self.chat_frame.pack(expand=True, fill="both")

        self.chat_area = scrolledtext.ScrolledText(
            self.chat_frame, wrap=tk.WORD, state='disabled',
            bg=self.panel_color, fg=self.text_color, font=("Arial", 12),
            bd=0, highlightthickness=1, highlightbackground=self.highlight_color
        )
        self.chat_area.pack(padx=10, pady=10, fill="both", expand=True)

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
            self.chat_area.yview("end")
            self.chat_area.config(state="disabled")
            self.entry.delete(0, "end")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)

    # Lấy kích thước màn hình
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Kích thước cửa sổ
    window_width = 800
    window_height = 600

    # Tính toán tọa độ x, y để căn giữa
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    # Thiết lập vị trí cửa sổ
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.mainloop()
