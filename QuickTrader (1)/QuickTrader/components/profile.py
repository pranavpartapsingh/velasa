import streamlit as st

def render_profile_settings(auth):
    """Render user profile settings"""
    st.markdown("## Profile Settings")
    
    # Get current user data
    username = auth.get_current_user()
    user_data = st.session_state.users.get(username, {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Account Information")
        st.markdown(f"""
        **Username:** {username}  
        **Email:** {user_data.get('email', 'Not set')}  
        **Phone:** {user_data.get('phone', 'Not set')}  
        **Account Type:** {'Google Account' if user_data.get('google_user') else 'Standard Account'}  
        **Created:** {user_data.get('created_at', 'Unknown').split('T')[0]}  
        **Last Login:** {user_data.get('last_login', 'Never').split('T')[0]}
        """)
    
    with col2:
        st.markdown("### Security Settings")
        with st.form("change_password_form"):
            st.markdown("#### Change Password")
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if new_password != confirm_password:
                    st.error("New passwords do not match")
                else:
                    success, message = auth.change_password(username, current_password, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    # Account Management
    st.markdown("### Account Management")
    if st.button("Delete Account", type="secondary"):
        st.warning("⚠️ This action cannot be undone!")
        password = st.text_input("Enter your password to confirm", type="password")
        if st.button("Confirm Delete Account"):
            success, message = auth.delete_account(username, password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
