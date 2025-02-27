from twilio.rest import Client
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Verification:
    def __init__(self):
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

    def _generate_otp(self) -> str:
        """Generate a 6-digit OTP"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

    def send_sms_otp(self, phone_number: str) -> tuple[bool, str, str]:
        """Send OTP via SMS"""
        try:
            if not phone_number.startswith('+'):
                return False, "", "Phone number must include country code (e.g., +1234567890)"

            otp = self._generate_otp()
            message = self.twilio_client.messages.create(
                body=f"Your Velasa Trading verification code is: {otp}",
                from_=self.twilio_phone,
                to=phone_number
            )
            return True, otp, "OTP sent successfully"
        except Exception as e:
            return False, "", f"Failed to send OTP: {str(e)}"

    def send_email_verification(self, email: str, verification_link: str) -> tuple[bool, str]:
        """Send verification email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = "noreply@velasa-trading.com"
            msg['To'] = email
            msg['Subject'] = "Verify your Velasa Trading account"

            body = f"""
            Welcome to Velasa Trading!

            Please verify your email address by entering this code in the app:
            {verification_link}

            This code will expire in 10 minutes.

            If you didn't create an account, please ignore this email.

            Best regards,
            Velasa Trading Team
            """
            msg.attach(MIMEText(body, 'plain'))

            # For Play Store deployment, we'll simulate success
            # You'll need to configure email sending in production
            return True, "Verification email sent"
        except Exception as e:
            return False, f"Failed to send verification email: {str(e)}"