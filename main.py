import time
import threading
import requests
import websocket
import json
import logging
import os
from dotenv import load_dotenv
from lightstreamer_client import LightstreamerClient, Subscription

logger = logging.getLogger(__name__)
load_dotenv()

API_URL = "https://api.ig.com/gateway/deal"
LS_URL = "https://push.lightstreamer.com"

ENV = "DEMO" # "DEMO" or "LIVE"

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
API_KEY = os.getenv(f"IG_API_KEY_{ENV}")
ACCOUNT_ID = os.getenv(f"IG_ACCOUNT_ID_{ENV}")

IG_ITEMS = ["CS.D.EURUSD.CFD.IP", "CS.D.GBPUSD.CFD.IP", "CS.D.USDJPY.CFD.IP"]


def heartbeat():
    while True:
        with open("/tmp/heartbeat.txt", "w") as f:
            f.write(str(time.time()))
        time.sleep(5)


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
    resp = requests.post(f"{API_URL}/session", json=data, headers=headers)
    resp.raise_for_status()
    cst = resp.headers.get("CST")
    x_security_token = resp.headers.get("X-SECURITY-TOKEN")
    logger.info("Authenticated")
    return cst, x_security_token


def on_item_update(update):
    logger.info(f"Update received: {update.name} -> {update.field_values}")


def run():

    threading.Thread(target=heartbeat, daemon=True).start()

    while True:
        try:
            # REST API Authentication
            cst, x_security_token = authenticate()

            # Lightstreamer Client
            client = LightstreamerClient(
                LS_URL,
                adapter_set="DEFAULT"
            )

            # Stream Client Authentication
            client.connection_details.set_user(ACCOUNT_ID)
            client.connection_details.set_password(f"CST-{cst}|XST-{x_security_token}")

            logger.info("Connecting to Lightstreamer server...")
            client.connect()

            # Define subscription
            subscription = Subscription(
                mode="MERGE",
                items=IG_ITEMS,
            fields=["BID", "OFFER", "HIGH", "LOW", "UPDATE_TIME", "MARKET_STATE"]
            )
            subscription.add_listener(on_item_update)

            # Subscribe to items
            client.subscribe(subscription)

            logger.info("Subscription activated, listening for updates...")

            # Keep the script running
            while True:
                time.sleep(1)

        except Exception as e:
            logger.exception(f"Exception in main loop: {e}")

        logger.info("Waiting 5 seconds before retrying connection...")
        time.sleep(5)


if __name__ == "__main__":
    run()
