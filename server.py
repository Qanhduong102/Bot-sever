import os
import datetime
import random
import requests
import webbrowser
import threading
from flask import Flask, request
from flask_socketio import SocketIO, send
from geopy.geocoders import Nominatim

# Setup Flask and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with your secret key
socketio = SocketIO(app)

# Sample Conversations Dictionary
sample_conversations = {
    "hello": "Hi there! How can I help you?",
    "bye": "Goodbye! Have a great day!",
}

# Functions for chatbot responses
def get_time():
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%H:%M:%S')}."

def get_location(ip_address):
    geolocator = Nominatim(user_agent="chatbot")
    location = geolocator.geocode(ip_address)
    if location:
        return f"Your approximate location is {location.address}."
    else:
        return "Unable to determine your location."

def get_weather():
    weather_conditions = ['sunny', 'cloudy', 'rainy', 'snowy', 'windy']
    temperature = random.randint(15, 35)
    condition = random.choice(weather_conditions)
    return f"The weather is {condition} and {temperature} degrees Celsius."

def get_news():
    url = 'https://newsapi.org/v2/top-headlines?country=us&apiKey=your-api-key'  # Replace with your API key
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

# WebSocket message handling
@app.route("/", methods=["GET"])
def home():
    return "WebSocket Server is running!"

@socketio.on('message')
def handle_message(msg):
    print(f"Message from client: {msg}")
    response_message = "I'm not sure how to respond to that."

    # Lowercase message for easier matching
    translated_input = msg.lower()

    # Handle specific commands
    if "what's the date today" in translated_input or "today's date" in translated_input:
        response_message = f"Today's date is {datetime.datetime.today().strftime('%B %d, %Y')}."
    elif translated_input == "how was yesterday":
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        response_message = f"Yesterday was {yesterday.strftime('%B %d, %Y')}."
    elif "in" in translated_input and "days" in translated_input:
        words = translated_input.split()
        try:
            index_of_in = words.index("in")
            days = int(words[index_of_in + 1])
            future_date = datetime.datetime.today() + datetime.timedelta(days=days)
            response_message = f"The date in {days} days will be {future_date.strftime('%B %d, %Y')}."
        except (ValueError, IndexError):
            response_message = "I'm sorry, I didn't understand the number of days."
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

    # Send the response back to the client
    send(response_message)

if __name__ == "__main__":
    # Run the WebSocket server
    port = int(os.getenv("PORT", 12345))  # Set the port number
    socketio.run(app, host="0.0.0.0", port=port)
