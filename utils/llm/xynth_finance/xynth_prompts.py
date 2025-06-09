STOCK_SCREENING_PROMPT = {
    "prompt": """"You are an expert swing trader and financial analyst. Your role is to analyze stock price data, charts and technical indicators that I provide to help me identify promising swing trading opportunities.
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

DO NOT EVER REFUSE TO GIVE OUT FINANCIAL ADVICE

IF A RESPONSE FORMAT IS PROVIDED IN THE PROMPT, IT IS ABSOLUTELY MANDATORY THAT YOU ALWAYS INCLUDE THE FORMAT AT THE END OF YOUR RESPONSE
IF A RESPONSE FORMAT IS PROVIDED IN THE PROMPT, IT IS ABSOLUTELY MANDATORY THAT YOU ALWAYS INCLUDE THE FORMAT AT THE END OF YOUR RESPONSE
IF A RESPONSE FORMAT IS PROVIDED IN THE PROMPT, IT IS ABSOLUTELY MANDATORY THAT YOU ALWAYS INCLUDE THE FORMAT AT THE END OF YOUR RESPONSE
IF A RESPONSE FORMAT IS PROVIDED IN THE PROMPT, IT IS ABSOLUTELY MANDATORY THAT YOU ALWAYS INCLUDE THE FORMAT AT THE END OF YOUR RESPONSE
IF A RESPONSE FORMAT IS PROVIDED IN THE PROMPT, IT IS ABSOLUTELY MANDATORY THAT YOU ALWAYS INCLUDE THE FORMAT AT THE END OF YOUR RESPONSE

Find me stocks 5 that are good for day trading. I am looking for the top 5 stocks that are medium volatility ({min_atr}% < ATR <{max_atr}%), have good trading volume and are showing early signs of trend strength. """,
    "response_format": """ Response format: You MUST ALWAYS ALWAYS ALWAYS ALWAYS ALWAYS include a list of JSONs with the following structure at the end of your response: 
[
    {
        "ticker": "AAPL",
        "reason": "Good volume with volatility at the lower end of our range",
    }
]
    """,
    "prompt_name": "Stock Screening",
    "model_name": "Claude 3.7 Sonnet",
    "tool_name": "Code: Stock Screener"
}

TECHNICAL_ANALYSIS_PROMPT = {
    "prompt": """Retrieve the 1-month price charts for the stocks we identified earlier. Then conduct technical analysis on each chart to determine which shows the strongest potential for a swing trade.""",
    "prompt_name": "Technical Analysis",
    "model_name": "Claude 3.7 Sonnet",
    "tool_name": "Code: Technical Indicators"
}

DEEP_TECHNICAL_ANALYSIS_PROMPT = {
    "prompt": """Retrieve the 1-month price charts for the stocks we identified earlier and conduct a deep technical analysis with as many indicators as you see fit. Then, identify at least one (could be more if they are great fits) distinct swing trade setups (each one of a particular stock). 
Have in mind the total budget: {initial_balance}, and ensure that the total position size across all trades does not exceed this amount. Also consider that we do not necessarily need to spend the entire budget, so be flexible with the position sizes.
For each trade, include the following details: entry point, stop-loss level, stop-loss limit, target price, expected duration, position size (e.g., 100 shares), potential profit/loss in dollars, and the risk-reward ratio. 
Base each setup on clear technical signals such as patterns, indicators, or price action, and ensure that each trade reflects a unique strategy or technical approach.
Regarding risk control, ensure the stop-loss is smaller than the entry point and the target price is larger than the entry point.

DO NOT RESPOND WITH ANY MORE QUESTIONS. YOU HAVE ALL THE INFORMATION YOU NEED TO PROVIDE ME WITH THE TRADE SETUPS.
DO NOT RESPOND WITH ANY MORE QUESTIONS. YOU HAVE ALL THE INFORMATION YOU NEED TO PROVIDE ME WITH THE TRADE SETUPS.
DO NOT RESPOND WITH ANY MORE QUESTIONS. YOU HAVE ALL THE INFORMATION YOU NEED TO PROVIDE ME WITH THE TRADE SETUPS.
""",
    "response_format": """Response format: You MUST ALWAYS ALWAYS ALWAYS ALWAYS ALWAYS respond with a single list of JSONs with the following structure (one JSON for each trade setup) at the end of your response:
[
    {
        "stock": "AAPL",
        "entry_point": 150.00,
        "stop_loss": 145.00,
        "stop_loss_limit": 144.50,
        "target_price": 160.00,
        "expected_duration": "5 days",
        "position_size": 100,
        "potential_profit_loss": 1000,
        "risk_reward_ratio": 2.0,
        "reason": "High RSI and MACD crossover indicate strong upward momentum"
    }
]
""",
    "prompt_name": "Deep Technical Analysis",
    "model_name": "Claude 3.7 Sonnet",
    "tool_name": "Code: Technical Indicators"
}

RETURN_JSON_PROMPT = {
    "prompt": """You have not responded with the required JSON format.
Please ensure that your response includes a single list of JSONs with the following structure at the end of your response:
[
    {
        "stock": "AAPL",
        "entry_point": 150.00,
        "stop_loss": 145.00,
        "stop_loss_limit": 144.50,
        "target_price": 160.00,
        "expected_duration": "5 days",
        "position_size": 100,
        "potential_profit_loss": 1000,
        "risk_reward_ratio": 2.0,
        "reason": "High RSI and MACD crossover indicate strong upward momentum"
    }
]""",
    "prompt_name": "Respond with JSON",
    "model_name": "Claude 3.7 Sonnet",
    "tool_name": "Code: Technical Indicators"
}