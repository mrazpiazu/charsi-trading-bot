import requests
import dotenv
import os
import logging
import datetime as dt
import base64


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


def send_telegram_report(report_data):
    """
    Sends a report to Telegram with the provided data.
    """
    api_token = os.getenv('TELEGRAM_API_TOKEN')
    channel_id = os.getenv('TELEGRAM_TARGET_ID')

    # Send plot images
    for plot in report_data['plots']:

        url = f"https://api.telegram.org/bot{api_token}/sendPhoto"
        payload = {
            'chat_id': int(channel_id),
            'caption': f"Plot: {plot}"
        }
        files = {'photo': base64.b64decode(report_data['plots'][plot].encode('utf-8'))}
        response = requests.post(url, data=payload, files=files)

        if response.status_code != 200:
            logger.error(f"Failed to send plot to Telegram. Code: {response.status_code}. Text: {response.text}")
        else:
            # Remove the file after sending
            logger.info(f"Plot sent successfully to Telegram.")

    # Send text report
    text_report = (
        f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Total Profit/Loss: ${report_data['total_profit_loss']}\n"
        f"Total Equity: ${report_data['total_equity']}\n"
        f"Max Equity: ${report_data['max_equity']}\n"
        f"Min Equity: ${report_data['min_equity']}\n"
        f"Avg Equity: ${report_data['avg_equity']}\n"
        f"Max Profit/Loss: {report_data['max_profit_loss']}\n"
        f"Min Profit/Loss: {report_data['min_profit_loss']}\n"
        f"Avg Profit/Loss: {report_data['avg_profit_loss']}\n"
    )

    url = f"https://api.telegram.org/bot{api_token}/sendMessage"
    payload = {
        'chat_id': int(channel_id),
        'text': text_report
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        logger.error(f"Failed to send text report to Telegram. Code: {response.status_code}. Text: {response.text}")
    else:
        logger.info("Text report sent successfully to Telegram.")

    return


if __name__ == "__main__":

    message = "test"

    send_telegram_message(message)