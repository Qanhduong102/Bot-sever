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
        self.root.geometry("400x500")
        self.root.configure(bg="#2E3B4E")  # Màu nền tối cho không gian dễ chịu
        self.root.resizable(False, False)  # Không cho phép thay đổi kích thước cửa sổ

        # Tiêu đề đẹp hơn
        self.header = tk.Label(
            root, text="Authentication", font=("Roboto", 18, "bold"), fg="#FFFFFF", bg="#2E3B4E"
        )
        self.header.pack(pady=20)

        # Nút Đăng ký, Đăng nhập, Quên mật khẩu
        self.register_button = self.create_button("Register", "#4CAF50", self.show_register_form)
        self.login_button = self.create_button("Login", "#2196F3", self.show_login_form)
        self.forgot_button = self.create_button("Forgot Password", "#F44336", self.show_forgot_password_form)

    def create_button(self, text, bg_color, command):
        return tk.Button(
            self.root, text=text, command=command, bg=bg_color, fg="white", font=("Roboto", 12, "bold"),
            relief="flat", activebackground="#45a049", activeforeground="white", width=20, height=2,
            cursor="hand2", bd=0
        )

    def show_register_form(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("400x400")
        register_window.configure(bg="#2E3B4E")

        self.username_label = self.create_label(register_window, "Username")
        self.username_entry = self.create_entry(register_window)

        self.password_label = self.create_label(register_window, "Password")
        self.password_entry = self.create_entry(register_window, show="*")

        self.register_button = self.create_button("Register", "#4CAF50", self.register_user)
        self.register_button.pack(pady=20)

    def show_login_form(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")
        login_window.geometry("400x400")
        login_window.configure(bg="#2E3B4E")

        self.username_label = self.create_label(login_window, "Username")
        self.username_entry = self.create_entry(login_window)

        self.password_label = self.create_label(login_window, "Password")
        self.password_entry = self.create_entry(login_window, show="*")

        self.login_button = self.create_button("Login", "#2196F3", self.login_user)
        self.login_button.pack(pady=20)

    def show_forgot_password_form(self):
        forgot_window = tk.Toplevel(self.root)
        forgot_window.title("Forgot Password")
        forgot_window.geometry("400x400")
        forgot_window.configure(bg="#2E3B4E")

        self.email_label = self.create_label(forgot_window, "Email")
        self.email_entry = self.create_entry(forgot_window)

        self.reset_button = self.create_button("Reset Password", "#F44336", self.reset_password)
        self.reset_button.pack(pady=20)

    def create_label(self, parent, text):
        return tk.Label(parent, text=text, fg="white", bg="#2E3B4E", font=("Roboto", 12))

    def create_entry(self, parent, **kwargs):
        return tk.Entry(parent, **kwargs, font=('Roboto', 12), fg='white', bg='#3a4d70', bd=0, 
                        highlightthickness=2, highlightbackground="#4CAF50", insertbackground='white', width=30)

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
