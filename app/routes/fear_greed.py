from fastapi import APIRouter, Depends, HTTPException, responses
from services.fear_greed.fear_greed_bot import Fear_Greed_Index
from services.fear_greed.bot import fear_greed_job
from services.database import crud
import uuid, asyncio
from typing import Literal

router = APIRouter(
    prefix="/fear_greed",
    tags=["Fear_And_Greed"],
    responses={404: {"description": "Not found"}},
)

fear_greed = Fear_Greed_Index()
# client = docker.from_env()
# docker_container =  client.containers.get('fear_greed_v1')


@router.get("/")
async def see_status():
    conf_status = await fear_greed.conf_status()
    bot_id = await fear_greed.get_conf_bot_id()
    description = await fear_greed.get_description()

    return {"description": description, "status": conf_status, "bot_id": bot_id}

@router.post("/suscribe/{user_id}/{level}", description="Suscribe or update a user in ")
async def suscribe_new_user(user_id: uuid.UUID, level):
    try:
        result = await crud.fear_greed_add_new_subscriber(user_id=user_id, level=int(level))

        return result
    except ValueError:
        return {"status": "error", "message": f"level {level} does not exsit!"}

@router.delete("/unsubscribe/{user_id}", description="Unsubscribe a user of fear and greed service")
async def unsubscribe_user(user_id: uuid.UUID):
    result = await crud.fear_greed_delete_subscriber(user_id=user_id)
    return result

@router.get("/get_subscribers", description="Get all subscribers subscrived to F&G and recive notifications")
async def get_fng_subscribers():
    subscribers = await crud.get_subscribers()
    return subscribers

@router.put("/run", description="Start fear and greed bot (admin mode)")
async def run_fear_and_greed_bot():
    response = await fear_greed.run_fear_and_greed_bot()
    
    return response

@router.delete("/stop", description="Stop fear and greed bot (Admin mode)")
async def stop_fear_and_greed_bot():
    response = await fear_greed.stop_fear_and_greed_bot()
    return response

@router.patch("/restart", description="Restart Fear And Greed bot (administrative bot)")
async def restart_fear_and_greed_bot():
    response = await fear_greed.restart_fear_and_greed_bot()
    return response
    

@router.get("/get_historical_notifications", description="Not avariable in this version")
async def get_cvo():
    return {"response": "Not avariable at this moment :("}

# NEVER CALL THIS
@router.put("/run_bot", description="Internal Router to run the bot.\n\n **Never call this endpoint, only will be called from the schedule node**", include_in_schema=True)
async def run_bot():
    try:
        if await fear_greed.conf_status() == "running":
            task = asyncio.create_task(fear_greed_job())
            await task
            return {"status": "success", "response": "today's job is running sucessfully!"}
        else:
            return {"status": "error", "error": "The bot is stopped, so it's not possible to run today's job"}
    except Exception as e:
        return {"status": "error", "error": f"An error ocurred while running the bot"}

@router.get("/last_analysis", description="Get last analysis")
async def get_last_analysis():
    last_analysis = await fear_greed.get_today_analysis()
    if last_analysis:
        return {"status": "success", "response": last_analysis}
    else:
        return {"status": "error", "response": "There is no analysis"}

@router.get("/get_today_analysis")
async def get_today_analysis():
    try:
        today_analysys = await fear_greed.get_today_analysis()

        return {"status":"success", "result": today_analysys}
    except Exception as e:
        return {"status": "error", "error": f"An error ocurred: {e}"}

