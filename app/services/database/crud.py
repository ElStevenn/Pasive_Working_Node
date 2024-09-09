from .database import async_engine
from .models import *
from sqlalchemy import select, update, insert, delete, join
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError
from fastapi import HTTPException
from typing import List, Literal, Optional
from datetime import timedelta, datetime, timezone
import asyncio
import numpy as np
import uuid


def db_connection(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with AsyncSession(async_engine) as session:
            async with session.begin():
                try:                
                    result = await func(session, *args, **kwargs)
    
                    return result
                except OSError:
                    return {"status": "error", "error": "DB connection in the server does not work, maybe the container is not running or IP is wrong since you've restarted the node"}
                except Exception as e:
                    print("An error occurred:", e)
                    raise
    return wrapper

@db_connection
async def get_email_by_ids(session: AsyncSession, lists_ids: List[str]):
    list_emails = []

    for user_id in lists_ids:
        result = await session.execute(select(User).where(User.id == user_id))
        user_email = result.scalar_one_or_none()
        if user_email:
            list_emails.append(user_email.email)

    return list_emails


@db_connection
async def add_new_alerts(session: AsyncSession, alert_id: uuid.UUID,  user_ids: List[str], alert_execution: datetime, message: str, headline: Optional[str] = None, alert_type: Literal["normal", "advise", "recommendation", "alert", "notification"] = "normal"):
    for user_id in user_ids:
        new_alert = Alert(
            id=alert_id,
            user_id = user_id,
            execution_alert_datetime = alert_execution,
            type = alert_type,
            headline = headline,
            message = message
        )
        session.add(new_alert)
        await session.flush()
    

@db_connection
async def get_alerts(session: AsyncSession, alert_id: str):
    result = await session.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    return alert

@db_connection
async def delete_alert(session: AsyncSession, alert_id: str):
    result = await session.execute(delete(Alert).where(Alert.id == alert_id))
    deleted_alert = result.scalar_one_or_none()

    if deleted_alert:
        return {"status": "sucess", "response": f"Alert {alert_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

@db_connection
async def fear_greed_add_new_subscriber(session: AsyncSession, user_id: str, level: Literal[1, 2, 3]):
    """Add new subscriber to fear and greed index"""
    res = await session.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} does not exist"
        )

    res = await session.execute(select(FearGreedSubscription).where(FearGreedSubscription.user_id == user_id))
    subscriber = res.scalar_one_or_none()

    if subscriber:
        await session.execute(update(FearGreedSubscription).where(FearGreedSubscription.user_id == user_id).values(level=level))
        return {"status": "success", "response": f"Level updated to {level}"}
    else:
        new_subscriber = FearGreedSubscription(
            user_id=user_id,
            level=level
        )

        session.add(new_subscriber)
        await session.flush()

        return {"status": "success", "response": "new user added successfully!"}


@db_connection
async def fear_greed_delete_subscriber(session: AsyncSession, user_id: uuid.UUID):
    """Delete a subscriber of fear and greed bot"""
    result = await session.execute(delete(FearGreedSubscription).where(FearGreedSubscription.user_id == user_id))
    await session.flush()

    if result.rowcount > 0:
        return {"status": "success", "response": f"User {user_id} has been deleted"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} does not exist"
        )

@db_connection
async def get_users_list(session: AsyncSession, level: int):
    """Get all the user emails from the list"""
    result = await session.execute(
        select(User.email)
        .join(FearGreedSubscription, FearGreedSubscription.user_id == User.id)
        .where(FearGreedSubscription.level == level)
    )
    
    users = np.array([user[0] for user in result.all()])

    return users

@db_connection
async def add_new_user_alert(session: AsyncSession, user_id: uuid.UUID, notification: dict):
    """Add new notification"""
    result = await session.execute(
        select(EconomicCalendarAlerts)
        .where(EconomicCalendarAlerts.user_id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        new_economic_sub = EconomicCalendarAlerts(
            user_id=user_id,
            event_alerts=[notification]
        )
        session.add(new_economic_sub)
        await session.flush()
    else:
        user.event_alerts.append(notification)
        await session.execute(
            update(EconomicCalendarAlerts)
            .where(EconomicCalendarAlerts.user_id == user_id)
            .values(event_alerts=user.event_alerts)
        )



@db_connection
async def get_user_data(session: AsyncSession, user_id: str):
    # Validate the UUID format
    try:
        uuid_obj = uuid.UUID(user_id)
    except ValueError:
        # If the UUID is invalid, return None
        return None

    result = await session.execute(
        select(User)
        .where(User.id == uuid_obj)
    )
    
    user = result.scalar_one_or_none()
    
    if user is not None:
        return {
            "user_id": user_id,      
            "username": user.username,
            "email": user.email,
        }
    else:
        return None

@db_connection
async def get_user_by_email(session: AsyncSession, user_email: str):
    result = await session.execute(select(User).where(User.email == user_email))
    db_user = result.scalar_one_or_none()

    if db_user:
        return db_user
    else:
        return None

@db_connection
async def create_user(session: AsyncSession, id: str, email: str, username: str, picture: str, country: str):
    # Set a default value for country if it's None
    if not country:
        country = "Unknown"

    user_db = User(
        id=id,
        username=username,
        password="oauth_passwd",
        email=email,
        country=country,
        picture=picture
    )
    session.add(user_db)
    await session.flush()

    return str(user_db.id)

@db_connection
async def set_user_token(session: AsyncSession, user_id: str, token: str, refresh_token: str, main_service: str):
    # Check if token already exists
    res = await session.execute(
        select(TokenHandle)
        .where(TokenHandle.user_id == user_id)
        )

    db_token = res.scalar_one_or_none()
    if not db_token:
        new_token = TokenHandle(
            user_id=user_id,
            oauth_token=token,
            refresh_token=refresh_token,
            main_service=main_service
        ) 
        session.add(new_token)
        await session.flush()

    else:
        await session.execute(
            update(TokenHandle)
            .where(TokenHandle.user_id == user_id)
            .values(oauth_token=token,refresh_token=refresh_token, main_service=main_service)
        )

   



@db_connection
async def get_subscribers(session: AsyncSession):
    """RETURN: user_id, email, username"""
    result = await session.execute(
        select(FearGreedSubscription)
    )
    
    subscribers = result.scalars().all()

    # Fetch user data without passing the level
    tasks = [
        get_user_data(str(subscriber.user_id)) 
        for subscriber in subscribers
    ]

    # Gather results
    user_data_list = await asyncio.gather(*tasks)

    # Combine user data with level
    final_result = [
        {**user_data, 'user_id': str(subscriber.user_id), 'level': subscriber.level}
        for user_data, subscriber in zip(user_data_list, subscribers)
    ]

    return final_result

@db_connection
async def add_new_error(session: AsyncSession, subject: str, text: str):
    """Add new error log"""
    new_error = ErrorsLogs(subject=subject, text=text)
    session.add(new_error)
    await session.flush()


@db_connection
async def create_new_alert(session: AsyncSession, user_id: str, alert_name: str, previous_value: str, zone: str, event_execution: datetime, timezone: str):
    """Create new alert as created"""
    new_alert = EconomicCalendarAlerts(
        user_id=user_id,
        status="scheduled",
        alert_name=alert_name,
        zone=zone,
        previous_value=previous_value,
        event_execution=event_execution,
        timezone=timezone
    )
    session.add(new_alert)
    await session.flush()

    return str(new_alert.id)


@db_connection
async def set_alet_as_created(session: AsyncSession, schedule_id, alert_id):
    """set alert as created"""
    res = await session.execute(
        update(EconomicCalendarAlerts)
        .where(EconomicCalendarAlerts.id == alert_id)
        .values(schedule_id=schedule_id, status="created")
    )

    await session.commit()
    return res.rowcount

@db_connection
async def set_alert_as_executed(session: AsyncSession, alert_id: str, value: str):
    """Updated the alert as executed and update its values"""
    res = await session.execute(
        update(EconomicCalendarAlerts)
        .where(EconomicCalendarAlerts.id == alert_id)
        .values(status="executed", value=value)
    )
    await session.commit()
    return res.rowcount

@db_connection
async def set_alert_as_failed(session: AsyncSession, alert_id: str):
    """Set an event as failed"""
    res = await session.execute(
        update(EconomicCalendarAlerts)
        .where(EconomicCalendarAlerts.id == alert_id)
        .values(status="failed")
    )
    await session.commit()
    return res.rowcount

@db_connection
async def delete_expired_events(session: AsyncSession, days_ago: int):
    """Delete events that are older than a given number of days. This is executed daily to clean the DB."""
    
    res = await session.execute(
        delete(EconomicCalendarAlerts)
        .where(EconomicCalendarAlerts.event_execution < (datetime.now(timezone.utc) - timedelta(days=days_ago)))
    )
    await session.commit()
    return res.rowcount


@db_connection
async def get_all_alerts_from_user(session: AsyncSession, user_id: str):
    """Get all the current alerts from a specific user"""
    res = await session.execute(
        select(
            EconomicCalendarAlerts.user_id, 
            EconomicCalendarAlerts.status, 
            EconomicCalendarAlerts.alert_name, 
            EconomicCalendarAlerts.previous_value, 
            EconomicCalendarAlerts.event_execution 
        ).where(EconomicCalendarAlerts.user_id == user_id)
    )

    alerts = res.fetchall()

    # Return a list of dictionaries with relevant alert information
    return [
        {
            'user_id': alert.user_id,
            "alert_id": alert.id,
            'status': alert.status,
            'alert_name': alert.alert_name,
            'previous_value': alert.previous_value,
            'event_execution': alert.event_exevution
        }
        for alert in alerts
    ]






async def main_testing():
    user_id = "53f22083-76f4-43fd-ad6d-d35de69791ee"
    result = await get_subscribers()
    print(result)

if __name__ == "__main__":
    asyncio.run(main_testing())