from twilio.rest import Client


# Twilio credentials
TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''

# Twilio phone number and recipient number
TWILIO_PHONE_NUMBER = ''
RECIPIENT_PHONE_NUMBER = '+254718897015'

def send_whatsapp_notification(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=RECIPIENT_PHONE_NUMBER
        )
        print("WhatsApp notification sent:", message.sid)
    except Exception as e:
        print("Error sending WhatsApp notification:", str(e))
