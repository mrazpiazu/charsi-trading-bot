import asyncio
from playwright.async_api import async_playwright
import logging
import dotenv
import json
import os
import datetime as dt
import re
from utils.llm.xynth_finance.xynth_prompts import *
from utils.logger.logger import get_logger_config

dotenv.load_dotenv()  # Load environment variables from .env file

# Configure logging
logger = logging.getLogger("xynth_playwright")
get_logger_config(logging)  # Apply custom logging setup

# Logs in to Xynth Finance using credentials from environment variables
async def login_to_xynth(page):
    await page.wait_for_selector("div.auth-buttons-container", timeout=30000)
    await page.locator("div.auth-buttons-container").get_by_role("button", name="Log in").click()

    await page.fill("input[type='email']", os.getenv("XYNTH_USERNAME"))  # Fill email field
    await page.fill("input[type='password']", os.getenv("XYNTH_PASSWORD"))  # Fill password field
    await page.get_by_role("button", name="Sign in").click()  # Submit login form

    return

# Selects a specific model from the dropdown, unless it's already selected
async def select_model(page, model_name):
    await asyncio.sleep(1)
    await page.wait_for_selector("div.search-bar-model-selector", timeout=30000)

    # Check if the desired model is already selected
    selected_model = await page.locator("div.search-bar-model-selector").get_by_role("span", name=model_name).is_visible()
    if selected_model:
        return

    await page.locator("div.search-bar-model-selector").click()
    await asyncio.sleep(1)

    badge_spans = await page.locator("div.model-option span").all_inner_texts()  # Collect badge labels to exclude from matching
    options = await page.locator(f"div.model-option:has-text('{model_name}')").all()

    for option in options:
        text = await option.inner_text()
        # Remove badge text (like “Premium”, etc.) from the label
        for badge in badge_spans:
            text = text.replace(badge, "").strip()
        if text.strip() == model_name:
            await option.click()  # Click the correct model option
            break

    return

# Selects the desired tool from the tool dropdown
async def select_tool(page, tool_name):
    try:
        await asyncio.sleep(1)
        await page.wait_for_selector("div.search-bar-tool-selector", timeout=30000)

        # Check if the tool is already selected
        tool_tags = await page.locator("div.tool-tag").all_inner_texts()
        if tool_name in tool_tags:
            return

        await page.locator("div.search-bar-tool-selector").click()
        await asyncio.sleep(1)

        await page.locator(f"div.tool-name:has-text('{tool_name}')").click()  # Select tool
        await asyncio.sleep(1)

        await page.locator("div.search-bar-tool-selector").click()  # Close the dropdown
    except Exception as e:
        logging.error(f"Error selecting tool: {e}")
        # Continue gracefully if the tool is unavailable
    return

# Types the given prompt into the search bar and submits it
async def fill_search_bar(page, prompt):
    await asyncio.sleep(1)
    await page.wait_for_selector("textarea.search-bar-input", timeout=30000)
    await page.locator("textarea.search-bar-input").click()
    await asyncio.sleep(1)

    await page.fill("textarea.search-bar-input", prompt)
    await asyncio.sleep(1)
    await page.keyboard.press("Enter")  # Submit prompt
    return

# Sends a prompt to Xynth using the chosen model and tool
async def send_message(page, total_prompt, model_name, tool_name):
    await select_model(page, model_name)
    await select_tool(page, tool_name)
    await fill_search_bar(page, total_prompt)
    return

# Handles full prompt interaction with Xynth and parses trading actions
async def xynth_conversation_handler(page):
    for prompt in [STOCK_SCREENING_PROMPT, DEEP_TECHNICAL_ANALYSIS_PROMPT]:
        logger.info(f"Sending {prompt['prompt_name']} prompt to Xynth Finance")

        # Dynamically format prompts based on their type
        if prompt["prompt_name"] == "Stock Screening":
            prompt_text = prompt["prompt"].format(
                initial_balance=1000,
                current_date=dt.datetime.today().strftime("%A, %d of %B of %Y"),
                min_atr=4,
                max_atr=5,
            )
        elif prompt["prompt_name"] == "Deep Technical Analysis":
            prompt_text = prompt["prompt"].format(initial_balance=1000)
        else:
            prompt_text = prompt["prompt"]

        # Combine prompt and response format if applicable
        total_prompt = prompt_text + "\n\n" + prompt.get("response_format", "")

        await send_message(page, total_prompt, prompt["model_name"], prompt["tool_name"])

        # Wait for generation to complete (when stop icon disappears)
        await page.wait_for_selector("svg.lucide.lucide-square", state="detached", timeout=900 * 1000)

    # Extract all response blocks after prompts
    xynth_responses = await page.locator("div.message-content-1 div.text-section").all_inner_texts()

    retries_count = 0
    # Retry if JSON response is not valid or empty
    while len(json.loads(re.search(r'\[.*?\]', xynth_responses[-1], re.DOTALL)[0])) == 0:
        retries_count += 1
        logger.info("No trading actions found in the Xynth Finance response. Retrying...")
        await asyncio.sleep(5)
        await send_message(page, RETURN_JSON_PROMPT["prompt"], RETURN_JSON_PROMPT["model_name"], RETURN_JSON_PROMPT["tool_name"])
        xynth_responses = await page.locator("div.message-content-1 div.text-section").all_inner_texts()

        if retries_count == 2:
            break

    try:
        # Extract the JSON array from the last response
        trading_actions = json.loads(re.search(r'\[.*?\]', xynth_responses[-1], re.DOTALL)[0])
    except:
        logger.error("No trading actions found in the Xynth Finance response. Xynth response:")
        logger.error(xynth_responses[-1])
        trading_actions = []

    logger.info(f"Trading actions extracted from Xynth Finance response: {len(trading_actions)}")
    return trading_actions

# Filters out invalid or logically incorrect trading actions
def clean_trading_actions(trading_actions):
    clean_trading_actions = []

    for action in trading_actions:
        # Validate required fields
        if not all(key in action for key in ["stock", "entry_point", "stop_loss", "stop_loss_limit", "target_price", "expected_duration", "position_size", "potential_profit_loss", "risk_reward_ratio"]):
            logger.error(f"Invalid trading action structure found: {action}")
            continue
        if float(action["stop_loss"]) >= float(action["entry_point"]):
            logger.error(f"Removing action for stock {action['stock']} - Reason: Stop loss >= entry point")
            continue
        if float(action["stop_loss"]) >= float(action['target_price']):
            logger.error(f"Removing action for stock {action['stock']} - Reason: Stop loss >= target price")
            continue
        if float(action["potential_profit_loss"]) <= 0:
            logger.error(f"Removing action for stock {action['stock']} - Reason: profit/loss <= 0")
            continue

        clean_trading_actions.append(action)  # Add valid action

    return clean_trading_actions

# Main entrypoint: launches Playwright, runs the Xynth pipeline, returns cleaned actions
async def run_xynth_consultation_pipeline():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=100)  # Launch headless browser with slow motion
        context = await browser.new_context()
        page = await context.new_page()

        logging.info("Loading Xynth Finance")
        await page.goto("https://xynth.finance", timeout=60000)

        await login_to_xynth(page)
        logging.info("Logged in")

        logging.info("Initiating conversation with Xynth Finance")
        trading_actions = await xynth_conversation_handler(page)

        logging.info("Trading actions received from Xynth Finance")

        await browser.close()

        trading_actions = clean_trading_actions(trading_actions)  # Final cleaning step

        return trading_actions

# Synchronous wrapper to run the async Playwright flow
if __name__ == "__main__":
    asyncio.run(run_xynth_consultation_pipeline())
