import aiohttp
import re
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from investpy import economic_calendar
from datetime import datetime, timedelta

class DataFetcher:
    """
    Handles all the data fetching operations, whether synchronous or asynchronous.
    - Responsible for fetching data from various sources.
    """

    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def fetch_html_async(self, url: str, headers: dict = None) -> str:
        """
        Fetches HTML content asynchronously from a given URL.
        """
        async with self.session.get(url, headers=headers) as response:
            response.raise_for_status()  # Raises an exception for 4XX/5XX responses
            return await response.text()

    def fetch_html(self, url: str, headers: dict = None) -> str:
        """
        Fetches HTML content synchronously from a given URL.
        """
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for 4XX/5XX responses
        return response.content

    def fetch_market_data(self, ticker: str, start_date: str, end_date: str, interval: str = '1d'):
        """
        Fetches historical market data for a given ticker symbol from Yahoo Finance.
        """
        return yf.download(ticker, start=start_date, end=end_date, interval=interval)

    async def fetch_json_async(self, url: str, headers: dict = None, params: dict = None) -> dict:
        """
        Fetches JSON data asynchronously from a given API endpoint.
        """
        async with self.session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            return await response.json()

    def fetch_json(self, url: str, headers: dict = None, params: dict = None) -> dict:
        """
        Fetches JSON data synchronously from a given API endpoint.
        """
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    async def close_session(self):
        """
        Closes the asynchronous session.
        """
        await self.session.close()


    def get_historical_economic_calendar(self, event_filter: re.Pattern = None):
            """
            Get historical economic calendar (as old as possible).
            
            Parameters:
            event_filter (re.Pattern): A regex pattern to filter events. 
                                    If provided, only events matching the pattern will be returned.

            Example:
            If you want to filter events related to 'GDP', you can pass:
            event_filter = re.compile(r'GDP')
            This will return only events with 'GDP' in their description.
            
            Returns:
            List[dict]: A list of dictionaries containing historical economic events.
            """
            today = datetime.now()
            five_years_ago = today - timedelta(days=365 * 5)  # 5 Years ago, let's try this 
            eco_calendar = economic_calendar(from_date=five_years_ago.strftime("%d/%m/%Y"), to_date=today.strftime("%d/%m/%Y"))

            # Apply filter to row 'event'
            if event_filter:
                eco_calendar = [row for row in eco_calendar if event_filter.search(row['event'])]

            return eco_calendar

if __name__ == "__main__":
    # Example usage if needed 
    data_fetcher = DataFetcher()
    pattern = re.Pattern(r"")
