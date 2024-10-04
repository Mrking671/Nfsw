import os
import requests
from flask import Flask, request
import telegram

TOKEN = os.getenv("BOT_TOKEN")  # Your Telegram bot token
API_URL = "https://evil.darkhacker7301.workers.dev/?question={}&model=horny"
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        
        if text:
            response = generate_ai_response(text)
            if response:
                bot.send_message(chat_id=chat_id, text=response['gpt'])
                if response['image']:
                    bot.send_photo(chat_id=chat_id, photo=response['image'])
                    
    return "OK", 200

def generate_ai_response(user_input):
    url = API_URL.format(user_input)
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status']:
            image_url = extract_image_url(data['gpt'])
            return {"gpt": data['gpt'], "image": image_url}
    return None

def extract_image_url(gpt_response):
    # Extract the image URL from the gpt response (Markdown format)
    if '![Image](' in gpt_response:
        start = gpt_response.find('(') + 1
        end = gpt_response.find(')')
        return gpt_response[start:end]
    return None

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    url = f"https://{os.getenv('RENDER_EXTERNAL_URL')}/webhook"
    webhook_status = bot.setWebhook(url)
    if webhook_status:
        return "Webhook set successfully", 200
    else:
        return "Webhook setup failed", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
