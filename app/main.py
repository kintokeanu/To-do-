from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .celery_config import celery_app, check_reminders
from .twilio_integration import send_whatsapp_notification
from .database import connect_to_mongodb, close_mongodb_connection
from .routes import auth, reminders, trash
from datetime import datetime, timedelta
from .config import settings
import asyncio
from .database import database


app = FastAPI()

app.include_router(auth.router)
app.include_router(reminders.router)
app.include_router(trash.router)


# Interval function to check reminders and send notifications
async def check_reminders_interval():
    while True:
        reminders = await database.client[settings.MONGODB_NAME].reminders.find({"isReminded": False}).to_list(None)
        now = datetime.utcnow()
        
        for reminder in reminders:
            print("processing reminder:", reminder)
            remind_at = reminder["remind_at"]
            if remind_at <= now:
                send_whatsapp_notification(reminder["title"])  # Call Twilio integration function
                await database.client[settings.MONGODB_NAME].reminders.update_one(
                    {"_id": reminder["_id"]},
                    {"$set": {"isReminded": True}}
                )
        
        await asyncio.sleep(60)  # Check every 60 seconds

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongodb()
    asyncio.create_task(check_reminders_interval())

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongodb_connection()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to my app"}

if __name__ == "__main__":
    celery_app.start()
