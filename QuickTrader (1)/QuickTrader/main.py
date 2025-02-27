import streamlit as st
from datetime import datetime
import os
from utils.auth import AuthManager
from utils.portfolio import Portfolio
from utils.verification import Verification
from components.dashboard import render_dashboard
from components.trading import render_trading_interface
from components.portfolio_analysis import render_portfolio_analysis
from components.notifications import render_notifications
from components.profile import render_profile_settings

# Security headers
st.set_page_config(
    page_title="Velasa Trading - JRP GROUPS OF INDUSTRIES",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Velasa Trading - A JRP GROUPS OF INDUSTRIES Company"
    }
)

# Load custom CSS
with open('styles/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize services
auth = AuthManager()
verification = Verification()

def show_help_tooltip(text: str):
    """Show a help tooltip with the given text"""
    st.markdown(f"""
        <div class="tooltip-text">
            ℹ️ {text}
        </div>
    """, unsafe_allow_html=True)

def main():
    # Check session validity
    if auth.get_current_user() and not auth.check_session_valid():
        st.warning("Your session has expired. Please log in again.")
        auth.logout()
        st.rerun()

    if auth.get_current_user() is None:
        st.markdown(
            """
            <div style='text-align: center; padding: 2rem;'>
                <h1>Welcome to Velasa Trading</h1>
                <p style='color: #FFD700; font-style: italic; font-size: 1.2em;'>
                    Your Premium Trading Platform
                </p>
                <p style='color: #888; font-size: 1.1em;'>
                    Start your trading journey with our user-friendly platform
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            show_help_tooltip("Enter your credentials to access your account")
            with st.form("login_form"):
                st.markdown("### Welcome Back")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    success, message = auth.login(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

            st.markdown("---")
            st.markdown("<div style='text-align: center;'><p>Or continue with</p></div>", unsafe_allow_html=True)

            # Google Sign In Button
            google_col1, google_col2, google_col3 = st.columns([1,2,1])
            with google_col2:
                show_help_tooltip("Quick login with your Google account")
                with st.form("google_login_form"):
                    st.markdown(
                        """
                        <div style='text-align: center; margin-bottom: 10px;'>
                            <img src="https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png" 
                                 style="height: 20px; margin-right: 8px; vertical-align: middle;">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    google_email = st.text_input("Google Email")
                    if st.form_submit_button("Continue with Google", use_container_width=True):
                        success, message = auth.google_sign_in(google_email)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

        with tab2:
            show_help_tooltip("Create a new account to start trading")
            with st.form("register_form"):
                st.markdown("### Join Velasa Trading")
                st.markdown("""
                📱 Get started in 3 easy steps:
                1. Fill in your details
                2. Verify your email
                3. Start trading!

                Your password should have:
                ✓ 8+ characters
                ✓ Upper & lowercase letters
                ✓ Numbers
                ✓ Special characters
                """)
                new_username = st.text_input("Username")
                email = st.text_input("Email Address")
                phone = st.text_input("Phone Number (with country code)", placeholder="+1234567890")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")

                if st.form_submit_button("Create Account", use_container_width=True):
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message = auth.register(new_username, new_password, email, phone)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

    else:
        # Sidebar with quick actions
        st.sidebar.markdown("## Quick Actions")
        st.sidebar.markdown(f"👋 Welcome back, {auth.get_current_user()}")

        # Main navigation
        tabs = ["Dashboard", "Trading", "Portfolio Analysis", "Profile"]
        tab1, tab2, tab3, tab4 = st.tabs(tabs)

        portfolio = Portfolio(auth.get_current_user())

        with tab1:
            show_help_tooltip("View your portfolio overview and quick insights")
            render_dashboard(portfolio)

        with tab2:
            show_help_tooltip("Place trades and analyze stocks")
            render_trading_interface(portfolio)

        with tab3:
            show_help_tooltip("Detailed analysis of your portfolio performance")
            render_portfolio_analysis(portfolio)

        with tab4:
            show_help_tooltip("Manage your account settings and preferences")
            render_profile_settings(auth)

        if st.sidebar.button("Logout"):
            auth.logout()
            st.rerun()

if __name__ == "__main__":
    main()