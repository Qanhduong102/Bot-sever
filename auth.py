import tkinter as tk
from tkinter import messagebox
import socketio
import re

# Khởi tạo client WebSocket
sio = socketio.Client()

# Địa chỉ server WebSocket (có thể thay đổi)
SERVER_URL = "https://bot-sever-1-m5e4.onrender.com"

class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Authentication")
        self.root.geometry("400x400")
        self.root.configure(bg="#1e1e2f")

        # Tạo các widget giao diện
        self.header = tk.Label(
            root, text="Authentication", font=("Montserrat", 16, "bold"), fg="#ffffff", bg="#1e1e2f"
        )
        self.header.pack(pady=10)

        # Đăng ký, Đăng nhập, Quên mật khẩu button
        self.register_button = tk.Button(
            root, text="Register", command=self.show_register_form,
            bg="#4CAF50", fg="white", font=("Roboto", 12, "bold"),
            relief="flat", activebackground="#45a049", activeforeground="white",
            cursor="hand2"
        )
        self.register_button.pack(pady=5)

        self.login_button = tk.Button(
            root, text="Login", command=self.show_login_form,
            bg="#2196F3", fg="white", font=("Roboto", 12, "bold"),
            relief="flat", activebackground="#1976D2", activeforeground="white",
            cursor="hand2"
        )
        self.login_button.pack(pady=5)

        self.forgot_button = tk.Button(
            root, text="Forgot Password", command=self.show_forgot_password_form,
            bg="#F44336", fg="white", font=("Roboto", 12, "bold"),
            relief="flat", activebackground="#D32F2F", activeforeground="white",
            cursor="hand2"
        )
        self.forgot_button.pack(pady=5)

    def show_register_form(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("400x400")

        self.username_label = tk.Label(register_window, text="Username", fg="white", bg="#1e1e2f")
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(register_window)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(register_window, text="Password", fg="white", bg="#1e1e2f")
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(register_window, show="*")
        self.password_entry.pack(pady=5)

        self.register_button = tk.Button(
            register_window, text="Register", command=self.register_user,
            bg="#4CAF50", fg="white", font=("Roboto", 12, "bold"),
            relief="flat", activebackground="#45a049", activeforeground="white",
            cursor="hand2"
        )
        self.register_button.pack(pady=20)

    def show_login_form(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")
        login_window.geometry("400x400")

        self.username_label = tk.Label(login_window, text="Username", fg="white", bg="#1e1e2f")
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(login_window)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(login_window, text="Password", fg="white", bg="#1e1e2f")
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(login_window, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = tk.Button(
            login_window, text="Login", command=self.login_user,
            bg="#2196F3", fg="white", font=("Roboto", 12, "bold"),
            relief="flat", activebackground="#1976D2", activeforeground="white",
            cursor="hand2"
        )
        self.login_button.pack(pady=20)

    def show_forgot_password_form(self):
        forgot_window = tk.Toplevel(self.root)
        forgot_window.title("Forgot Password")
        forgot_window.geometry("400x400")

        self.email_label = tk.Label(forgot_window, text="Email", fg="white", bg="#1e1e2f")
        self.email_label.pack(pady=5)
        self.email_entry = tk.Entry(forgot_window)
        self.email_entry.pack(pady=5)

        self.reset_button = tk.Button(
            forgot_window, text="Reset Password", command=self.reset_password,
            bg="#F44336", fg="white", font=("Roboto", 12, "bold"),
            relief="flat", activebackground="#D32F2F", activeforeground="white",
            cursor="hand2"
        )
        self.reset_button.pack(pady=20)

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            # Gửi yêu cầu đăng ký lên server
            sio.emit("register", {"username": username, "password": password})
            messagebox.showinfo("Success", "Registration successful!")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            # Gửi yêu cầu đăng nhập lên server
            sio.emit("login", {"username": username, "password": password})
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def reset_password(self):
        email = self.email_entry.get()

        if email and self.is_valid_email(email):
            # Gửi yêu cầu reset mật khẩu lên server
            sio.emit("reset_password", {"email": email})
            messagebox.showinfo("Success", "Password reset email sent!")
        else:
            messagebox.showerror("Error", "Please provide a valid email address.")

    def is_valid_email(self, email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email)

# Kết nối đến server khi chạy
sio.connect(SERVER_URL)

# Khởi tạo ứng dụng đăng nhập
root = tk.Tk()
app = AuthApp(root)
root.mainloop()
