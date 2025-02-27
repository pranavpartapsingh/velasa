import streamlit as st
import hashlib
import secrets
import time
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from .verification import Verification

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

    def _check_rate_limit(self, username: str) -> tuple[bool, str]:
        now = datetime.now()
        attempts = st.session_state.login_attempts.get(username, [])

        # Remove attempts older than 15 minutes
        attempts = [attempt for attempt in attempts 
                   if attempt > now - timedelta(minutes=15)]

        if len(attempts) >= 5:
            return False, "Too many login attempts. Please try again later."

        st.session_state.login_attempts[username] = attempts
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

    def verify_email(self, token: str) -> tuple[bool, str]:
        for username, verification in st.session_state.pending_verifications.items():
            if verification['email_token'] == token:
                if datetime.now() > verification['expires_at']:
                    return False, "Verification link has expired"
                st.session_state.users[username]['email_verified'] = True
                del st.session_state.pending_verifications[username] #remove after verification
                return True, "Email verified successfully"
        return False, "Invalid verification token"

    def verify_phone(self, username: str, otp: str) -> tuple[bool, str]:
        if username not in st.session_state.pending_verifications:
            return False, "No pending verification found"
        if st.session_state.pending_verifications[username]['phone_otp'] != otp:
            return False, "Invalid OTP"
        if datetime.now() > st.session_state.pending_verifications[username]['expires_at']:
            return False, "OTP has expired"
        st.session_state.users[username]['phone_verified'] = True
        del st.session_state.pending_verifications[username] #remove after verification
        return True, "Phone number verified successfully"

    def google_sign_in(self, email: str) -> tuple[bool, str]:
        """
        Simulated Google Sign In that creates or logs in a user
        """
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

        # Rate limiting
        rate_limit_ok, rate_limit_msg = self._check_rate_limit(username)
        if not rate_limit_ok:
            return False, rate_limit_msg

        # Record login attempt
        st.session_state.login_attempts.setdefault(username, []).append(datetime.now())

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
        # Check session expiration (2 hours)
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

    def change_password(self, username: str, current_password: str, new_password: str) -> tuple[bool, str]:
        """Change user's password"""
        if username not in st.session_state.users:
            return False, "User not found"

        user = st.session_state.users[username]
        current_hash = self._hash_password(current_password, user['salt'])

        if current_hash != user['password_hash']:
            return False, "Current password is incorrect"

        # Check password strength
        valid, message = self._check_password_strength(new_password)
        if not valid:
            return False, message

        # Update password
        new_salt = self._generate_salt()
        new_hash = self._hash_password(new_password, new_salt)
        user['salt'] = new_salt
        user['password_hash'] = new_hash

        return True, "Password updated successfully"

    def link_google_account(self, username: str, google_email: str) -> tuple[bool, str]:
        """Link existing account with Google"""
        if not google_email or '@' not in google_email:
            return False, "Invalid email address"

        user = st.session_state.users.get(username)
        if not user:
            return False, "User not found"

        if user.get('google_user'):
            return False, "Account already linked with Google"

        user['google_email'] = google_email
        user['google_user'] = True

        return True, "Google account linked successfully"

    def create_additional_account(
        self,
        username: str,
        account_type: str,
        initial_deposit: float
    ) -> tuple[bool, str]:
        """Create an additional trading account for existing user"""
        if username not in st.session_state.users:
            return False, "User not found"

        # Generate new account ID
        account_count = len([
            u for u in st.session_state.users 
            if u.startswith(f"{username}_account")
        ])
        new_account_id = f"{username}_account{account_count + 1}"

        # Create new account
        st.session_state.users[new_account_id] = {
            'parent_account': username,
            'account_type': account_type,
            'portfolio': {
                'cash': initial_deposit,
                'positions': {},
                'transactions': []
            },
            'created_at': datetime.now().isoformat()
        }

        return True, f"Additional account created successfully: {new_account_id}"

    def delete_account(self, username: str, password: str) -> tuple[bool, str]:
        """Delete user account and all associated data"""
        if username not in st.session_state.users:
            return False, "User not found"

        user = st.session_state.users[username]
        password_hash = self._hash_password(password, user['salt'])

        if password_hash != user['password_hash']:
            return False, "Incorrect password"

        # Delete main account and all linked accounts
        accounts_to_delete = [
            acc_id for acc_id in st.session_state.users
            if acc_id == username or 
            (isinstance(st.session_state.users[acc_id], dict) and 
             st.session_state.users[acc_id].get('parent_account') == username)
        ]

        for account_id in accounts_to_delete:
            del st.session_state.users[account_id]

        # Clear current session
        self.logout()

        return True, "Account deleted successfully"

    def get_linked_accounts(self, username: str) -> List[str]:
        """Get all accounts linked to the main account"""
        return [
            acc_id for acc_id in st.session_state.users
            if isinstance(st.session_state.users[acc_id], dict) and 
            st.session_state.users[acc_id].get('parent_account') == username
        ]