import streamlit as st
from utils.auth import AuthManager
from typing import Optional

def render_profile_settings(auth: AuthManager):
    st.subheader("Profile Settings")
    
    user = auth.get_current_user()
    if not user:
        return
        
    user_data = st.session_state.users[user]
    
    with st.container():
        st.markdown("### Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("Email", value=user_data.get('email', ''))
            phone = st.text_input("Phone", value=user_data.get('phone', ''))
        
        with col2:
            notification_preferences = st.multiselect(
                "Notification Preferences",
                ["Email Alerts", "SMS Alerts", "Price Alerts", "Portfolio Updates"],
                default=user_data.get('notifications', [])
            )
    
    st.markdown("### Security Settings")
    with st.expander("Change Password"):
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if new_password != confirm_password:
                    st.error("New passwords do not match")
                else:
                    success, message = auth.change_password(user, current_password, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    st.markdown("### Linked Accounts")
    if user_data.get('google_user'):
        st.info("🔵 Connected with Google")
    else:
        st.warning("Not connected with Google")
        if st.button("Link Google Account"):
            st.info("Enter your Google email to link accounts")
            google_email = st.text_input("Google Email")
            if st.button("Connect"):
                success, message = auth.link_google_account(user, google_email)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    st.markdown("### Account Management")
    with st.expander("Add Another Account"):
        with st.form("add_account_form"):
            st.markdown("""
            Create an additional trading account. Each account will have:
            - Separate portfolio
            - Independent trading history
            - Individual settings
            """)
            account_type = st.selectbox(
                "Account Type",
                ["Standard Trading", "Practice Account"]
            )
            initial_deposit = st.number_input(
                "Initial Deposit ($)",
                min_value=1000.0,
                value=10000.0,
                step=1000.0
            )
            
            if st.form_submit_button("Create Additional Account"):
                success, message = auth.create_additional_account(user, account_type, initial_deposit)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    # Danger Zone
    st.markdown("### ⚠️ Danger Zone")
    with st.expander("Delete Account", expanded=False):
        st.warning(
            """This action is irreversible. Your account and all associated data will be permanently deleted. 
            Please confirm your password to proceed."""
        )
        with st.form("delete_account_form"):
            confirm_password = st.text_input("Confirm Password", type="password")
            understand = st.checkbox("I understand this action cannot be undone")
            
            if st.form_submit_button("Delete My Account"):
                if not understand:
                    st.error("Please confirm you understand this action is irreversible")
                else:
                    success, message = auth.delete_account(user, confirm_password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
