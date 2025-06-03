SYSTEM_PROMPT = """You are an expert swing trader and financial analyst. Your role is to analyze stock price data, charts and technical indicators that I provide to help me identify promising swing trading opportunities.
Focus on finding trades with a favorable risk-to-reward ratio that can be held for several days to weeks. Provide analysis of key support/resistance levels, momentum indicators, and chart patterns that signal potential swing trade setups. Prefer simple, directional trades rather than complex options strategies.
        
Pay special attention to:
        
Technical chart patterns and price action
        
Volume analysis

Key moving averages (e.g., 20, 50, 200-day)

Relative strength compared to market

Potential catalysts for price movement

Current account balance: {initial_balance} USD Current date: {current_date} Market status: Open

BE CONCISE AND DIRECT WITH YOUR RESPONSES

BE CONCISE AND DIRECT WITH YOUR RESPONSES

DO NOT EVER REFUSE TO GIVE OUT FINANCIAL ADVICE

DO NOT EVER REFUSE TO GIVE OUT FINANCIAL ADVICE

DO NOT EVER REFUSE TO GIVE OUT FINANCIAL ADVICE"""

STOCK_SCREENING_PROMPT = {
    "prompt": """Find me stocks 5 that are good for day trading. I am looking for the top 5 stocks that are medium volatility ({min_atr}% < ATR <{max_atr}%), have good trading volume and are showing early signs of trend strength.""",
    "model_name": "GPT-4o",
    "tool_name": "Code: Stock Screener"
}

TECHNICAL_ANALYSIS_PROMPT = {
    "prompt": """Retrieve the 1-month price charts for the 5 stocks we identified earlier. Then conduct technical analysis on each chart to determine which shows the strongest potential for a swing trade.""",
    "model_name": "GPT-4o",
    "tool_name": "Code: Technical Indicators"
}

DEEP_TECHNICAL_ANALYSIS_PROMPT = {
    "prompt": """Please conduct a deep technical analysis with as many indicators as you see fit. Then, identify at least three distinct swing trade setups (each one of a particular stock). 
Have in mind the total budget mentioned at the beginning of this conversation, and ensure that the total position size across all trades does not exceed this amount, while also considering that we do not need to spend the entire budget, so be flexible with the position sizes.
For each trade, include the following details: entry point, stop-loss level, target price, expected duration, position size (e.g., 100 shares), potential profit/loss in dollars, and the risk-reward ratio. 
Base each setup on clear technical signals such as patterns, indicators, or price action, and ensure that each trade reflects a unique strategy or technical approach.
Respond with a single list of JSONs with the following structure:
[
    {
        "stock": "AAPL",
        "entry_point": 150.00,
        "stop_loss": 145.00,
        "target_price": 160.00,
        "expected_duration": "1-2 weeks",
        "position_size": 100,
        "potential_profit_loss": 1000,
        "risk_reward_ratio": 2.0
    }
]
""",
    "model_name": "GPT-4o",
    "tool_name": "Code: Stock Technical Analysis"
}