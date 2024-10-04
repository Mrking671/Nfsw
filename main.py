from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Your bot token from Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Store your bot token in environment variables for security

# API endpoint to get images based on user prompts
API_URL = "https://img-api.ashlynn.workers.dev/?prompt="

# Route to set the webhook for Telegram
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = f"{request.host_url}webhook"  # Your deployed server's webhook URL
    set_webhook_url = f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}'
    response = requests.get(set_webhook_url)
    return response.json()

# Webhook route for handling incoming updates from Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        # Get the incoming update (JSON format)
        update = request.get_json()
        
        # Extract message details
        message = update.get('message')
        if message:
            chat_id = message['chat']['id']
            text = message.get('text')

            if text:
                # Call the API with the user's prompt
                api_response = requests.get(API_URL + text).json()

                # Extract image URLs from the API response
                image_urls = api_response.get('image_urls', [])
                
                # Send each image back to the user
                for image_url in image_urls:
                    send_photo(chat_id, image_url)
                    
                # Optionally send the join message if provided in the API response
                join_message = api_response.get('join')
                if join_message:
                    send_message(chat_id, join_message)

        return "ok", 200

# Function to send a message via Telegram bot
def send_message(chat_id, text):
    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(send_url, json=payload)

# Function to send a photo via Telegram bot
def send_photo(chat_id, photo_url):
    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url
    }
    requests.post(send_url, json=payload)

if __name__ == '__main__':
    app.run(debug=True)
