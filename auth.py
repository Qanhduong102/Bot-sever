import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
import requests
from PIL import Image, ImageTk
SERVER_URL = "https://bot-sever-1-m5e4.onrender.com"  # Địa chỉ WebSocket server

def login():
    email = email_entry.get()
    password = password_entry.get()

    if not email or not password:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
        return

    try:
        response = requests.post(f"{SERVER_URL}/login", json={"email": email, "password": password})
        if response.status_code == 200:
            messagebox.showinfo("Thành công", "Đăng nhập thành công!")
        else:
            messagebox.showerror("Lỗi", response.json().get("message", "Đăng nhập thất bại!"))
    except requests.exceptions.RequestException:
        messagebox.showerror("Lỗi", "Không thể kết nối đến server!")

def show_register():
    login_frame.pack_forget()
    register_frame.pack()

def register():
    email = reg_email_entry.get()
    password = reg_password_entry.get()
    confirm_password = reg_confirm_entry.get()

    if not email or not password or not confirm_password:
        messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
        return

    if password != confirm_password:
        messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
        return

    try:
        response = requests.post(f"{SERVER_URL}/register", json={"email": email, "password": password})
        if response.status_code == 201:
            messagebox.showinfo("Thành công", "Đăng ký thành công!")
            register_frame.pack_forget()
            login_frame.pack()
        else:
            messagebox.showerror("Lỗi", response.json().get("message", "Đăng ký thất bại!"))
    except requests.exceptions.RequestException:
        messagebox.showerror("Lỗi", "Không thể kết nối đến server!")

# Giao diện chính
root = tk.Tk()
root.title("Đăng nhập/Đăng ký")
root.geometry("800x600")
root.resizable(False, False)

# Thêm hình nền
bg_image = Image.open("background.jpg")  # Đường dẫn file ảnh
bg_image = bg_image.resize((800, 600), Image.ANTIALIAS)  # Resize ảnh phù hợp với cửa sổ
bg_image = ImageTk.PhotoImage(bg_image)

# Định dạng chung cho các nút
button_style = {
    "bg": "#6C63FF",  # Màu tím
    "fg": "white",  # Chữ trắng
    "font": ("Arial", 12, "bold"),
    "relief": "flat",
    "activebackground": "#4A47A3",  # Màu tím đậm hơn khi hover
}

# Frame đăng nhập
login_frame = tk.Frame(root, bg="#F5F5F5", bd=2, relief="solid", width=400, height=400)
login_frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(login_frame, text="Đăng nhập", font=("Arial", 20, "bold"), bg="#F5F5F5", fg="#333333").pack(pady=20)
tk.Label(login_frame, text="Email:", font=("Arial", 12), bg="#F5F5F5").pack(anchor="w", padx=50)
email_entry = tk.Entry(login_frame, width=30, font=("Arial", 12))
email_entry.pack(padx=50, pady=5)

tk.Label(login_frame, text="Mật khẩu:", font=("Arial", 12), bg="#F5F5F5").pack(anchor="w", padx=50)
password_entry = tk.Entry(login_frame, show="*", width=30, font=("Arial", 12))
password_entry.pack(padx=50, pady=5)

tk.Button(login_frame, text="Đăng nhập", command=login, **button_style).pack(pady=15)
tk.Button(login_frame, text="Chưa có tài khoản? Đăng ký", command=show_register, **button_style).pack()

# Frame đăng ký
register_frame = tk.Frame(root, bg="#F5F5F5", bd=2, relief="solid", width=400, height=450)

tk.Label(register_frame, text="Đăng ký", font=("Arial", 20, "bold"), bg="#F5F5F5", fg="#333333").pack(pady=20)
tk.Label(register_frame, text="Email:", font=("Arial", 12), bg="#F5F5F5").pack(anchor="w", padx=50)
reg_email_entry = tk.Entry(register_frame, width=30, font=("Arial", 12))
reg_email_entry.pack(padx=50, pady=5)

tk.Label(register_frame, text="Mật khẩu:", font=("Arial", 12), bg="#F5F5F5").pack(anchor="w", padx=50)
reg_password_entry = tk.Entry(register_frame, show="*", width=30, font=("Arial", 12))
reg_password_entry.pack(padx=50, pady=5)

tk.Label(register_frame, text="Xác nhận mật khẩu:", font=("Arial", 12), bg="#F5F5F5").pack(anchor="w", padx=50)
reg_confirm_entry = tk.Entry(register_frame, show="*", width=30, font=("Arial", 12))
reg_confirm_entry.pack(padx=50, pady=5)

tk.Button(register_frame, text="Hoàn tất", command=register, **button_style).pack(pady=15)
tk.Button(register_frame, text="Quay lại", command=lambda: (register_frame.pack_forget(), login_frame.pack()), **button_style).pack()

# Hiển thị frame đăng nhập ban đầu
login_frame.pack()

root.mainloop()
