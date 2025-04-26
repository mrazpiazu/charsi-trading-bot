import time
import requests
import websocket
import json
import logger
from dotenv import load_dotenv
import os

load_dotenv()

# Configuración
API_URL = "https://api.ig.com/gateway/deal/session"
WS_URL = "wss://push.lightstreamer.com/lightstreamer"

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
API_KEY = os.getenv("IG_API_KEY")
ACCOUNT_ID = os.getenv("IG_ACCOUNT_ID")


def authenticate():
    logger.info("Authenticating...")
    headers = {
        "X-IG-API-KEY": API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Version": "3"
    }
    data = {
        "identifier": USERNAME,
        "password": PASSWORD
    }
    resp = requests.post(API_URL, json=data, headers=headers)
    resp.raise_for_status()
    cst = resp.headers.get("CST")
    x_security_token = resp.headers.get("X-SECURITY-TOKEN")
    logger.success("Authenticated")
    return cst, x_security_token


def on_message(ws, message):
    logger.info(f"Message received: {message}")


def on_error(ws, error):
    logger.error(f"WebSocket error: {error}")


def on_close(ws, close_status_code, close_msg):
    logger.warning("WebSocket closed")


def on_open(ws):
    logger.success("WebSocket connection opened")
    # Aquí deberías mandar tu mensaje de suscripción a un instrumento concreto


def run():
    while True:
        try:
            cst, token = authenticate()

            headers = {
                "CST": cst,
                "X-SECURITY-TOKEN": token
            }

            ws = websocket.WebSocketApp(
                WS_URL,
                header=[f"CST: {cst}", f"X-SECURITY-TOKEN: {token}"],
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )

            ws.run_forever(ping_interval=20, ping_timeout=10)

        except Exception as e:
            logger.exception(f"Exception in main loop: {e}")

        logger.info("Waiting 5 seconds before retrying...")
        time.sleep(5)


if __name__ == "__main__":
    run()
