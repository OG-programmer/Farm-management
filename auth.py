import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

# Dictionary for users with their credentials
users_db = {
    "Des": {"password": "2024", "name": "User One"},
    "Ezra": {"password": "2024", "name": "User Two"},
    "Agi": {"password": "2024", "name": "User Three"},
    "user4": {"password": "passwordABC", "name": "User Four"},
    "user5": {"password": "passwordXYZ", "name": "User Five"}
}

# Initialize cookies manager with a password argument
cookies = EncryptedCookieManager(prefix="auth", password="your_secret_key_here")

# Ensure cookies are ready before proceeding
if not cookies.ready():
    st.stop()

def authenticate_user():
    """Display login form and authenticate user."""
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    remember_me = st.sidebar.checkbox("Remember me")
    login_button = st.sidebar.button("Login")

    if login_button:
        if username in users_db and users_db[username]["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["user_name"] = users_db[username]["name"]
            st.sidebar.success(f"Welcome, {st.session_state['user_name']}!")
            
            # Store credentials in cookies if "Remember Me" is checked
            if remember_me:
                cookies["username"] = username
                cookies["password"] = password
                cookies.save()
        else:
            st.sidebar.error("Invalid username or password")

def check_authentication():
    """Check if the user is authenticated."""
    # Check for saved credentials in cookies
    if "username" in cookies and "password" in cookies:
        username = cookies["username"]
        password = cookies["password"]
        if username in users_db and users_db[username]["password"] == password:
            st.session_state["authenticated"] = True
            st.session_state["user_name"] = users_db[username]["name"]
            return True

    # Check session state
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        authenticate_user()
        return False
    return True

def logout():
    """Log out the current user."""
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        del st.session_state["authenticated"]
        del st.session_state["user_name"]
        st.sidebar.write("You have been logged out.")
        # Clear cookies on logout
        cookies.delete("username")
        cookies.delete("password")
        cookies.save()



