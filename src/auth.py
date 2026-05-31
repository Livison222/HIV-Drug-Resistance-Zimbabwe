import streamlit as st
import hashlib
from datetime import datetime

# Default credentials - Change these in production
DEFAULT_PASSWORD = "admin123"

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password() -> bool:
    """Returns True if the user had the correct password."""
    
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    # If already authenticated, return True
    if st.session_state.password_correct:
        return True
    
    # Show login page
    login_container = st.container()
    
    with login_container:
        # Center the login form using columns
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
                <style>
                .login-container {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 50px;
                    border-radius: 10px;
                    color: white;
                    text-align: center;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    margin-top: 50px;
                }
                .login-title {
                    font-size: 2em;
                    font-weight: 700;
                    margin-bottom: 10px;
                }
                .login-subtitle {
                    font-size: 1.1em;
                    opacity: 0.95;
                    margin-bottom: 30px;
                }
                </style>
                <div class="login-container">
                    <div class="login-title">🔐 HIV Drug Resistance Predictor</div>
                    <div class="login-subtitle">Please log in to continue</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Login form
            with st.form("login_form"):
                st.markdown("### 🔑 Enter Your Password")
                password = st.text_input(
                    "Password",
                    type="password",
                    label_visibility="collapsed",
                    placeholder="Enter password"
                )
                
                submit_button = st.form_submit_button(
                    "🔓 Login",
                    use_container_width=True,
                    type="primary"
                )
                
                if submit_button:
                    password_hash = hash_password(password)
                    default_hash = hash_password(DEFAULT_PASSWORD)
                    
                    if password_hash == default_hash:
                        st.session_state.password_correct = True
                        st.session_state.login_time = datetime.now()
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password. Please try again.")
            
            st.markdown("---")
            st.markdown("""
                <div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 20px;">
                    <p><strong>Default Password:</strong> admin123</p>
                    <p style="font-size: 0.8em; color: #999;">💡 Change the default password in production</p>
                </div>
            """, unsafe_allow_html=True)
    
    return False

def show_logout_button():
    """Display a logout button in the sidebar."""
    if st.session_state.get("password_correct", False):
        with st.sidebar:
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
                st.session_state.password_correct = False
                st.session_state.login_time = None
                st.rerun()
            
            # Show login time
            if "login_time" in st.session_state and st.session_state.login_time:
                login_time = st.session_state.login_time.strftime("%Y-%m-%d %H:%M:%S")
                st.caption(f"📋 Logged in: {login_time}")
