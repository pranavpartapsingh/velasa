import streamlit as st
import hashlib
import secrets
import time
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from utils.sms import send_verification_code
from utils.verification import Verification

class AuthManager:
    def __init__(self):
        if 'users' not in st.session_state:
            st.session_state.users = {}
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = {}
        if 'session_start' not in st.session_state:
            st.session_state.session_start = None
        if 'pending_verifications' not in st.session_state:
            st.session_state.pending_verifications = {}

        self.verification = Verification()

    def _generate_salt(self) -> str:
        return secrets.token_hex(16)

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000  # Increased iterations for security
        ).hex()

    def _check_password_strength(self, password: str) -> tuple[bool, str]:
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in password):
            return False, "Password must contain at least one special character"
        return True, ""

    def _validate_input(self, username: str, password: str, email: str = "", phone: str = "") -> tuple[bool, str]:
        if not username or not password:
            return False, "Username and password are required"
        if len(username) < 3 or len(username) > 50:
            return False, "Username must be between 3 and 50 characters"
        if not username.isalnum():
            return False, "Username must contain only letters and numbers"
        if email and not '@' in email:
            return False, "Invalid email address"
        if phone and not phone.startswith('+'):
            return False, "Phone number must include country code (e.g., +1234567890)"
        return True, ""

    def register(self, username: str, password: str, email: str, phone: str) -> tuple[bool, str]:
        # Input validation
        input_valid, input_msg = self._validate_input(username, password, email, phone)
        if not input_valid:
            return False, input_msg

        # Password strength check
        password_valid, password_msg = self._check_password_strength(password)
        if not password_valid:
            return False, password_msg

        if username in st.session_state.users:
            return False, "Username already exists"

        # Generate verification tokens
        email_token = secrets.token_urlsafe(32)
        phone_otp = self.verification._generate_otp()

        # Store pending verification
        st.session_state.pending_verifications[username] = {
            'email_token': email_token,
            'phone_otp': phone_otp,
            'email': email,
            'phone': phone,
            'expires_at': datetime.now() + timedelta(hours=24)
        }

        # Generate salt and hash password
        salt = self._generate_salt()
        password_hash = self._hash_password(password, salt)

        # Send verification email and SMS
        verification_link = f"https://velasa-trading.com/verify/email/{email_token}"
        email_success, email_msg = self.verification.send_email_verification(email, verification_link)
        sms_success, otp, sms_msg = self.verification.send_sms_otp(phone)

        if not email_success:
            return False, f"Failed to send verification email: {email_msg}"
        if not sms_success:
            return False, f"Failed to send verification SMS: {sms_msg}"

        st.session_state.users[username] = {
            'password_hash': password_hash,
            'salt': salt,
            'email': email,
            'phone': phone,
            'email_verified': False,
            'phone_verified': False,
            'portfolio': {'cash': 100000, 'positions': {}},
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        return True, "Registration initiated. Please check your email and phone for verification codes."

    def google_sign_in(self, email: str) -> tuple[bool, str]:
        """Simulated Google Sign In for mobile app"""
        if not email or not '@' in email:
            return False, "Invalid email address"

        # Generate username from email
        username = email.split('@')[0]
        base_username = username
        counter = 1

        # Ensure unique username
        while username in st.session_state.users:
            if st.session_state.users[username].get('google_user'):
                # Existing Google user - log them in
                st.session_state.current_user = username
                st.session_state.session_start = datetime.now()
                return True, "Welcome back!"
            username = f"{base_username}{counter}"
            counter += 1

        # Create new user
        st.session_state.users[username] = {
            'email': email,
            'google_user': True,
            'email_verified': True,
            'portfolio': {'cash': 100000, 'positions': {}},
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat()
        }

        st.session_state.current_user = username
        st.session_state.session_start = datetime.now()
        return True, f"Welcome to Velasa Trading!"

    def login(self, username: str, password: str) -> tuple[bool, str]:
        # Input validation
        input_valid, input_msg = self._validate_input(username, password)
        if not input_valid:
            return False, input_msg

        if username not in st.session_state.users:
            time.sleep(1)  # Prevent timing attacks
            return False, "Invalid credentials"

        user = st.session_state.users[username]

        # Check verification status
        if not user.get('email_verified'):
            return False, "Please verify your email address first"
        if not user.get('phone_verified'):
            return False, "Please verify your phone number first"

        salt = user['salt']
        password_hash = self._hash_password(password, salt)

        if password_hash == user['password_hash']:
            st.session_state.current_user = username
            st.session_state.session_start = datetime.now()
            st.session_state.users[username]['last_login'] = datetime.now().isoformat()
            return True, "Login successful"

        return False, "Invalid credentials"

    def logout(self):
        st.session_state.current_user = None
        st.session_state.session_start = None

    def get_current_user(self) -> Optional[str]:
        if (st.session_state.session_start and 
            datetime.now() - st.session_state.session_start > timedelta(hours=2)):
            self.logout()
            return None
        return st.session_state.current_user

    def check_session_valid(self) -> bool:
        if not st.session_state.current_user or not st.session_state.session_start:
            return False
        if datetime.now() - st.session_state.session_start > timedelta(hours=2):
            self.logout()
            return False
        return True

auth_manager = AuthManager()

def setup_google_oauth():
    st.markdown("""
        <div class="login-container">
            <h2>Welcome to Velasa Trading</h2>
            <p>Premium Trading Platform by JRP Groups Industries</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Sign in with Google"):
        email = st.text_input("Enter your Google email:")
        if st.button("Sign in"):
            success, message = auth_manager.google_sign_in(email)
            if success:
                st.success(message)
            else:
                st.error(message)


def verify_phone():
    #This function is likely handled within the AuthManager now.  No direct replacement needed here.
    pass


def check_authentication():
    return auth_manager.check_session_valid()