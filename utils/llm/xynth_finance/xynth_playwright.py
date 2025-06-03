import asyncio
from playwright.async_api import async_playwright
import logging
import dotenv
import os
import datetime as dt
import re
from utils.llm.xynth_finance.xynth_prompts import *

dotenv.load_dotenv()

# Configures logging
logging.basicConfig(level=logging.INFO)

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

    # Wait for the model selector to be visible
    await page.wait_for_selector("div.search-bar-model-selector", timeout=30000)

    # Check if the model is already selected
    selected_model = await page.locator("div.search-bar-model-selector").get_by_role("span", name=model_name).is_visible()

    if selected_model:
        return

    # Click on the model selector and select the desired model
    await page.locator("div.search-bar-model-selector").click()
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

    logging.info(f"Model selected: {model_name}")

    return


async def select_tool(page, tool_name):

    await page.wait_for_selector("div.search-bar-tool-selector", timeout=30000)

    # Click on the tool selector
    await page.locator("div.search-bar-tool-selector").click()
    # Click on the desired tool
    await page.locator(f"div.tool-name:has-text('{tool_name}')").click()

    return


async def xynth_conversation_handler(page):

    INITIAL_PROMPT = SYSTEM_PROMPT.format(initial_balance=1000, current_date=dt.datetime.today().strftime("%A, %d of %B of %Y")) + "\n\n" + STOCK_SCREENING_PROMPT["prompt"].format(min_atr=4, max_atr=5)

    await select_model(page, STOCK_SCREENING_PROMPT["model_name"])
    await select_tool(page, STOCK_SCREENING_PROMPT["tool_name"])
    await page.locator("textarea.search-bar-input").click()
    await page.fill("textarea.search-bar-input", INITIAL_PROMPT)
    await page.keyboard.press("Enter")

    await page.wait_for_timeout(30000)  # Wait for the response to be generated

    await select_model(page, TECHNICAL_ANALYSIS_PROMPT["model_name"])
    await select_tool(page, TECHNICAL_ANALYSIS_PROMPT["tool_name"])
    await page.locator("textarea.search-bar-input").click()
    await page.fill("textarea.search-bar-input", TECHNICAL_ANALYSIS_PROMPT["prompt"])
    await page.keyboard.press("Enter")

    await page.wait_for_selector(30000) # Wait for the response to be generated

    await select_model(page, DEEP_TECHNICAL_ANALYSIS_PROMPT["model_name"])
    await select_tool(page, DEEP_TECHNICAL_ANALYSIS_PROMPT["tool_name"])
    await page.locator("textarea.search-bar-input").click()
    await page.fill("textarea.search-bar-input", DEEP_TECHNICAL_ANALYSIS_PROMPT["prompt"])
    await page.keyboard.press("Enter")

    await page.wait_for_selector(30000) # Wait for the response to be generated

    xynth_responses = await page.locator("pre.codebar_results").all()

    responses_texts = [await response.inner_text() for response in xynth_responses]

    trading_actions = re.search(r'\[.*?\]', responses_texts[-1], re.DOTALL)

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
