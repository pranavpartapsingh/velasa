import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
from .verification import Verification

class NotificationManager:
    def __init__(self):
        if 'notifications' not in st.session_state:
            st.session_state.notifications = {}
        self.verification = Verification()

    def add_notification(
        self,
        username: str,
        message: str,
        notification_type: str,
        priority: str = "normal",
        send_email: bool = False,
        send_sms: bool = False
    ) -> bool:
        """Add a new notification"""
        if username not in st.session_state.notifications:
            st.session_state.notifications[username] = []
        
        notification = {
            'id': len(st.session_state.notifications[username]),
            'message': message,
            'type': notification_type,
            'priority': priority,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        st.session_state.notifications[username].append(notification)

        # Send external notifications if requested
        if send_email and username in st.session_state.users:
            user_email = st.session_state.users[username].get('email')
            if user_email:
                self.verification.send_email_verification(
                    user_email,
                    f"Velasa Trading Notification: {message}"
                )

        if send_sms and username in st.session_state.users:
            user_phone = st.session_state.users[username].get('phone')
            if user_phone:
                self.verification.send_sms_otp(
                    user_phone,
                    f"Velasa Trading: {message}"
                )

        return True

    def get_notifications(
        self,
        username: str,
        unread_only: bool = False,
        notification_type: Optional[str] = None
    ) -> List[Dict]:
        """Get user notifications with optional filters"""
        if username not in st.session_state.notifications:
            return []
        
        notifications = st.session_state.notifications[username]
        
        if unread_only:
            notifications = [n for n in notifications if not n['read']]
        
        if notification_type:
            notifications = [n for n in notifications if n['type'] == notification_type]
        
        return sorted(
            notifications,
            key=lambda x: x['timestamp'],
            reverse=True
        )

    def mark_as_read(self, username: str, notification_id: int) -> bool:
        """Mark a notification as read"""
        if username not in st.session_state.notifications:
            return False
        
        for notification in st.session_state.notifications[username]:
            if notification['id'] == notification_id:
                notification['read'] = True
                return True
        
        return False

    def mark_all_as_read(self, username: str) -> bool:
        """Mark all notifications as read"""
        if username not in st.session_state.notifications:
            return False
        
        for notification in st.session_state.notifications[username]:
            notification['read'] = True
        
        return True

    def clear_notifications(self, username: str) -> bool:
        """Clear all notifications for a user"""
        if username not in st.session_state.notifications:
            return False
        
        st.session_state.notifications[username] = []
        return True
