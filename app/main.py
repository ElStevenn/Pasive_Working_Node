from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from routes import CVI, fear_greed, economic_calendar, google_authentication#, on_gain_data, sentiment_analysis
import os, aiofiles

app = FastAPI(
    title="Passive Income Node",
    description="API for passive income project",
    version="1.1",
    contact={
        "name": "Pau Mateu",
        "email": "paumat17@gmail.com",
    }
)

app.mount("/mini_frontend", StaticFiles(directory="mini_frontend"), name="mini_frontend")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    path = os.path.join(os.getcwd(), "mini_frontend/index.html")
    async with aiofiles.open(path) as f:
        content = await f.read()
    return HTMLResponse(content)

@app.get("/economic_calendar", response_class=HTMLResponse, include_in_schema=False)
async def economic_calendar_():
    path = os.path.join(os.getcwd(), "mini_frontend/economic_calendar.html")
    async with aiofiles.open(path) as f:
        content = await f.read()
    return HTMLResponse(content) 

@app.get("/cucker_laverage", response_class=HTMLResponse, include_in_schema=False)
async def laverage_cuck_page():
    path = os.path.join(os.getcwd(), "mini_frontend/leverage_cuck.html")
    async with aiofiles.open(path) as f:
        content = await f.read()
    return HTMLResponse(content)

"""Call each route"""
app.include_router(CVI.router, prefix="")
app.include_router(fear_greed.router, prefix="")
app.include_router(economic_calendar.router, prefix="")
app.include_router(google_authentication.router, prefix="")
# app.include_router(on_gain_data.router, prefix="/on-gain-data")
# app.include_router(sentiment_analysis.router, prefix="/sentiment-analysis")

if __name__ == "__main__":
    import uvicorn, socket; hostname = socket.gethostname()
    if hostname == 'node5':
        # Correct paths to SSL certificates relative to /app directory
        path_ssl_keyfile = "/home/ubuntu/Pasive_Working_Node/app/certificates/privkey.pem"
        path_ssl_certificate = "/home/ubuntu/Pasive_Working_Node/app/certificates/fullchain.pem"
    

        # Run Uvicorn with SSL certificates
        uvicorn.run(app, host="0.0.0.0", port=443, ssl_keyfile=path_ssl_keyfile, ssl_certfile=path_ssl_certificate)
    else:
        # Run without SSL
        uvicorn.run(app, host="0.0.0.0", port=80)