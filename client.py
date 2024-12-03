import socketio

# Địa chỉ server WebSocket
SERVER_URL = "https://socket-server-mt3h.onrender.com"

# Tạo client WebSocket
sio = socketio.Client()

# Xử lý kết nối
@sio.event
def connect():
    print("Kết nối thành công tới server!")

# Xử lý ngắt kết nối
@sio.event
def disconnect():
    print("Ngắt kết nối từ server!")

# Xử lý tin nhắn từ server
@sio.on('message')
def on_message(data):
    print(f"Phản hồi từ server: {data}")

def start_client():
    try:
        sio.connect(SERVER_URL)
        while True:
            message = input("Nhập tin nhắn (hoặc 'exit' để thoát): ")
            if message.lower() == "exit":
                print("Đã ngắt kết nối.")
                break
            sio.send(message)
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        sio.disconnect()

if __name__ == "__main__":
    start_client()
