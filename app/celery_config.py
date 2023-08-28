from celery import Celery
from datetime import datetime
from pytz import timezone

app_timezone = timezone('GMT')  # Set your desired time zone here


celery_app = Celery(
    'celery_tasks',
    broker='pyamqp://guest@localhost//',  # Update with your broker URL
    backend='',
)

@celery_app.task
def check_reminders():
    # Import Reminder model here (if not already imported)
    from app.schemas import reminder
    print("celery task executing")
    current_time = datetime.now(app_timezone)
    
    # Query for reminders that need to be reminded
    reminders_to_remind = reminder.objects(
        remind_at__lte=current_time,
        is_reminded=False,
    )
    
    for reminder in reminders_to_remind:
        print("Processing reminder:", reminder)
   
        reminder.is_reminded = True
        reminder.save()

        print("Whatsapp notification sent for reminder", reminder)
    
    print("celery task finished")

# Schedule the task to run periodically
celery_app.conf.beat_schedule = {
    'check-reminders-every-1-minute': {
        'task': 'celery_tasks.check_reminders',
        'schedule': 60.0,  # Interval in seconds
    },
}
