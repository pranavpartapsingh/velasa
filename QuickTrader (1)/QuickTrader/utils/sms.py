import os
from twilio.rest import Client
import random

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def send_verification_code(phone_number: str) -> str:
    """Send verification code via SMS"""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Generate verification code
    verification_code = str(random.randint(100000, 999999))
    
    message = client.messages.create(
        body=f"Your Velasa Trading verification code is: {verification_code}",
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    
    return verification_code
