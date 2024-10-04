import requests
import logging
from flask import Flask, request
import telebot

# Initialize Flask and TeleBot
app = Flask(__name__)
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

API_URL = 'https://evil.darkhacker7301.workers.dev/?question={}&model=horny'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to generate response from the API
def generate_ai_response(user_input):
    url = API_URL.format(user_input)
    logging.info(f"Sending request to API: {url}")
    
    try:
        response = requests.get(url)
        logging.info(f"API Response: {response.text}")  # Log the raw API response
        
        if response.status_code == 200:
            data = response.json()
            if data['status']:
                image_url = extract_image_url(data['gpt'])
                return {"gpt": data['gpt'], "image": image_url}
    except Exception as e:
        logging.error(f"Error while fetching API response: {e}")
    
    return None

# Function to extract image URL from the response
def extract_image_url(gpt_response):
    # Check if the Markdown contains the image URL
    if '![Image](' in gpt_response:
        start = gpt_response.find('(') + 1
        end = gpt_response.find(')')
        return gpt_response[start:end]
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
            response = generate_ai_response(text)
            if response:
                logging.info(f"Sending message: {response['gpt']}")  # Log the response message
                bot.send_message(chat_id=chat_id, text=response['gpt'])
                
                if response['image']:
                    logging.info(f"Sending image: {response['image']}")
                    bot.send_photo(chat_id=chat_id, photo=response['image'])
            else:
                logging.error("No response from API")
    return "OK", 200

# Set webhook
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url="https://YOUR_RENDER_DOMAIN/webhook")
    app.run(host="0.0.0.0", port=5000)
