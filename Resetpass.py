import tkinter as tk
from tkinter import messagebox
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import os
import bcrypt
def is_email_registered(email):
    try:
        # Đảm bảo kết nối tới đúng file cơ sở dữ liệu
        conn = sqlite3.connect(r"C:\Users\Acer\PycharmProjects\Server-Render-main\users.db")  # Thay "user.db" bằng đường dẫn đầy đủ nếu cần
        cursor = conn.cursor()
        
        # Truy vấn kiểm tra email
        query = "SELECT 1 FROM users WHERE email = ? LIMIT 1"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        
        conn.close()
        
        # Trả về True nếu email tồn tại
        return result is not None
    except sqlite3.Error as e:
        # In lỗi nếu có
        print(f"Database error: {e}")
        return False

def show_forgot_password(root):
     # Xóa tất cả các widget trong root để hiển thị giao diện mới
    for widget in root.winfo_children():
        widget.destroy()

    # Tạo một khung chính (giữa cửa sổ)
    forgot_password_frame = tk.Frame(root, bg="#f5f5f5", bd=2, relief="solid")
    
    # Căn giữa khung bằng pack + padding
    forgot_password_frame.pack(expand=True, fill="both", padx=50, pady=50)

    # Tiêu đề
    tk.Label(forgot_password_frame, text="Forgot Password", font=("Arial", 24, "bold"), 
             fg="#00796b", bg="#f5f5f5").pack(pady=(30, 15))  # Khoảng cách từ trên xuống

    # Hướng dẫn
    tk.Label(forgot_password_frame, text="Please enter your email to reset your password", 
             font=("Arial", 12), fg="#555555", bg="#f5f5f5").pack(pady=5)

    # Ô nhập email
    email_entry = tk.Entry(forgot_password_frame, font=("Arial", 14), bg="#e0f7fa", 
                           fg="#00796b", width=30, relief="groove")
    email_entry.pack(pady=(10, 20))  # Khoảng cách giữa ô nhập và nút
    
    # Xử lý gửi mã xác minh
    def send_verification_code():
        email = email_entry.get()
        if not email:
            messagebox.showerror("Error", "Please enter your email.")
            return
        # Kiểm tra email trong cơ sở dữ liệu
        if not is_email_registered(email):
            messagebox.showerror("Error", "This email is not registered.")
            return
        # Tạo mã xác minh
        verification_code = str(random.randint(100000, 999999))

        try:
            # Thông tin email người gửi
            sender_email = "autochatbot40@gmail.com"  # Thay bằng email của bạn
            sender_password = "zlji ftme fhcc zlzg"  # Thay bằng App Password của bạn

            # Cấu hình email
            subject = "Your Verification Code"
            message = f"Your verification code is: {verification_code}"

            # Tạo email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            # Kết nối tới SMTP Server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
            server.quit()

            # Hiển thị thông báo thành công
            messagebox.showinfo("Success", f"Verification code has been sent to {email}")

            # Chuyển sang giao diện nhập mã
            show_code_verification(forgot_password_frame, email, verification_code)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")

    # Nút gửi mã
    send_button = tk.Button(
        forgot_password_frame, text="Send Verification Code", font=("Arial", 12, "bold"),
        bg="#00796b", fg="white", activebackground="#004d40", activeforeground="white",
        command=send_verification_code, cursor="hand2", relief="flat"
    )
    send_button.pack(pady=20)
    # Nút "Back to Sign Up"
    back_button = tk.Button(
       forgot_password_frame, text="Back to Sign Up", font=("Arial", 12),
       bg="#f5f5f5", fg="#00796b", activebackground="#e0f7fa", activeforeground="#004d40",
       command=lambda: close_and_show_signup(root),  
       cursor="hand2", relief="flat"
)
    back_button.pack(pady=10)
# Hàm đóng cửa sổ và mở lại file Sign.py
def close_and_show_signup(root):
    # Đóng cửa sổ hiện tại
    root.destroy()
    
    # Mở file Sign.py
    os.system("python Sign.py")
    
# Giao diện nhập mã xác minh
def show_code_verification(forgot_password_frame, email, verification_code):
    # Dọn dẹp giao diện cũ
    for widget in forgot_password_frame.winfo_children():
        widget.destroy()

    # Tiêu đề
    tk.Label(forgot_password_frame, text="Verify Code", font=("Arial", 24, "bold"), fg="#00796b", bg="#f5f5f5").pack(pady=15)

    # Hướng dẫn
    tk.Label(forgot_password_frame, text=f"Enter the code sent to {email}", font=("Arial", 12), fg="#555555", bg="#f5f5f5").pack(pady=5)

    # Ô nhập mã xác minh
    code_entry = tk.Entry(forgot_password_frame, font=("Arial", 14), bg="#e0f7fa", fg="#00796b", width=30, relief="groove")
    code_entry.pack(pady=10)

    # Xử lý đặt lại mật khẩu
    def reset_password():
        entered_code = code_entry.get()
        if entered_code != verification_code:
            messagebox.showerror("Error", "Invalid verification code.")
        else:
            show_reset_password(forgot_password_frame)

    # Nút xác minh
    verify_button = tk.Button(
        forgot_password_frame, text="Verify Code", font=("Arial", 12, "bold"),
        bg="#00796b", fg="white", activebackground="#004d40", activeforeground="white",
        command=reset_password, cursor="hand2", relief="flat"
    )
    verify_button.pack(pady=20)
   
   # Nút "Back"
    back_button = tk.Button(
    forgot_password_frame, text="Back", font=("Arial", 12, "bold"),
    bg="#b71c1c", fg="white", activebackground="#7f0000", activeforeground="white",
    command=lambda: show_forgot_password(root),  # Truyền root thay vì forgot_password_frame
    cursor="hand2", relief="flat"
    )
    back_button.pack(pady=10)

# Giao diện đặt lại mật khẩu
def show_reset_password(forgot_password_frame):
    # Dọn dẹp giao diện cũ
    for widget in forgot_password_frame.winfo_children():
        widget.destroy()

    # Tiêu đề
    tk.Label(forgot_password_frame, text="Reset Password", font=("Arial", 24, "bold"), fg="#00796b", bg="#f5f5f5").pack(pady=15)

    # Nhập email
    tk.Label(forgot_password_frame, text="Email", font=("Arial", 12), fg="#555555", bg="#f5f5f5").pack(pady=5)
    email_entry = tk.Entry(forgot_password_frame, font=("Arial", 14), bg="#e0f7fa", fg="#00796b", width=30, relief="groove")
    email_entry.pack(pady=10)

    # Nhập mật khẩu mới
    tk.Label(forgot_password_frame, text="New Password", font=("Arial", 12), fg="#555555", bg="#f5f5f5").pack(pady=5)
    new_password_entry = tk.Entry(forgot_password_frame, font=("Arial", 14), bg="#e0f7fa", fg="#00796b", width=30, show="*", relief="groove")
    new_password_entry.pack(pady=10)

    # Nhập lại mật khẩu mới
    tk.Label(forgot_password_frame, text="Confirm New Password", font=("Arial", 12), fg="#555555", bg="#f5f5f5").pack(pady=5)
    confirm_password_entry = tk.Entry(forgot_password_frame, font=("Arial", 14), bg="#e0f7fa", fg="#00796b", width=30, show="*", relief="groove")
    confirm_password_entry.pack(pady=10)

    # Hiển thị/ẩn mật khẩu
    def toggle_password_visibility():
        if show_password_var.get():
            new_password_entry.config(show="")
            confirm_password_entry.config(show="")
        else:
            new_password_entry.config(show="*")
            confirm_password_entry.config(show="*")

    show_password_var = tk.BooleanVar()
    show_password_checkbox = tk.Checkbutton(forgot_password_frame, text="Show Password", variable=show_password_var, 
                                            font=("Arial", 12), fg="#00796b", bg="#f5f5f5", command=toggle_password_visibility)
    show_password_checkbox.pack(pady=10)

    # Xác nhận đặt lại mật khẩu
    def confirm_reset():
        email = email_entry.get()
        new_password = new_password_entry.get()
        confirm_password = confirm_password_entry.get()

        if not email or not new_password or not confirm_password:
            messagebox.showerror("Error", "All fields are required.")
        elif new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
        else:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            try:
                # Kết nối cơ sở dữ liệu
                conn = sqlite3.connect(r"C:\Users\Acer\PycharmProjects\Server-Render-main\users.db")  # Thay "user.db" bằng đường dẫn đầy đủ nếu cần
                cursor = conn.cursor()

                # Kiểm tra xem email có tồn tại không
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                user = cursor.fetchone()
                if not user:
                    messagebox.showerror("Error", "Email does not exist.")
                else:
                    # Cập nhật mật khẩu mới
                    cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
                    conn.commit()
                    messagebox.showinfo("Success", "Password has been reset successfully!")
                    
                    # Đóng giao diện hiện tại
                    forgot_password_frame.destroy()
                    
                    # Mở lại giao diện Sign.py
                    os.system("python Sign.py")
                
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset password: {e}")

    # Nút xác nhận
    reset_button = tk.Button(
        forgot_password_frame, text="Reset Password", font=("Arial", 12, "bold"), 
        bg="#00796b", fg="white", activebackground="#004d40", activeforeground="white", 
        command=confirm_reset, cursor="hand2", relief="flat"
    )
    reset_button.pack(pady=20)


def center_window(window, width, height):
    # Lấy kích thước màn hình
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Tính toán tọa độ để đặt cửa sổ ở giữa
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Thiết lập vị trí cửa sổ
    window.geometry(f"{width}x{height}+{x}+{y}")

# Main
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Forgot Password Example")
    root.configure(bg="#e0f7fa")

    # Kích thước cửa sổ
    window_width = 800
    window_height = 600

    # Đặt cửa sổ ở giữa màn hình
    center_window(root, window_width, window_height)

    # Hàm hiển thị giao diện quên mật khẩu
    show_forgot_password(root)  # Bạn cần định nghĩa hàm này

    root.mainloop()