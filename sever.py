import socket
import threading
import random
import requests
from datetime import date, timedelta
import webbrowser
from geopy.geocoders import Nominatim
import datetime
import os

# Cấu hình server
HOST = '0.0.0.0'  # Lắng nghe mọi kết nối
PORT = int(os.getenv("PORT", 12345))  # Lấy cổng từ biến môi trường hoặc dùng mặc định là 12345

# Hàm lấy thời gian chính xác
def get_time():
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%H:%M:%S')}."

# Hàm lấy vị trí người dùng dựa trên địa chỉ IP
def get_location(ip_address):
    geolocator = Nominatim(user_agent="chatbot")
    # Ở đây bạn có thể sử dụng một dịch vụ IP Geolocation để lấy vị trí
    # Ví dụ: dịch vụ miễn phí hoặc API như ipinfo.io, ipstack.com.
    # Tuy nhiên, ở đây chỉ đơn giản giả lập bằng cách yêu cầu người dùng nhập thông tin vị trí
    location = geolocator.geocode(ip_address)
    if location:
        return f"Your approximate location is {location.address}."
    else:
        return "Unable to determine your location."

# Dự báo thời tiết giả lập
def get_weather():
    weather_conditions = ['sunny', 'cloudy', 'rainy', 'snowy', 'windy']
    temperature = random.randint(15, 35)
    condition = random.choice(weather_conditions)
    return f"The weather is {condition} and {temperature} degrees Celsius."

# Lấy tin tức
def get_news():
    url = 'https://newsapi.org/v2/top-headlines?country=us&apiKey=aa322ef7db774b6da2eb37acc2827518'
    try:
        response = requests.get(url, timeout=10)
        news_data = response.json()
        if news_data.get('status') == 'ok':
            articles = news_data.get('articles', [])
            if not articles:
                return "No articles found."
            return "Here are the top news headlines: " + ", ".join([article['title'] for article in articles[:5]])
        else:
            return "I'm unable to fetch the news right now."
    except requests.exceptions.RequestException as e:
        return f"Error fetching news: {e}"

# Lưu trữ các cuộc trò chuyện mẫu (ví dụ)
sample_conversations = {
    "hello": "Hi there! How can I help you?",
    "bye": "Goodbye! Have a great day!",
}

def handle_client(client_socket):
    stop_listening = False
    message = ""
    
    # Khởi tạo giá trị mặc định cho response_message trước khi sử dụng
    response_message = "Waiting for your message..."
    client_socket.send(response_message.encode('utf-8'))  # Gửi phản hồi ban đầu
    
    while not stop_listening:
        try:
            # Tiếp tục nhận dữ liệu cho đến khi không còn gì để nhận
            data = client_socket.recv(1024).decode('utf-8')
            if not data:  # Nếu không có dữ liệu, ngừng
                break
            message += data.strip()

            if message:  # Nếu có dữ liệu đầy đủ, xử lý
                print(f"Received message: {message}")
                translated_input = message.lower()

                # Kiểm tra các yêu cầu đặc biệt
                if "what's the date today" in translated_input or "today's date" in translated_input:
                    response_message = f"Today's date is {date.today().strftime('%B %d, %Y')}."
                elif translated_input == "how was yesterday":
                    yesterday = date.today() - timedelta(days=1)
                    response_message = f"Yesterday was {yesterday.strftime('%B %d, %Y')}."
                elif "in" in translated_input and "days" in translated_input:
                    words = translated_input.split()
                    try:
                        index_of_in = words.index("in")
                        days = int(words[index_of_in + 1])
                        future_date = date.today() + timedelta(days=days)
                        response_message = f"The date in {days} days will be {future_date.strftime('%B %d, %Y')}."
                    except (ValueError, IndexError):
                        response_message = "I'm sorry, I didn't understand the number of days."
                elif "stop" in translated_input:
                    stop_listening = True
                    response_message = "Goodbye! The program will stop now."
                elif "what time is it" in translated_input or "current time" in translated_input:
                    response_message = get_time()
                elif "weather" in translated_input:
                    response_message = get_weather()
                elif "news" in translated_input:
                    response_message = get_news()
                elif "play music" in translated_input:
                    user_request = translated_input.replace("play music", "").strip()
                    webbrowser.open(f"https://www.youtube.com/results?search_query={'+'.join(user_request.split())}")
                    response_message = f"Playing {user_request} for you on YouTube!"
                elif "turn on youtube" in translated_input:
                    webbrowser.open("https://www.youtube.com")
                    response_message = "Opening YouTube for you!"
                elif "turn on facebook" in translated_input:
                    webbrowser.open("https://www.facebook.com")
                    response_message = "Opening Facebook for you!"
                elif "turn on google" in translated_input:
                    webbrowser.open("https://www.google.com")
                    response_message = "Opening Google for you!"
                elif "turn on twitter" in translated_input:
                    webbrowser.open("https://www.twitter.com")
                    response_message = "Opening Twitter for you!"
                else:
                    response_message = sample_conversations.get(translated_input, "I'm not sure how to respond to that.")

                # Gửi phản hồi về cho client
                client_socket.send(response_message.encode('utf-8'))
                message = ""  # Reset message after sending response

        except Exception as e:
            print(f"Error handling client message: {e}")
            break
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)  # Lắng nghe tối đa 5 kết nối
    print(f"Server is running on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    start_server()
