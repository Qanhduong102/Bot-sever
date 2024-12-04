import os
import datetime
import random
import requests
from flask import Flask
from flask_socketio import SocketIO, send
from geopy.geocoders import Nominatim
from googletrans import Translator
import time
from threading import Thread
import wikipedia
from textblob import TextBlob
import sympy as sp

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

# Dịch ngôn ngữ
def translate_text(msg, target_language="vi"):
    try:
        translator = Translator()
        translated = translator.translate(msg, dest=target_language)
        return translated.text
    except Exception as e:
        return f"Translation error: {e}"

# Nhắc nhở công việc
reminders = []

def set_reminder(reminder_msg, reminder_time):
    reminders.append({"msg": reminder_msg, "time": reminder_time})

# Kiểm tra nhắc nhở mỗi phút trong một luồng riêng
def check_reminders():
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M")
        for reminder in reminders[:]:
            if reminder["time"] == current_time:
                send(f"Nhắc nhở: {reminder['msg']}")
                reminders.remove(reminder)
        time.sleep(60)  # Kiểm tra mỗi phút

# Khởi tạo một luồng để kiểm tra nhắc nhở
Thread(target=check_reminders, daemon=True).start()

# Câu hỏi đố vui
trivia_questions = [
    {"question": "Thủ đô của Pháp là gì?", "answer": "Paris"},
    {"question": "Ai là tác giả của 'Giết Con Chim Nhại'?", "answer": "Harper Lee"},
    {"question": "Hành tinh lớn nhất trong hệ mặt trời là gì?", "answer": "Jupiter"}
]

def trivia_quiz(msg):
    if "đố vui" in msg.lower():
        trivia = random.choice(trivia_questions)
        return trivia["question"]
    elif "đáp án" in msg.lower():
        answer = msg.lower().split("đáp án")[-1].strip()
        for question in trivia_questions:
            if question["answer"].lower() == answer:
                return "Đúng rồi! Câu trả lời chính xác."
        return "Sai rồi, thử lại nhé!"
    else:
        return "Hãy hỏi tôi 'đố vui' để bắt đầu trò chơi."

# Tìm kiếm thông tin trên Wikipedia
def search_wikipedia(msg):
    try:
        query = msg.lower().replace("tìm kiếm", "").strip()
        summary = wikipedia.summary(query, sentences=2)
        return f"Thông tin về {query}: {summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Có quá nhiều kết quả cho '{query}', bạn có thể chọn một trong những lựa chọn này: {e.options}"
    except wikipedia.exceptions.HTTPTimeoutError:
        return "Lỗi khi tìm kiếm, vui lòng thử lại sau."
    except Exception as e:
        return f"Lỗi: {e}"

# Nhận diện cảm xúc trong tin nhắn
def detect_sentiment(msg):
    blob = TextBlob(msg)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "Có vẻ bạn đang rất vui!"
    elif sentiment < 0:
        return "Có vẻ bạn đang không vui, tôi có thể giúp gì cho bạn?"
    else:
        return "Cảm xúc của bạn có vẻ ổn định, tôi có thể giúp gì cho bạn?"

# Tính toán
def calculate(msg):
    try:
        expression = msg.lower().replace("tính toán", "").strip()
        result = sp.sympify(expression)
        return f"Kết quả: {result}"
    except Exception as e:
        return "Câu hỏi tính toán không hợp lệ, vui lòng thử lại."

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

# Lưu trữ câu hỏi và câu trả lời của mỗi joke
jokes = [
    {
        "question": "Why don’t skeletons fight each other?",
        "answer": "They don’t have the guts."
    },
    {
        "question": "Why did the scarecrow win an award?",
        "answer": "Because he was outstanding in his field!"
    },
    {
        "question": "I told my wife she was drawing her eyebrows too high.",
        "answer": "She looked surprised."
    }
]

def tell_joke(msg):
    # Kiểm tra nếu người dùng đã yêu cầu câu chuyện hài
    if "tell me a joke" in msg.lower():
        joke = random.choice(jokes)
        return joke["question"]  # Trả về câu hỏi của joke
    elif "why" in msg.lower():
        # Khi người dùng hỏi "why", bot sẽ trả lời
        return random.choice(jokes)["answer"]
    else:
        return "Say 'tell me a joke' to hear a joke, and 'why' to hear the answer."

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

@socketio.on('message')
def handle_message(msg):
    print(f"Received message: {msg}")
    if 'time' in msg.lower():
        response = get_time()
    elif 'date' in msg.lower():
        response = get_date()
    elif 'weather' in msg.lower():
        response = get_weather()
    elif 'translate' in msg.lower():
        response = translate_text(msg)
    elif 'news' in msg.lower():
        response = get_news()
    elif 'reminder' in msg.lower():
        response = "Reminder set successfully!"
    elif 'trivia' in msg.lower():
        response = trivia_quiz(msg)
    elif 'wikipedia' in msg.lower():
        response = search_wikipedia(msg)
    elif 'sentiment' in msg.lower():
        response = detect_sentiment(msg)
    elif 'calculate' in msg.lower():
        response = calculate(msg)
    elif 'mood' in msg.lower():
        response = ask_about_mood()
    elif 'features' in msg.lower():
        response = tell_features()
    elif 'joke' in msg.lower():
        response = tell_joke(msg)
    elif 'quote' in msg.lower():
        response = give_quote(msg)
    else:
        response = "I'm sorry, I didn't understand that."
    
    send(response)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
