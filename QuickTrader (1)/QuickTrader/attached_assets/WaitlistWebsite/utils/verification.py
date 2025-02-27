import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from typing import Tuple

class Verification:
    def __init__(self):
        self.twilio_client = Client(
            os.environ['TWILIO_ACCOUNT_SID'],
            os.environ['TWILIO_AUTH_TOKEN']
        )
        self.smtp_username = os.environ['SMTP_USERNAME']
        self.smtp_password = os.environ['SMTP_PASSWORD']
        
    def _generate_otp(self) -> str:
        return str(random.randint(100000, 999999))
    
    def send_sms_otp(self, phone_number: str) -> Tuple[bool, str, str]:
        try:
            otp = self._generate_otp()
            message = self.twilio_client.messages.create(
                body=f"Your Velasa Trading verification code is: {otp}",
                from_=os.environ['TWILIO_PHONE_NUMBER'],
                to=phone_number
            )
            return True, otp, "OTP sent successfully"
        except Exception as e:
            return False, "", f"Failed to send OTP: {str(e)}"
    
    def send_email_verification(self, email: str, verification_link: str) -> Tuple[bool, str]:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = email
            msg['Subject'] = "Verify your Velasa Trading Account"
            
            body = f"""
            <html>
            <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #FFD700;">Welcome to Velasa Trading</h2>
                <h3 style="color: #666;">A JRP GROUPS OF INDUSTRIES Company</h3>
                <p>Thank you for choosing Velasa Trading. To complete your registration, please verify your email address by clicking the button below:</p>
                <a href="{verification_link}" style="background-color: #FFD700; color: #000; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">
                    Verify Email
                </a>
                <p style="color: #666; font-size: 12px;">
                    If you didn't create an account with Velasa Trading, please ignore this email.
                </p>
                <hr>
                <p style="color: #999; font-size: 11px;">
                    © 2025 Velasa Trading - JRP GROUPS OF INDUSTRIES. All rights reserved.
                </p>
            </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            return True, "Verification email sent successfully"
        except Exception as e:
            return False, f"Failed to send verification email: {str(e)}"
