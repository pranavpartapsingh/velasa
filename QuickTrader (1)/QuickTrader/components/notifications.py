import streamlit as st
from datetime import datetime

def render_notifications(notification_manager, username: str):
    """Render notifications in the sidebar"""
    notifications = notification_manager.get_user_notifications(username)
    
    if notifications:
        with st.sidebar:
            st.markdown("### Notifications")
            for notif in notifications:
                with st.container():
                    st.markdown(f"""
                    **{notif['title']}**  
                    {notif['message']}  
                    *{notif['timestamp'].strftime('%Y-%m-%d %H:%M')}*
                    """)
                    if st.button("Mark as Read", key=f"notif_{notif['id']}"):
                        notification_manager.mark_as_read(username, notif['id'])
                st.markdown("---")
