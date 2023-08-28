from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from typing import List
from ..schemas.reminder import ReminderCreate, Reminder, ReminderUpdate
from ..database import database
from ..config import settings
from ..celery_config import celery_app, check_reminders
from ..twilio_integration import send_whatsapp_notification

router = APIRouter(
    prefix='/reminders',
    tags=['Reminders']
)

# Create a reminder
@router.post("/addReminder", response_model=Reminder)
async def create_reminder(reminder_data: ReminderCreate):
    reminder = reminder_data.dict()
    reminder["user_id"] = "user_id_here"  # Replace with actual user ID
    result = await database.client[settings.MONGODB_NAME].reminders.insert_one(reminder)
    reminder["id"] = str(result.inserted_id)
    return reminder

@router.get("/getAllReminder", response_model=List[Reminder])
async def get_all_reminders():
    reminders = await database.client[settings.MONGODB_NAME].reminders.find().to_list(length=None)
    for reminder in reminders:
        reminder["id"] = str(reminder.pop("_id"))
    return reminders

@router.get("/search", response_model=List[Reminder])
async def search_reminders(search_query: str):
    reminders = await database.client[settings.MONGODB_NAME].reminders.find({
        "$or": [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"description": {"$regex": search_query, "$options": "i"}},
        ]
    }).to_list(length=None)
    for reminder in reminders:
        reminder["id"] = str(reminder["_id"])
    return reminders

@router.get("/{reminder_id}", response_model=Reminder)
async def get_reminder(reminder_id: str):
    reminder = await database.client[settings.MONGODB_NAME].reminders.find_one({"_id": ObjectId(reminder_id)})
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    reminder["id"] = str(reminder["_id"])
    return reminder

@router.put("/{reminder_id}", response_model=Reminder)
async def update_reminder(reminder_id: str, reminder_data: ReminderUpdate):
    updated_reminder = await database.client[settings.MONGODB_NAME].reminders.find_one_and_update(
        {"_id": ObjectId(reminder_id)},
        {"$set": reminder_data.dict()},
        return_document=True
    )
    if not updated_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    updated_reminder["id"] = str(updated_reminder["_id"])
    return updated_reminder

@router.delete("/{reminder_id}", response_model=dict)
async def delete_reminder(reminder_id: str):
    deleted_reminder = await database.client[settings.MONGODB_NAME].reminders.find_one_and_delete({"_id": ObjectId(reminder_id)})
    if not deleted_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder deleted"}

# # Integrate Celery periodic task to check reminders
# @celery_app.task(name="check_reminders_task", bind=True)
# def check_reminders_task(self):
#     reminders = database.client[settings.MONGODB_NAME].reminders.find({"isReminded": False})
#     for reminder in reminders:
#         if reminder["remind_at"] <= datetime.utcnow():
#             send_whatsapp_notification(reminder)  # Call Twilio integration function
#             database.client[settings.MONGODB_NAME].reminders.update_one(
#                 {"_id": reminder["_id"]},
#                 {"$set": {"isReminded": True}}
#             )
