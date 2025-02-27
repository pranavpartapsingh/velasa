import streamlit as st
from utils.notifications import NotificationManager
from datetime import datetime
import pytz

def render_notifications(notification_manager: NotificationManager, username: str):
    st.sidebar.markdown("### 📬 Notifications")
    
    # Get notifications
    notifications = notification_manager.get_notifications(username)
    unread_count = len(notification_manager.get_notifications(username, unread_only=True))
    
    # Notification counter
    if unread_count > 0:
        st.sidebar.markdown(
            f"""
            <div style='background-color: #FFD700; color: black; padding: 5px 10px; 
            border-radius: 10px; display: inline-block;'>
                {unread_count} new
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Notification controls
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Mark All Read"):
            notification_manager.mark_all_as_read(username)
            st.rerun()
    with col2:
        if st.button("Clear All"):
            if st.sidebar.checkbox("Confirm clear all notifications?"):
                notification_manager.clear_notifications(username)
                st.rerun()
    
    # Display notifications
    for notification in notifications:
        with st.sidebar.container():
            # Format timestamp
            timestamp = datetime.fromisoformat(notification['timestamp'])
            local_time = timestamp.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Notification card
            st.markdown(
                f"""
                <div style='
                    background: {'#1A1C24' if notification['read'] else '#262730'};
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 3px solid {_get_priority_color(notification['priority'])};
                    margin: 5px 0;
                '>
                    <div style='color: #888; font-size: 0.8em;'>{local_time}</div>
                    <div style='color: {_get_type_color(notification['type'])}; font-size: 0.9em;'>
                        {notification['type'].upper()}
                    </div>
                    <div style='margin: 5px 0;'>{notification['message']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if not notification['read']:
                if st.button("Mark Read", key=f"read_{notification['id']}"):
                    notification_manager.mark_as_read(username, notification['id'])
                    st.rerun()

def _get_priority_color(priority: str) -> str:
    """Get color based on notification priority"""
    colors = {
        "high": "#FF4B4B",
        "normal": "#FFD700",
        "low": "#00FF00"
    }
    return colors.get(priority.lower(), "#FFD700")

def _get_type_color(notification_type: str) -> str:
    """Get color based on notification type"""
    colors = {
        "trade": "#00FF00",
        "security": "#FF4B4B",
        "portfolio": "#FFD700",
        "system": "#888888"
    }
    return colors.get(notification_type.lower(), "#FFFFFF")
