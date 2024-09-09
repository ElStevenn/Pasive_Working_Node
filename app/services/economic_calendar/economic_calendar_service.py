import numpy as np
import pandas as pd
import aiohttp, asyncio, aiofiles
import sys, os, json, re
import time
from datetime import datetime, timedelta
from fastapi import HTTPException
from functools import wraps
from investpy import *
from dotenv import load_dotenv

load_dotenv()

def metadata_handle(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_metadata = os.path.join(script_dir, 'metadata.json')

        if not file_metadata:
            raise FileNotFoundError("File 'metadata.json' does not exsit! Create it please")

        async with aiofiles.open(file_metadata, mode='r') as session:
            content = await session.read()
            metadata_file = json.loads(content)
        
        result = await func(self, metadata_file, *args, **kwargs)

        async with aiofiles.open(file_metadata, mode='w') as session:
            await session.write(result)
        
        return result
    return wrapper

KEY_EVENTS = ["CPI", "PPI", "GDP", "FOMC", "NFP", "ISM", "CFTC", "Retail Sales", "PMI", "Unemployment Rate", "Interest Rate Decision", "Jobless Claims", "Durable Goods Orders", "Trade Balance", "Housing Starts", "Consumer Confidence", "Industrial Production", "Manufacturing PMI", "Services PMI", "Federal Budget", "Existing Home Sales", "New Home Sales", "Construction Spending", "Core Inflation Rate", "Factory Orders", "Labor Force Participation Rate", "Personal Income", "Personal Spending", "Core PCE Price Index", "Initial Jobless Claims", "Continuing Jobless Claims", "Treasury Budget", "Import Price Index", "Export Price Index", "Producer Prices", "Capacity Utilization", "Current Account Balance"]
COUNTRIES = ["USD", "EUR", "GBP", "JPY", "CNY", "AUD", "NZD", "CHF", "CAD", "RUB", "BRL", "INR", "KRW", "MXN", "ZAR"]

class EconomicCalendarData():
    def __init__(self):
        self._script_dir = os.path.dirname(os.path.abspath(__file__))
        self._conf_file = os.path.join(self._script_dir, 'important_events.json')
        self._shedule_ip = os.getenv('SCHEDULE_NODE_IP')
        self._ip_server = "https://" + str(os.getenv('SERVER_IP'))

        if not self._conf_file:
            raise FileNotFoundError("File 'important_events.json' does not exsit! Create it please")

    @metadata_handle
    async def add_new_event_to_triger(self, metadata_file, execute_at):
        url = self._shedule_ip + "/schedule_one_time"
        data = {
            "url": "string",
            "method": "post",
            "data": {

            },
            "headers": {},
            "execute_at": execute_at
        }
        async with aiohttp.ClientSession(url=url, json=data) as session:
            async with session.post(url) as response:
                pass
            
    @metadata_handle
    async def trigger_event_alert(self, event: str, event_time: str):
        time_format = ""
        
        

        pass

    @property
    def important_events(self):
        return json.loads(open(self._conf_file).read())

    async def dialy_job(self):
        important_events = self.get_today_important_events()
        relevant_data = await self.get_relevant_data()


    async def add_new_relevant_country(self, country:  str):
        pass

    async def delete_relevant_coutry(self, country: str):
        pass

    def get_today_important_events(self):
        """Get today important events"""
        economic_events = ["GDP Release", "Unemployment Rate", "CPI", "Federal Reserve Meeting", "Non-Farm Payrolls", "Retail Sales Data", "ISM Manufacturing PMI", "Trade Balance", "Consumer Confidence Index", "PPI (Producer Price Index)", "Interest Rate Decision"]
        from_countries = ["USD", "JPY", "GBP", "EUR"]

        # Get today's data
        df_today = economic_calendar(); print(df_today)

        # Filter rows matching the economic events and countries
        filtered_df = df_today[
            df_today['event'].str.extract('|'.join(economic_events), na=False) & 
            df_today['currency'].isin(from_countries) %
            df_today['importance'].str.extract('high', case=False, na=False)
            ]

        if filtered_df.shape[0]:
            return None
        return filtered_df

    async def get_relevant_data(self):
        """Migrate this in on chain data later since it's its competency"""
        
        # 1: Get this week data
        pass
    

    def has_time_passed(self, time_str, tz = None):
        time_format = "%H:%M"
        current_time = datetime.now(tz=tz).strftime(time_format)
        return current_time > time_str

    async def create_alert_datetime(self, user_id, alert_name, previous_value, zone, event_execution: datetime, alert_id, timezone):
        """Create alert for economic calendar for today"""
        # Get hour trigger event
        trigger_event = event_execution - timedelta(minutes=1)

        # Prepare data payload
        data = {
            "url": f"{self._ip_server}/economic_calendar/trigger_alert",
            "method": "patch",
            "data": {
                "user_id": user_id,
                "event_name": alert_name,
                "previous_value": previous_value,
                "zone": zone,
                "event_execution": event_execution.isoformat(),
                "alert_id": alert_id,
                "timezone": timezone
            },
            "headers": {'Content-Type': 'application/json'},
            "timezone": timezone,
            "task_datetime": trigger_event.isoformat(),
        }

        # Make asynchronous HTTP request using aiohttp
        async with aiohttp.ClientSession() as session:
            url = f"http://{self._shedule_ip}/schedule_datetime"
            print(url)

            # Use json=data to serialize the dictionary to JSON
            async with session.post(url, json=data) as result:
                response = await result.json()
                if result.status in [404, 400, 500, 401]:
                    return HTTPException(status_code=400, detail=f"An error occurred: {response}")

                if result.status == 422:
                    raise HTTPException(status_code=404, detail=f"It seems like the task cannot be processed: {response}")

                return {"status": "success", "response": f"The alert {alert_name} has been correctly scheduled for {event_execution}", "task_id": response["task_id"]}


    def get_event_execution_and_previous_value(self, event_name: str, timezone: str = None, zone: str = None) -> tuple[str, str, str]:
        """Get event execution (as datetime) and event value"""
        today = datetime.combine(datetime.today(), datetime.min.time())
        _10_days = (today + timedelta(10))
        
        try:
            df_10_days = economic_calendar(time_zone=timezone, from_date=today.strftime("%d/%m/%Y"), to_date=_10_days.strftime("%d/%m/%Y"))
        except ValueError as e:
            if "time_zone does not exist" in str(e):
                timezone = None
                df_10_days = economic_calendar(time_zone=timezone, from_date=today.strftime("%d/%m/%Y"), to_date=_10_days.strftime("%d/%m/%Y"))
            else:
                raise e

        df_10_days.to_csv("delete_this.csv")  # Debugging purpose


        row = df_10_days[df_10_days['event'].str.replace("  ", " ") == event_name]
        if row.empty:
            row = df_10_days[df_10_days['event'] == event_name]
        
        if zone:
            # Further filter by zone if provided
            row = row[row['zone'] == zone]

        print(row)

        if row.empty:
            raise HTTPException(status_code=404, detail=f"Event {event_name} not found")

        if len(row) > 1:
            raise HTTPException(status_code=400, detail=f"Multiple events found for {event_name} in zone {zone}. We need more hits like zone!")

        # Ensure single row selection
        row = row.iloc[0]

        time_execution = row['time']
        previous_value = row['previous'] or ''
        date_execution = row['date']

        # Check 'actual' value and raise exception if None
        if row['actual'] is not None:
            raise HTTPException(status_code=400, detail=f"The time has expired ({time_execution}), and couldn't be scheduled, the final value was {row['actual']}")

        if not isinstance(previous_value, str):
            previous_value = "NaN"
        
        return time_execution, previous_value, date_execution

        
    async def trigger_event(self, event_name, user_email):
        """Add description here"""
        max_time = 60 * 5 # 5 minutes 
        while True:


            time.sleep(1)
            max_time -1
            break

    async def get_alert_value(self, event_name):
        pass

    async def send_notification(self, user_email, subject, description):
        pass
    
    


async def main():
    economic_calendar = EconomicCalendarData()
    
    event = "Irish Retail Sales (YoY)  (Jul)"
    zone = "ireland"; timezone = "Europe/Amsterdam"

    res = economic_calendar.get_event_execution_and_previous_value(event_name=event, timezone=timezone, zone=zone)

    print(res)

    """
    execution = datetime.now() + timedelta(minutes=60)
    res = await economic_calendar.create_alert_datetime("user_id", "alert_name", "previous_value", "zone", execution, "alert_id", "Europe/Amsterdam")
    print(res)
    """


if __name__ == "__main__":
    asyncio.run(main())
    # eco_calendar = EconomicCalendarData()
    
