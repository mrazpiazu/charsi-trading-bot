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
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
API_KEY = os.getenv(f"IG_API_KEY_{ENV}")
ACCOUNT_ID = os.getenv(f"IG_ACCOUNT_ID_{ENV}")

IG_ITEMS = ["CS.D.EURUSD.CFD.IP", "CS.D.GBPUSD.CFD.IP", "CS.D.USDJPY.CFD.IP"]


def wait_for_input():
    input("{0:-^80}\n".format("HIT CR TO UNSUBSCRIBE AND DISCONNECT FROM LIGHTSTREAMER"))


def heartbeat():
    while True:
        with open("/tmp/heartbeat.txt", "w") as f:
            f.write(str(time.time()))
        time.sleep(5)


def generate_sub():
    sub = Subscription("MERGE", IG_ITEMS, ["stock_name", "last_price", "time", "bid", "ask"])
    sub.setDataAdapter("QUOTE_ADAPTER")

    return sub


def run():

    threading.Thread(target=heartbeat, daemon=True).start()

    try:

        ig_service = IGService(
            config.username,
            config.password,
            config.api_key,
            config.acc_type,
            acc_number=config.acc_number,
        )

        ig_stream_service = IGStreamService(ig_service)
        ig_stream_service.create_session()


        logger.info(f"Generating subscription for items {IG_ITEMS}...")
        sub = generate_sub()

        logger.info("Setting up subscription...")
        sub.addListener(SubListener())
        ig_stream_service.subscribe(sub)

        wait_for_input()


    except Exception as e:
        logger.exception(f"Exception in main loop: {e}")

    logger.info("Waiting 5 seconds before retrying connection...")
    time.sleep(5)


if __name__ == "__main__":
    run()
