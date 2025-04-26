import time
import threading
import requests
import websocket
import json
import logging
import os
from dotenv import load_dotenv
from lightstreamer.client import *
from trading_ig import IGService, IGStreamService
from trading_ig.config import config

from models import SubListener

logger = logging.getLogger(__name__)
load_dotenv()

ENV = "LIVE" # "DEMO" or "LIVE"

LS_URL = "https://push.lightstreamer.com"
API_URL = os.getenv(f"IG_API_URL_{ENV}")
USERNAME = os.getenv("IG_SERVICE_USERNAME")
PASSWORD = os.getenv("IG_SERVICE_PASSWORD")
API_KEY = os.getenv(f"IG_SERVICE_API_KEY_{ENV}")
ACCOUNT_ID = os.getenv(f"IG_SERVICE_ACCOUNT_ID_{ENV}")

IG_ITEMS = ["CS.D.EURUSD.CFD.IP", "CS.D.GBPUSD.CFD.IP", "CS.D.USDJPY.CFD.IP"]


def wait_for_input():
    input("{0:-^80}\n".format("HIT CR TO UNSUBSCRIBE AND DISCONNECT FROM LIGHTSTREAMER"))


def heartbeat():
    while True:
        with open("/tmp/heartbeat.txt", "w") as f:
            f.write(str(time.time()))
        time.sleep(5)


def authenticate():
    logger.info("Authenticating...")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-IG-API-KEY": API_KEY,
        "Version": "3"
    }
    data = {
        "identifier": USERNAME,
        "password": PASSWORD
    }
    resp = requests.post(f"{API_URL}/session", json=data, headers=headers)
    resp.raise_for_status()
    response_json = resp.json()
    logger.info("Authenticated")
    return response_json


def get_stream_auth_tokens(auth_json):

    logger.info("Obtaining stream auth tokens...")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {auth_json['oauthToken']['access_token']}",
        "IG-ACCOUNT-ID": auth_json['accountId'],
        "IG-API-KEY": API_KEY,
        "Version": "3"
    }

    params = {
        "fetchSessionTokens": "true"
    }

    resp = requests.get(f"{API_URL}/session", headers=headers, params=params)
    resp.raise_for_status()
    response_json = resp.json()
    logger.info("Obtained stream auth tokens")
    return response_json['cst'], response_json['x-st']  # cst, x-st

def generate_sub():
    sub = Subscription("MERGE", IG_ITEMS, ["stock_name", "last_price", "time", "bid", "ask"])
    sub.setDataAdapter("QUOTE_ADAPTER")

    return sub


def run():

    threading.Thread(target=heartbeat, daemon=True).start()

    try:

        logger.info("Obtaining cst and security token...")
        auth_json = authenticate()

        cst, xst = get_stream_auth_tokens(auth_json)

        loggerProvider = ConsoleLoggerProvider(ConsoleLogLevel.WARN)
        LightstreamerClient.setLoggerProvider(loggerProvider)

        logger.info("Creating Lightstreamer client...")
        client = LightstreamerClient(
            auth_json['lightstreamerEndpoint'],
            adapterSet=None
        )
        client.connectionDetails.setUser(auth_json['clientId'])
        client.connectionDetails.setPassword(auth_json['oauthToken']['access_token'])
        client.connect()

        logger.info(f"Generating subscription for items {IG_ITEMS}...")
        sub = generate_sub()

        logger.info("Setting up subscription...")
        sub.addListener(SubListener())
        client.subscribe(sub)

        wait_for_input()

        # Unsubscribing from Lightstreamer by using the subscription as key
        client.unsubscribe(sub)

        # Disconnecting
        client.disconnect()

    except Exception as e:
        logger.exception(f"Exception in main loop: {e}")

    logger.info("Waiting 5 seconds before retrying connection...")
    time.sleep(5)


if __name__ == "__main__":
    run()
