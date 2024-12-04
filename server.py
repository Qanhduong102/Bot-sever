import os
import datetime
import random
import requests
from flask import Flask
from flask_socketio import SocketIO, send
from geopy.geocoders import Nominatim


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Thay bằng secret key của bạn
socketio = SocketIO(app)

# Hàm lấy ngày hôm nay
def get_date():
    today = datetime.date.today()
    return f"Today's date is {today.strftime('%Y-%m-%d')}."

# Hàm lấy thời gian chính xác
def get_time():
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%H:%M:%S')}."

# Hàm lấy thời gian của một ngày cụ thể
def get_specific_day_time(date_str):
    try:
        specific_day = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return f"The time on {specific_day.strftime('%Y-%m-%d')} was {specific_day.strftime('%H:%M:%S')}."
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD."

# Thay đổi hàm get_weather để sử dụng OpenWeather API
def get_weather():
    api_key = "58e915fd5512001ac90dfdde93093371"  # Thay bằng API Key của bạn
    city = "Hanoi"  # Bạn có thể thay đổi thành tên thành phố bạn muốn lấy thông tin thời tiết

    # Tạo URL yêu cầu thời tiết
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric&lang=vi"  # units=metric để lấy nhiệt độ theo độ C, lang=vi để hiển thị tiếng Việt

    try:
        response = requests.get(complete_url, timeout=10)
        response.raise_for_status()  # Tăng cường việc kiểm tra trạng thái HTTP
        data = response.json()

        if data.get('cod') != 200:  # Kiểm tra lỗi trả về từ API
            return f"Error fetching weather data: {data.get('message', 'Unknown error')}"
        
        # Lấy thông tin thời tiết từ phản hồi
        main = data['main']
        weather = data['weather'][0]

        temperature = main['temp']
        description = weather['description']
        city_name = data['name']
        country_name = data['sys']['country']

        # Trả về thông tin thời tiết
        return f"The current weather in {city_name}, {country_name} is {description} with a temperature of {temperature}°C."

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"

# Lấy tin tức
def get_news():
    url = 'https://newsapi.org/v2/top-headlines?country=us&apiKey=aa322ef7db774b6da2eb37acc2827518'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Tăng cường việc kiểm tra trạng thái HTTP
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
def tell_joke(msg):
    jokes = [
        "Why don’t skeletons fight each other? They don’t have the guts.",
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "What do you call fake spaghetti? An impasta."
    ]
    return random.choice(jokes)
def greet():
    return "Hello! How can I help you today?"

def ask_about_mood():
    moods = ["I'm feeling great!", "I'm always happy to help!", "I'm just a bot, but I'm doing fine."]
    return random.choice(moods)

def about_bot():
    return "I'm a chatbot designed to assist you with information, time, weather, and more. How can I help you?"

def ask_about_hobbies():
    return "I enjoy chatting, answering questions, and helping people like you!"

def tell_features():
    return "I can tell you the time, weather, news, and even find out your location. I can also chat with you about various topics!"

def give_quote(msg):
    # Thêm điều kiện random để có thể trả lời quote hay không
    if random.choice([True, False]):
        quotes = [
            "The only way to do great work is to love what you do. – Steve Jobs",
            "In the middle of every difficulty lies opportunity. – Albert Einstein",
            "Life is what happens when you’re busy making other plans. – John Lennon"
        ]
        return random.choice(quotes)
    else:
        return "I don't feel like giving a quote right now."

# Lấy vị trí người dùng từ địa chỉ IP
def get_location():
    try:
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        if data['status'] == 'fail':
            return "Unable to get your location."
        
        city = data.get('city', 'Unknown')
        country = data.get('country', 'Unknown')
        return f"Your location is {city}, {country}."
    except requests.exceptions.RequestException as e:
        return f"Error fetching location: {e}"

@app.route("/", methods=["GET"])
def home():
    return "WebSocket Server is running!"

@socketio.on('message')
def handle_message(msg):
    print(f"Message from client: {msg}")
    # Kiểm tra yêu cầu của client
    if "what's the time" in msg.lower() or "current time" in msg.lower():
        response = get_time()
    elif "weather" in msg.lower():
        response = get_weather()
    elif "news" in msg.lower():
        response = get_news()
    elif "today's date" in msg.lower() or "what's the date" in msg.lower():
        response = get_date()
    elif "what time is it" in msg.lower():
        response = get_time()
    elif "what's the time on" in msg.lower():
        date_str = msg.lower().split("on")[-1].strip()
        response = get_specific_day_time(date_str)
    elif "how are you" in msg.lower():
        response = ask_about_mood()
    elif "who are you" in msg.lower():
        response = about_bot()
    elif "hobbies" in msg.lower():
        response = ask_about_hobbies()
    elif "joke" in msg.lower() or "funny" in msg.lower():
        response = tell_joke(msg)
    elif "quote" in msg.lower():
        response = give_quote(msg)
    elif "what can you do" in msg.lower():
        response = tell_features()
    elif "location" in msg.lower():
        response = get_location()
    else:
        response = f"{msg}"

    send(response)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 12345))  # PORT sẽ được Render cấp tự động
    socketio.run(app, host="0.0.0.0", port=port)
