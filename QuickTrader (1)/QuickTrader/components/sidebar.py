import streamlit as st

def render_sidebar():
    """Render the sidebar with navigation and user info"""
    with st.sidebar:
        st.image('assets/logo.svg', width=200)
        st.title("Velasa Trading")
        
        # User info
        st.subheader("Account Info")
        st.info(f"Welcome, {st.session_state.user_data['name']}")
        
        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Go to",
            ["Dashboard", "Portfolio", "Orders", "Settings"]
        )
        
        # Market Status
        st.subheader("Market Status")
        st.success("Market Open")
        
        # Settings and Logout
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.experimental_rerun()
