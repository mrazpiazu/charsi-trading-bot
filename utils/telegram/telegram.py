import requests
import dotenv
import os
import logging


logger = logging.getLogger("telegram_connector")
logging.basicConfig()
logger.setLevel(logging.INFO)

dotenv.load_dotenv()

def send_telegram_message(message):

    api_token = os.getenv('TELEGRAM_API_TOKEN')
    channel_id = os.getenv('TELEGRAM_TARGET_ID')

    url = f"https://api.telegram.org/bot{api_token}/sendMessage"
    payload = {
        'chat_id': int(channel_id),
        'text': message
    }

    response = requests.get(url, data=payload)

    if response.status_code != 200:
        logger.error(f"Failed to send message to Telegram. Code: {response.status_code}. Text: {response.text}")

    return