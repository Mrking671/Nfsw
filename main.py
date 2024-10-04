import requests
import logging
from flask import Flask, request
import telebot

# Initialize Flask and TeleBot
app = Flask(__name__)
TOKEN = '7011638444:AAGqffTejoqZ8hegXPAsf_ddWJNtrYWfzsY'
bot = telebot.TeleBot(TOKEN)

API_URL = 'https://img-api.ashlynn.workers.dev/?prompt={}'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to fetch images from the API
def fetch_images_from_api(prompt):
    url = API_URL.format(prompt)
    logging.info(f"Sending request to API: {url}")
    
    try:
        response = requests.get(url)
        logging.info(f"API Response: {response.text}")  # Log the raw API response
        
        if response.status_code == 200:
            data = response.json()
            return data['image_urls']  # Return list of image URLs
    except Exception as e:
        logging.error(f"Error fetching from API: {e}")
    
    return None

# Telegram webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    logging.info(f"Received data from Telegram: {data}")
    
    if "message" in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        if text:
            image_urls = fetch_images_from_api(text)
            if image_urls:
                for img_url in image_urls:
                    logging.info(f"Sending image: {img_url}")
                    bot.send_photo(chat_id=chat_id, photo=img_url)
            else:
                bot.send_message(chat_id=chat_id, text="Sorry, I couldn't find any images.")
    return "OK", 200

# Set webhook
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url="https://nfsw.onrender.com/webhook")
    app.run(host="0.0.0.0", port=5000)
