import requests
import dotenv
import os
import logging
import datetime as dt


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
        plot_path = f"/tmp/{plot.get_label()}.png"
        plot.savefig(plot_path)

        with open(plot_path, 'rb') as file:
            url = f"https://api.telegram.org/bot{api_token}/sendPhoto"
            payload = {
                'chat_id': int(channel_id),
                'caption': f"{plot.get_label()}"
            }
            files = {'photo': file}
            response = requests.post(url, data=payload, files=files)

            if response.status_code != 200:
                logger.error(f"Failed to send plot to Telegram. Code: {response.status_code}. Text: {response.text}")
            else:
                # Remove the file after sending
                os.remove(plot_path)
                logger.info(f"Plot {plot.get_label()} sent successfully to Telegram.")

    # Send text report
    text_report = (
        f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Total Profit/Loss: ${report_data['total_profit_loss']}\n"
        f"Total Equity: ${report_data['total_equity']}\n"
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