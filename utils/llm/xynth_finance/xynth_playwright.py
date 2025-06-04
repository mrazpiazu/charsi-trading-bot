import asyncio
from playwright.async_api import async_playwright
import logging
import dotenv
import json
import os
import datetime as dt
import re
import time
from utils.llm.xynth_finance.xynth_prompts import *
from utils.logger.logger import get_logger_config

dotenv.load_dotenv()

# Configures logging
logger = logging.getLogger("xynth_playwright")
get_logger_config(logging)

async def login_to_xynth(page):

    await page.wait_for_selector("div.auth-buttons-container", timeout=30000)
    await page.locator("div.auth-buttons-container").get_by_role("button", name="Log in").click()

    # Fills the email field
    await page.fill("input[type='email']", os.getenv("XYNTH_USERNAME"))
    # Fills the password field
    await page.fill("input[type='password']", os.getenv("XYNTH_PASSWORD"))
    # Clicks on submit
    await page.get_by_role("button", name="Sign in").click()

    return


async def select_model(page, model_name):

    time.sleep(1)

    # Wait for the model selector to be visible
    await page.wait_for_selector("div.search-bar-model-selector", timeout=30000)

    # Check if the model is already selected
    selected_model = await page.locator("div.search-bar-model-selector").get_by_role("span", name=model_name).is_visible()

    if selected_model:
        return

    # Click on the model selector and select the desired model
    await page.locator("div.search-bar-model-selector").click()

    time.sleep(1)

    badge_spans = await page.locator("div.model-option span").all_inner_texts()
    options = await page.locator(f"div.model-option:has-text('{model_name}')").all()

    for option in options:
        text = await option.inner_text()
        # Remove every badge span from the text
        for badge in badge_spans:
            text = text.replace(badge, "").strip()
        if text.strip() == model_name:
            await option.click()
            break

    return


async def select_tool(page, tool_name):

    try:

        time.sleep(1)

        await page.wait_for_selector("div.search-bar-tool-selector", timeout=30000)

        # Check if the tool is already selected
        tool_tags = await page.locator("div.tool-tag").all_inner_texts()
        if tool_name in tool_tags:
            return

        # Click on the tool selector
        await page.locator("div.search-bar-tool-selector").click()

        time.sleep(1)

        # Click on the desired tool
        await page.locator(f"div.tool-name:has-text('{tool_name}')").click()

        time.sleep(1)

        # Close the tool selector
        await page.locator("div.search-bar-tool-selector").click()

    except Exception as e:
        logging.error(f"Error selecting tool: {e}")
        # If the tool is not found, we can just return
        # This might happen if the tool is not available in the current context
        # or if the tool name is incorrect

    return


async def fill_search_bar(page, prompt):

    time.sleep(1)

    await page.wait_for_selector("textarea.search-bar-input", timeout=30000)

    await page.locator("textarea.search-bar-input").click()

    time.sleep(1)

    await page.fill("textarea.search-bar-input", prompt)

    time.sleep(1)

    await page.keyboard.press("Enter")
    return


async def xynth_conversation_handler(page):


    for prompt in [STOCK_SCREENING_PROMPT, TECHNICAL_ANALYSIS_PROMPT, DEEP_TECHNICAL_ANALYSIS_PROMPT]:

        logger.info(f"Sending {prompt["prompt_name"]} prompt to Xynth Finance")


        if prompt["prompt_name"] == "Stock Screening":
            prompt_text = prompt["prompt"].format(initial_balance=1000, current_date=dt.datetime.today().strftime("%A, %d of %B of %Y"), min_atr=4, max_atr=5)
        else:
            prompt_text = prompt["prompt"]

        if "response_format" in prompt:
            total_prompt = prompt_text + "\n\n" + prompt["response_format"]
        else:
            total_prompt = prompt_text

        await select_model(page, STOCK_SCREENING_PROMPT["model_name"])
        await select_tool(page, STOCK_SCREENING_PROMPT["tool_name"])
        await fill_search_bar(page, total_prompt)
        await page.keyboard.press("Enter")

        # Wait until element does not exist anymore
        await page.wait_for_selector("svg.lucide.lucide-square", state="detached", timeout=900 * 1000)

    # logger.info("Sending technical analysis prompt to Xynth Finance")
    #
    # SECOND_PROMPT = TECHNICAL_ANALYSIS_PROMPT["prompt"]
    # if "response_format" in TECHNICAL_ANALYSIS_PROMPT:
    #     SECOND_PROMPT += "\n\n" + TECHNICAL_ANALYSIS_PROMPT["response_format"]
    #
    # await select_model(page, TECHNICAL_ANALYSIS_PROMPT["model_name"])
    # await select_tool(page, TECHNICAL_ANALYSIS_PROMPT["tool_name"])
    # await fill_search_bar(page, SECOND_PROMPT)
    # await page.keyboard.press("Enter")
    #
    # # Wait until element does not exist anymore
    # await page.wait_for_selector("svg.lucide.lucide-square", state="detached", timeout=900 * 1000)
    #
    # logger.info("Sending deep technical analysis prompt to Xynth Finance")
    #
    # THIRD_PROMPT = DEEP_TECHNICAL_ANALYSIS_PROMPT["prompt"]
    # if "response_format" in DEEP_TECHNICAL_ANALYSIS_PROMPT:
    #     THIRD_PROMPT += "\n\n" + DEEP_TECHNICAL_ANALYSIS_PROMPT["response_format"]
    #
    # await select_model(page, DEEP_TECHNICAL_ANALYSIS_PROMPT["model_name"])
    # await select_tool(page, DEEP_TECHNICAL_ANALYSIS_PROMPT["tool_name"])
    # await fill_search_bar(page, THIRD_PROMPT)
    # await page.keyboard.press("Enter")
    #
    # # Wait until element does not exist anymore
    # await page.wait_for_selector("svg.lucide.lucide-square", state="detached", timeout=900 * 1000)
    #
    # logger.info("Retrieving trading actions from Xynth Finance")

    xynth_responses = await page.locator("div.message-content-1 div.text-section").all_inner_texts()

    try:
        trading_actions = json.loads(re.search(r'\[.*?\]', xynth_responses[-1], re.DOTALL)[0])
    except:
        logger.error("No trading actions found in the Xynth Finance response.")
        trading_actions = []

    logger.info(f"Trading actions extracted from Xynth Finance response: {len(trading_actions)}")

    return trading_actions


# Main function to run the Playwright script
async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context()
        page = await context.new_page()

        logging.info("Loading Xynth Finance")
        await page.goto("https://xynth.finance", timeout=60000)

        # Logs in
        await login_to_xynth(page)
        logging.info("Logged in")

        logging.info("Initiating conversation with Xynth Finance")
        # Starts the conversation handler
        trading_actions = await xynth_conversation_handler(page)

        logging.info("Trading actions received from Xynth Finance")
        logging.info(trading_actions)

        await browser.close()

if __name__ == "__main__":

    asyncio.run(run())
