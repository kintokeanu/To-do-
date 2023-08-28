from fastapi import APIRouter, Depends, HTTPException
from ..database import database
from ..config import settings
from bson import ObjectId

router = APIRouter(
    prefix='/trash',
    tags=['Trash']
)

# Move a reminder to trash
@router.put("/{reminder_id}", response_model=dict)
async def move_to_trash(reminder_id: str):
    # Get the reminder from the database
    reminder = await database.client[settings.db_name].reminders.find_one({"_id": ObjectId(reminder_id)})
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Update the reminder to mark it as in trash
    updated_reminder = await database.client[settings.db_name].reminders.find_one_and_update(
        {"_id": ObjectId(reminder_id)},
        {"$set": {"in_trash": True}},
        return_document=True
    )
    if not updated_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder moved to trash"}

# Clear the trash
@router.delete("/", response_model=dict)
async def clear_trash():
    deleted_count = await database.client[settings.db_name].reminders.delete_many({"in_trash": True})
    return {"message": f"{deleted_count.deleted_count} reminders cleared from trash"}
