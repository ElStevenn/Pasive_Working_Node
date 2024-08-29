from datetime import datetime, timedelta
import asyncio
import re

import aiohttp
import httpx
import numpy as np
import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from investpy import economic_calendar, get_stock_historical_data
from openai import OpenAI, AsyncOpenAI
from sklearn.linear_model import LinearRegression
from typing import Literal, Optional, List

from services.economic_calendar.economic_calendar_service import EconomicCalendarData

client = AsyncOpenAI()



def get_market_variation(from_date: datetime = None, to_date: datetime = None):
    tickers = {
        'S&P 500': '^GSPC',
        'Dow Jones Industrial Average (DJIA)': '^DJI',
        'NASDAQ Composite': '^IXIC',
        'Russell 2000': '^RUT',
        'FTSE 100': '^FTSE',
        'DAX': '^GDAXI',
        'Nikkei 225': '^N225',
        'Hang Seng Index': '^HSI'
    }

    if from_date is None or to_date is None:
        raise ValueError("Both from_date and to_date must be provided")

    from_date_str = from_date.strftime('%Y-%m-%d %H:%M:%S')
    to_date_str = to_date.strftime('%Y-%m-%d %H:%M:%S')

    variations = []
    for name, ticker in tickers.items():
        try:
            data = yf.download(ticker, start=from_date_str, end=to_date_str, interval='1m')
            if not data.empty:
                variation = data['Close'].pct_change().dropna().mean()
                variations.append(variation)
        except Exception as e:
            print(f"Failed to download data for {name}: {e}")

    if not variations:
        return 0

    average_variation = sum(variations) / len(variations)
    return average_variation


def make_summary(all_pages: List[str]):
    """
    NEEDED DATA: 
     - Let me know if you see some of these words -> ["CPI", "PPI", "GDP", "FOMC", "NFP", "ISM", "CFTC", "Retail Sales", "PMI", "Unemployment Rate", "Interest Rate Decision", "Jobless Claims", "Durable Goods Orders", "Trade Balance", "Housing Starts", "Consumer Confidence", "Industrial Production", "Manufacturing PMI", "Services PMI", "Federal Budget", "Existing Home Sales", "New Home Sales", "Construction Spending", "Core Inflation Rate", "Factory Orders", "Labor Force Participation Rate", "Personal Income", "Personal Spending", "Core PCE Price Index", "Initial Jobless Claims", "Continuing Jobless Claims", "Treasury Budget", "Import Price Index", "Export Price Index", "Producer Prices", "Capacity Utilization", "Current Account Balance"]
     - Important Countries involved over the last days with the crypto market
     - Bitcoin resistance levels (number output)
    """

    # Combine all pages content into a single string
    content = " | ".join(all_pages)

    # Words of interest
    key_words = ["CPI", "PPI", "GDP", "FOMC", "NFP", "ISM", "CFTC", "Retail Sales", "PMI", "Unemployment Rate", 
                 "Interest Rate Decision", "Jobless Claims", "Durable Goods Orders", "Trade Balance", "Housing Starts", 
                 "Consumer Confidence", "Industrial Production", "Manufacturing PMI", "Services PMI", "Federal Budget", 
                 "Existing Home Sales", "New Home Sales", "Construction Spending", "Core Inflation Rate", "Factory Orders", 
                 "Labor Force Participation Rate", "Personal Income", "Personal Spending", "Core PCE Price Index", 
                 "Initial Jobless Claims", "Continuing Jobless Claims", "Treasury Budget", "Import Price Index", 
                 "Export Price Index", "Producer Prices", "Capacity Utilization", "Current Account Balance"]

    # Check for key words in the content
    found_words = [word for word in key_words if word in content]
    
    # This assumes you have a method to get country mentions and Bitcoin resistance levels, otherwise, adjust accordingly
    important_countries = get_important_countries(content)
    bitcoin_resistance_levels = get_bitcoin_resistance_levels(content)
    
    # Generate a summary prompt based on the content and your requirements
    summary_prompt = (
        f"Make a summary of cryptocurrency based on these news articles. Focus on the following:\n"
        f"1. Mention of key economic indicators: {', '.join(found_words)}\n"
        f"2. Important countries involved in the last few days related to the crypto market: {', '.join(important_countries)}\n"
        f"3. Bitcoin resistance levels mentioned: {bitcoin_resistance_levels}\n"
        f"News content: {content}"
    )

    # Assuming you have a client object for interacting with OpenAI's API
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI specialized in creating concise and insightful summaries of cryptocurrency news."},
            {"role": "user", "content": summary_prompt}
        ]
    )

    return completion['choices'][0]['message']['content']

def get_important_countries(content: str) -> List[str]:
    # Implement logic to extract country mentions related to the crypto market
    # For now, returning a placeholder
    countries = ["USA", "China", "Germany", "Japan", "South Korea"]
    found_countries = [country for country in countries if country in content]
    return found_countries

def get_bitcoin_resistance_levels(content: str) -> str:
    """Get bitcoin resistance levels according to other analysis"""
    # Simple mock logic to extract resistance levels
    match = re.search(r"resistance at \$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", content, re.IGNORECASE)
    if match:
        return match.group(1)
    return "No specific resistance levels mentioned"

def filter_text(text: str):
    key_words = ["bitcoin"]
    if any(re.search(rf'\b{word}\b', text.lower()) for word in key_words):
        return text
    else:
        return None



async def fetch_important_events(client: AsyncOpenAI, text_element: str):
    completion = await client.chat.completions.create(
        model="gpt-4o",
         messages=[
            {"role": "system", "content": "You are a machine that is able to extract important events from a given text. Please return a JSON array of any important events detected, including those that are similar or related to the following: GDP Release, Unemployment Rate, CPI, Federal Reserve Meeting, Non-Farm Payrolls, Retail Sales Data, ISM Manufacturing PMI, Trade Balance, Consumer Confidence Index, PPI (Producer Price Index), Interest Rate Decision."},
            {"role": "user", "content": f"Analyze this text: {text_element} and return a JSON array of important or similar events mentioned in the text."}
        ],
        max_tokens=100,
    )
    
    # Extract the content and assume it's a JSON array
    content = completion # ['choices'][0]['message']['content'].strip()

async def get_important_events(client: AsyncOpenAI, text: List[str]):
    tasks = [fetch_important_events(client, element) for element in text]
    results = await asyncio.gather(*tasks)
    return results


    
    """
    # Pass the list of strings to the function
    result = await get_important_events(client, category_texts)
    print(result)
    """
    
async def generate_economic_event_dataset(event_name: str, country: str, timezone: str):
    """
     - Generate a dataset containing key economic event information from the current moment onwards.

    This function retrieves and compiles data related to a specified economic event from a particular country,
    within a specific timezone, starting from the current date and time. The dataset includes details such as the event's 
    execution time, the event name, the Fear & Greed (F&G) index value, the previous value associated with the event, 
    the forecast value, and the final value.

       - Example dataset returning value:

    | Execution Event   | Event Name        | F&G  | Previous Value | Forecast | Final Value |
    |-------------------|-------------------|------|----------------|----------|-------------|
    | 2024-08-10 09:00  | CPI Report        | 80   | 75.5           | 78.0     | 79.8        |
    | 2024-08-11 14:30  | Unemployment Rate | 85   | 80.2           | 82.0     | 83.7        |
    | 2024-08-12 16:45  | GDP Growth        | 90   | 88.1           | 89.0     | 90.5        |

    """
    
    

    pass



if __name__ == "__main__":
    asyncio.run(trading_view_news())
