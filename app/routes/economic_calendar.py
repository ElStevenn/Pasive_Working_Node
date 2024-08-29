from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Query
from pydantic import BaseModel
from typing import Literal, List, Optional
from investpy import economic_calendar
from dotenv import load_dotenv
from datetime import time, datetime
import uuid, os

from services.database import crud
from services.others import get_timezone, convert_timezone_to_gmt_offset
from services.economic_calendar.economic_calendar_service import EconomicCalendarData, KEY_EVENTS, COUNTRIES

load_dotenv()

router = APIRouter(
    prefix="/economic_calendar",
    tags=["Economic Calendar"],
    responses={404: {"description": "Not found"}},
)

economic_calendar_service = EconomicCalendarData()

class TriggerAlert(BaseModel):
    user_id: uuid.UUID
    event_name: str
    previous_value: str
    event_execution: datetime
    alert_id: str

class CreateAlert(BaseModel):
    user_id: str
    event_name: str
    zone: str
    # alert_type: str
    timezone: Optional[str] = None


# ECONOMIC CALENDAR ENDPOINTS V1

@router.post("/get_notified/{user_id}/{level}", deprecated=True, description="Not implementated in this version, basically is to be always notificated for every important event")
async def get_notified(user_id: uuid.UUID):
    return {"response": "not implemented in this version"}

@router.post("/create_alert", description="Create an alert")
async def create_alert(request: Request, request_data: CreateAlert, background_task: BackgroundTasks):
    try:

        if not request_data.timezone:
            client_ip = request.client.host
            client_timezone = get_timezone(client_ip)
        else:
            client_timezone = request_data.timezone

        # Get event execution and previous value
        time_execution, previous_value, date_execution = economic_calendar_service.get_event_execution_and_previous_value(request_data.event_name, client_timezone, request_data.zone)
        
        # Get datetime execution in datetetime and strftime format
        day, month, year = date_execution.split('/'); hour, minute = time_execution.split(":")
        datetime_execution = datetime(int(year), int(month), int(day), int(hour), int(minute))
        formatted_datetime = datetime_execution.strftime("%Y-%m-%dT%H:%M:%S%z")

        # Save this alert in the DB 
        alert_id = await crud.create_new_alert(
            user_id=request_data.user_id,
            alert_name=request_data.event_name,
            previous_value=previous_value,
            zone=request_data.zone,
            event_execution=datetime_execution,
            timezone=client_timezone
        )

        # Create Alert
        response = await economic_calendar_service.create_alert_datetime(
            user_id=request_data.user_id,
            alert_name=request_data.event_name,
            previous_value=previous_value,
            event_execution=datetime_execution,
            alert_id=alert_id,
            timezone=client_timezone
        )

        
        return response
    except KeyError:
        # Event doesn't exist
        raise HTTPException(
            status_code=404,
            detail=f"Event {request_data.event_name} doesn't exist"
        )


@router.get("/get_all_active_alerts/{user_id}", description="Get all active alerts for a user pendent to be triggered")
async def get_all_active_events(user_id: str):
    user_all_alerts = await crud.get_all_alerts_from_user(user_id)
    return user_all_alerts

@router.delete("/delete_alert/{alert_id}", description="Delete an alert using alert_id")
async def delete_an_alert(alert_id: str):
    result = await crud.delete_alert(alert_id=alert_id)
    return result

@router.get("/get_all_events_names", description="Get all key events that you can get notificated")
async def get_all_events():
    return {
        "key_events": KEY_EVENTS,
        "economic_calendar_countries": COUNTRIES
    }

@router.post("/get_always_notificated/{user_id}/{event_key}/{country}", description="")
async def get_always_notificated(user_id: uuid.UUID, event_key: Literal[tuple(KEY_EVENTS)], country: Optional[Literal[tuple(COUNTRIES)]] = None):
    
    # Insert this user into the table
    notification = {event_key: country if country else "NaN"}
    result = await crud.add_new_user_alert(user_id=user_id, notification=notification)

    return result

@router.get("/today_important_events", description="Return importants even of today (if is there)")
async def get_today_important_events():
    today_events = economic_calendar_service.get_today_important_events()
    if today_events.empty:
        return {}
    else:
        return today_events.to_dict()


@router.get("/today_events", description="Get all today events in json format")
async def get_today_events(request: Request, timezone: Optional[str] = Query(None)):
    if not timezone:
        client_ip = request.client.host
        client_timezone = get_timezone(client_ip)
    else:
        client_timezone = timezone

    # Convert the timezone to GMT offset format
    gmt_timezone = convert_timezone_to_gmt_offset(client_timezone)
    
    print(gmt_timezone)
    if gmt_timezone is None:
        gmt_timezone = "GMT" 

    try:
        events = economic_calendar(time_zone=gmt_timezone)
        events_list = events.to_dict(orient="records")
    except ValueError as e:
        return {"error": str(e)}

    result = []
    for event in events_list:
        if event.get('currency'):
            result.append({
                "id": event.get('id'), 
                "date": event.get('date'), 
                "time": event.get('time'), 
                "zone": event.get('zone'), 
                "currency": event.get('currency'), 
                "importance": event.get('importance'), 
                "event": event.get('event'), 
                "actual": event.get('actual'), 
                "previous": event.get('previous')
            })

    return result

@router.patch("/trigger_alert", description="Trigger an event so that the user can be notificated")
async def trigger_event_alert(request_boddy: TriggerAlert, background_task: BackgroundTasks):
    
    user_email = crud.get_user_data(user_id=request_boddy.user_id)

    background_task.add_task(await economic_calendar_service.trigger_event(event_name=request_boddy.event_name, user_email=user_email))

    return {"result": "sucess", "message": "the event is beeing triggering, i don't know whether or not it'll work"}


@router.delete("/delete_expired_events", description="**Internal endoint**", include_in_schema=True)
async def delete_expired_events():
    delete_lasts = int(os.getenv('DELETE_THE_LAST'))

    result = await crud.delete_expired_events(days_ago=delete_lasts)
    if result:
        return {"result": "sucess", "row_count": result, }
    return {"result": "error", "message": "unexpected error oucrred when deleting the expired events"}

# ULTRA OWN BOT PART
@router.get("/check_event", description="Check if today there is an important event")
async def check_if_today_there_is_any_event():
    return {"response": "under construction"}

