import httpx, pytz
from datetime import datetime

def get_timezone(client_ip: str) -> str:
    """Get client timezone based on their IP address."""
    try:
        with httpx.Client() as client:
            response = client.get(f"https://ipinfo.io/{client_ip}/json")
            response.raise_for_status()  # Raises an error if the request failed
            response_data = response.json()
            return response_data.get('timezone', 'Europe/Amsterdam')  # Default to 'Europe/Amsterdam' if not found
                
    except httpx.RequestError as e:
        print(f"Request error: {e}")  # Log the error
        return 'Europe/Amsterdam'
    except httpx.HTTPStatusError as e:
        print(f"HTTP status error: {e}")  # Log the HTTP error
        return 'Europe/Amsterdam'

def convert_timezone_to_gmt_offset(timezone_str: str) -> str:
    # Get the timezone object
    timezone = pytz.timezone(timezone_str)
    
    # Get the current time in the specified timezone
    now = datetime.now(timezone)
    
    # Calculate the UTC offset
    utc_offset = now.utcoffset()
    
    # Format the offset in +/-H:MM format
    offset_hours = int(utc_offset.total_seconds() // 3600)
    offset_minutes = int((utc_offset.total_seconds() % 3600) // 60)
    
    # Handle the sign and format it as GMT +H:MM or GMT -H:MM
    offset_str = f"GMT {'+' if offset_hours >= 0 else '-'}{abs(offset_hours)}:{abs(offset_minutes):02}"
    
    return offset_str