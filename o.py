import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import pandas as pd
import json
import time
import secrets
import string
import os
import traceback

import ssl



# Page configuration
st.set_page_config(
    page_title="VOLAR FASHION - Leave Management",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Beautiful Elegant CSS with Premium Design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f8f9ff 0%, #f5f7fa 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9ff 0%, #f5f7fa 100%);
        background-attachment: fixed;
    }
    
    .form-container {
        background: white;
        padding: 3.5rem;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(103, 58, 183, 0.08);
        margin: 2rem auto;
        max-width: 1000px;
        border: 1px solid rgba(103, 58, 183, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .form-container:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #673ab7, #9c27b0, #2196f3);
    }
    
    h1 {
        background: linear-gradient(135deg, #673ab7 0%, #2196f3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3.2rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
        font-family: 'Playfair Display', serif;
        letter-spacing: -0.5px;
    }
    
    h2 {
        color: #5a6c7d;
        text-align: center;
        font-size: 1.6rem;
        margin-bottom: 3rem;
        font-weight: 400;
        font-family: 'Inter', sans-serif;
        opacity: 0.9;
    }
    
    h3 {
        color: #4a5568;
        font-size: 1.4rem;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
        position: relative;
        padding-bottom: 10px;
    }
    
    h3:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #673ab7, #9c27b0);
        border-radius: 2px;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        color: white;
        border: none;
        padding: 1rem 3rem;
        font-size: 1.1rem;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 25px rgba(103, 58, 183, 0.25);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button:after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 5px;
        height: 5px;
        background: rgba(255, 255, 255, 0.5);
        opacity: 0;
        border-radius: 100%;
        transform: scale(1, 1) translate(-50%);
        transform-origin: 50% 50%;
    }
    
    .stButton>button:focus:not(:active)::after {
        animation: ripple 1s ease-out;
    }
    
    @keyframes ripple {
        0% {
            transform: scale(0, 0);
            opacity: 0.5;
        }
        100% {
            transform: scale(20, 20);
            opacity: 0;
        }
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(103, 58, 183, 0.35);
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>select, 
    .stTextArea>div>div>textarea, .stDateInput>div>div>input {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 0.875rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #fafbfc;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus, 
    .stTextArea>div>div>textarea:focus, .stDateInput>div>div>input:focus {
        border-color: #673ab7;
        box-shadow: 0 0 0 4px rgba(103, 58, 183, 0.1);
        background: white;
        outline: none;
    }
    
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
        color: #155724;
        padding: 1.75rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 500;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(40, 167, 69, 0.1);
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid #dc3545;
        color: #721c24;
        padding: 1.75rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 500;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(220, 53, 69, 0.1);
        animation: shake 0.5s ease;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        color: #0d47a1;
        padding: 1.75rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(33, 150, 243, 0.1);
    }
    
    .thumbsup-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 4px solid #4caf50;
        color: #2e7d32;
        padding: 1.75rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.1);
        text-align: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(156, 39, 176, 0.1);
        border: 1px solid rgba(156, 39, 176, 0.1);
    }
    
    .approval-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .status-pending {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid rgba(255, 193, 7, 0.3);
    }
    
    .status-approved {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid rgba(40, 167, 69, 0.3);
    }
    
    .status-rejected {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid rgba(220, 53, 69, 0.3);
    }
    
    label {
        font-weight: 600 !important;
        color: #4a5568 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
        display: block;
    }
    
    .stTextInput>div>label, .stSelectbox>div>label, 
    .stTextArea>div>label, .stDateInput>div>label {
        color: #4a5568 !important;
        font-weight: 600 !important;
    }
    
    .footer {
        text-align: center;
        color: #718096;
        padding: 3rem 2rem;
        margin-top: 4rem;
        position: relative;
    }
    
    .footer:before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #673ab7, transparent);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: white;
        padding: 12px;
        border-radius: 16px;
        border: 1px solid rgba(103, 58, 183, 0.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 12px;
        color: #718096;
        font-weight: 500;
        padding: 12px 28px;
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        color: white;
        border-color: #673ab7;
        box-shadow: 0 4px 12px rgba(103, 58, 183, 0.2);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .password-field {
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
        font-weight: 600;
        color: #673ab7;
    }
    
    .company-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem;
        background: white;
        border-radius: 24px;
        box-shadow: 0 15px 40px rgba(103, 58, 183, 0.08);
        border: 1px solid rgba(103, 58, 183, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .company-header:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #673ab7, #9c27b0, #2196f3);
    }
    
    .glass-effect {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #673ab7 0%, #2196f3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .icon-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        color: white;
        margin-right: 12px;
        font-size: 1.2rem;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f1f5f9;
    }
    
    .floating-element {
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .sparkle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: white;
        border-radius: 50%;
        animation: sparkle 2s infinite;
    }
    
    @keyframes sparkle {
        0%, 100% { opacity: 0; transform: scale(0); }
        50% { opacity: 1; transform: scale(1); }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5e35b1 0%, #8e24aa 100%);
    }
    
    .confetti {
        position: fixed;
        width: 10px;
        height: 10px;
        background: #673ab7;
        opacity: 0;
    }
    
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.9rem;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .thumbsup-emoji {
        font-size: 3rem;
        animation: thumbsupAnimation 2s ease-in-out infinite;
    }
    
    @keyframes thumbsupAnimation {
        0%, 100% { transform: scale(1) rotate(0deg); }
        25% { transform: scale(1.1) rotate(-5deg); }
        50% { transform: scale(1.2) rotate(5deg); }
        75% { transform: scale(1.1) rotate(-5deg); }
    }
    
    /* Copy code button */
    .copy-code-btn {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        margin-top: 10px;
        transition: all 0.3s;
    }
    
    .copy-code-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 142, 60, 0.3);
    }
    
    .copy-success {
        color: #4caf50;
        font-size: 12px;
        margin-top: 5px;
        display: none;
    }
    
    /* Test email styles */
    .test-email-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
    }
    
    .test-email-input {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 6px;
        margin: 10px 0;
    }
    
    .test-email-btn {
        background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        width: 100%;
        font-weight: 500;
    }
    
    .test-result-success {
        background: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 6px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
    
    .test-result-error {
        background: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 6px;
        margin: 10px 0;
        border-left: 4px solid #dc3545;
    }
    
    .debug-log {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 10px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        max-height: 200px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Superior details dictionary
SUPERIORS = {
    "Shantanu": "s37@vfemails.com",
    "Ayushi": "ayushi@volarfashion.in",
    "Sandip Sir": "sandip@ragunited.com",
    "Akshaya": "Akshaya@vfemails.com",
    "Vitika": "vitika@vfemails.com",
    "MANISH": "Manish@vfemails.com",
    "TAHIR": "tahir@vfemails.com",
    "Tariq": "dn1@volarfashion.in",
    "HR": "hrvolarfashion@gmail.com",
    "Rajeev": "Rajeev@vfemails.com",
    "Krishna": "Krishna@vfemails.com",
    "Sarath": "Sarath@vfemails.com",
    "Demo": "Shinde78617@gmail.com"
}

# Department options
DEPARTMENTS = [
    "Human Resources",
    "Finance",
    "Ecom",
    "Graphic Design",
    "Sales and Marketing",
    "Quality Control",
    "IT",
    "Administration"
]

# Initialize session state
if 'approval_code_to_copy' not in st.session_state:
    st.session_state.approval_code_to_copy = ""
if 'show_copy_section' not in st.session_state:
    st.session_state.show_copy_section = False
if 'test_email_result' not in st.session_state:
    st.session_state.test_email_result = None
if 'email_config_status' not in st.session_state:
    st.session_state.email_config_status = "Not Tested"
if 'debug_logs' not in st.session_state:
    st.session_state.debug_logs = []

def add_debug_log(message, level="INFO"):
    """Add debug log message"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"
    st.session_state.debug_logs.append(log_entry)
    # Keep only last 50 logs
    if len(st.session_state.debug_logs) > 50:
        st.session_state.debug_logs.pop(0)

def log_debug(message):
    """Log debug messages"""
    add_debug_log(message, "DEBUG")
    st.sidebar.text(f"{datetime.now().strftime('%H:%M:%S')}: {message}")

def generate_approval_password():
    """Generate a 5-digit alphanumeric password"""
    alphabet = string.ascii_uppercase + string.digits
    # Remove confusing characters (0, O, 1, I, L)
    alphabet = alphabet.replace('0', '').replace('O', '').replace('1', '').replace('I', '').replace('L', '')
    password = ''.join(secrets.choice(alphabet) for _ in range(5))
    log_debug(f"Generated approval password: {password}")
    return password

def get_google_credentials():
    """Get Google credentials from Streamlit secrets"""
    try:
        # Check if secrets exist
        if 'GOOGLE_CREDENTIALS' not in st.secrets:
            add_debug_log("GOOGLE_CREDENTIALS not found in secrets", "ERROR")
            st.error("❌ Google credentials not found in Streamlit secrets")
            return None
        
        add_debug_log("Loading Google credentials from Streamlit secrets", "INFO")
        
        # Access each field individually (more reliable in Streamlit Cloud)
        creds_dict = {
            "type": st.secrets["GOOGLE_CREDENTIALS"]["type"],
            "project_id": st.secrets["GOOGLE_CREDENTIALS"]["project_id"],
            "private_key_id": st.secrets["GOOGLE_CREDENTIALS"]["private_key_id"],
            "private_key": st.secrets["GOOGLE_CREDENTIALS"]["private_key"],
            "client_email": st.secrets["GOOGLE_CREDENTIALS"]["client_email"],
            "client_id": st.secrets["GOOGLE_CREDENTIALS"]["client_id"],
            "auth_uri": st.secrets["GOOGLE_CREDENTIALS"]["auth_uri"],
            "token_uri": st.secrets["GOOGLE_CREDENTIALS"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["GOOGLE_CREDENTIALS"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["GOOGLE_CREDENTIALS"]["client_x509_cert_url"]
        }
        
        add_debug_log(f"Credentials loaded for: {creds_dict['client_email']}", "SUCCESS")
        return creds_dict
            
    except KeyError as e:
        add_debug_log(f"Missing key in GOOGLE_CREDENTIALS: {str(e)}", "ERROR")
        st.error(f"❌ Missing credential field: {str(e)}")
        return None
    except Exception as e:
        add_debug_log(f"Error getting Google credentials: {traceback.format_exc()}", "ERROR")
        st.error(f"❌ Error loading credentials: {str(e)}")
        return None

def setup_google_sheets():
    """Setup Google Sheets connection"""
    try:
        log_debug("Setting up Google Sheets connection...")
        
        SCOPES = ['https://spreadsheets.google.com/feeds', 
                 'https://www.googleapis.com/auth/drive']
        
        # Get credentials
        creds_dict = get_google_credentials()
        
        if not creds_dict:
            st.error("❌ No Google credentials found")
            return None
        
        # Check if private key exists
        if not creds_dict.get("private_key"):
            st.error("❌ Google private key not found in credentials")
            return None
        
        # Create credentials
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
        
        # Authorize client
        client = gspread.authorize(creds)
        
        # Try to open the sheet
        SHEET_NAME = "Leave_Applications"
        try:
            spreadsheet = client.open(SHEET_NAME)
            sheet = spreadsheet.sheet1
            log_debug(f"Successfully connected to sheet: {SHEET_NAME}")
            
            # Check if headers exist, add them if not
            try:
                if sheet.row_count == 0 or not sheet.row_values(1):
                    headers = [
                        "Submission Date", "Employee Name", "Employee Code", "Department",
                        "Type of Leave", "No of Days", "Purpose of Leave", "From Date",
                        "Till Date", "Superior Name", "Superior Email", "Status", 
                        "Approval Date", "Approval Password"
                    ]
                    sheet.append_row(headers)
                    log_debug("Added headers to sheet")
            except Exception as e:
                log_debug(f"Warning: Could not check/add headers: {str(e)}")
            
            return sheet
            
        except gspread.SpreadsheetNotFound:
            st.error(f"❌ Google Sheet '{SHEET_NAME}' not found!")
            st.info(f"Please create a sheet named '{SHEET_NAME}' in Google Sheets and share it with: {creds_dict.get('client_email', 'service account email')}")
            return None
        except Exception as e:
            st.error(f"❌ Error accessing sheet: {str(e)}")
            return None
        
    except Exception as e:
        error_msg = f"❌ Error in setup_google_sheets: {str(e)}"
        st.error(error_msg)
        add_debug_log(f"setup_google_sheets error: {traceback.format_exc()}", "ERROR")
        return None

def get_email_credentials():
    """Get email credentials from Streamlit secrets"""
    try:
        if 'EMAIL' not in st.secrets:
            add_debug_log("EMAIL section not found in secrets", "ERROR")
            return "", "", "Missing"
        
        sender_email = st.secrets["EMAIL"]["sender_email"]
        sender_password = st.secrets["EMAIL"]["sender_password"]
        
        add_debug_log(f"Email credentials loaded for: {sender_email}", "INFO")
        return sender_email, sender_password, "Streamlit Secrets"
        
    except KeyError as e:
        add_debug_log(f"Missing email credential: {str(e)}", "ERROR")
        return "", "", f"Missing: {str(e)}"
    except Exception as e:
        add_debug_log(f"Error getting email credentials: {str(e)}", "ERROR")
        return "", "", "Error"

def check_email_configuration():
    """Check if email is configured properly"""
    sender_email, sender_password, source = get_email_credentials()
    
    if not sender_email or not sender_password:
        return {
            "configured": False,
            "message": "❌ Email credentials not found",
            "details": f"Please check your {source} configuration",
            "source": source
        }
    
    # Test if credentials might be an app password (16 characters)
    if len(sender_password) == 16 and ' ' not in sender_password:
        password_type = "App Password"
    elif len(sender_password) > 0:
        password_type = "Regular Password"
    else:
        password_type = "Unknown"
    
    return {
        "configured": True,
        "sender_email": sender_email,
        "source": source,
        "password_type": password_type,
        "message": f"✅ Email credentials found ({password_type})"
    }

def create_smtp_connection(sender_email, sender_password, method="auto"):
    """Create and return SMTP connection with proper error handling"""
    try:
        add_debug_log(f"Attempting SMTP connection with method: {method}", "INFO")
        
        if method == "ssl" or method == "auto":
            try:
                # Method 1: SMTP_SSL (Port 465) - Most reliable for Gmail
                add_debug_log("Trying SMTP_SSL on port 465...", "INFO")
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30, context=context)
                server.login(sender_email, sender_password)
                add_debug_log("SMTP_SSL connection successful", "SUCCESS")
                return server, "SMTP_SSL (Port 465)"
            except Exception as e:
                add_debug_log(f"SMTP_SSL failed: {str(e)}", "WARNING")
        
        if method == "starttls" or method == "auto":
            try:
                # Method 2: STARTTLS (Port 587) - Alternative
                add_debug_log("Trying STARTTLS on port 587...", "INFO")
                server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
                server.starttls(context=ssl.create_default_context())
                server.login(sender_email, sender_password)
                add_debug_log("STARTTLS connection successful", "SUCCESS")
                return server, "STARTTLS (Port 587)"
            except Exception as e:
                add_debug_log(f"STARTTLS failed: {str(e)}", "WARNING")
        
        return None, "All connection methods failed"
        
    except Exception as e:
        add_debug_log(f"SMTP connection error: {str(e)}", "ERROR")
        return None, str(e)

def test_email_connection(test_recipient=None):
    """Test email connection by sending a test email"""
    try:
        sender_email, sender_password, source = get_email_credentials()
        
        if not sender_email or not sender_password:
            result = {
                "success": False,
                "message": "❌ Email credentials not configured",
                "details": "Please check your secrets.toml or environment variables",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            add_debug_log("Email test failed: No credentials", "ERROR")
            return result
        
        # Use test recipient or sender's email for testing
        recipient = test_recipient or sender_email
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = "📧 VOLAR FASHION - Email Configuration Test"
        
        test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = f"""
        This is a test email from VOLAR FASHION Leave Management System.
        
        Test Details:
        - Time: {test_time}
        - Sender: {sender_email}
        - Recipient: {recipient}
        - Source: {source}
        
        If you received this email, your email configuration is working correctly!
        
        --
        VOLAR FASHION HR Department
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Try to create SMTP connection
        server, method = create_smtp_connection(sender_email, sender_password)
        
        if server:
            try:
                server.send_message(msg)
                server.quit()
                result = {
                    "success": True,
                    "message": f"✅ Email sent successfully via {method}",
                    "details": f"Test email sent to {recipient} at {test_time}",
                    "method": method,
                    "sender": sender_email,
                    "timestamp": test_time
                }
                add_debug_log(f"Test email sent successfully to {recipient}", "SUCCESS")
                return result
            except Exception as e:
                server.quit()
                add_debug_log(f"Error sending test email: {str(e)}", "ERROR")
                raise e
        else:
            error_msg = f"❌ Could not establish SMTP connection. Method tried: {method}"
            
            # Check for specific authentication errors
            if "535" in method or "534" in method:
                error_msg = "❌ SMTP Authentication Error - App Password Required"
                troubleshooting = """
                **Solution:**
                1. Go to: https://myaccount.google.com/security
                2. Enable 2-Step Verification
                3. Go to: https://myaccount.google.com/apppasswords
                4. Generate an App Password for "Mail"
                5. Use the 16-character App Password in secrets.toml
                """
            elif "Connection refused" in method or "timed out" in method:
                error_msg = "❌ Network Connection Error"
                troubleshooting = "Check if Streamlit Cloud allows outgoing SMTP connections"
            else:
                troubleshooting = "Please check your email credentials and try again"
            
            result = {
                "success": False,
                "message": error_msg,
                "details": f"{troubleshooting}\n\nError: {method}",
                "sender": sender_email,
                "timestamp": test_time
            }
            add_debug_log(f"Test email failed: {method}", "ERROR")
            return result
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = str(e)
        result = {
            "success": False,
            "message": "❌ SMTP Authentication Failed",
            "details": f"Error: {error_msg}\n\n**Solution:** Use an App Password (not your regular Gmail password). Enable 2-Step Verification first.",
            "sender": sender_email,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        add_debug_log(f"SMTP Authentication Error: {error_msg}", "ERROR")
        return result
    except Exception as e:
        error_msg = str(e)
        result = {
            "success": False,
            "message": "❌ Unexpected Error",
            "details": f"Error: {error_msg}",
            "sender": sender_email,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        add_debug_log(f"Unexpected error in test_email_connection: {traceback.format_exc()}", "ERROR")
        return result

def calculate_days(from_date, till_date, leave_type):
    """Calculate number of days"""
    if leave_type == "Half Day":
        return 0.5
    elif leave_type == "Early Exit":
        return "N/A"
    else:
        delta = till_date - from_date
        return delta.days + 1

def send_approval_email(employee_name, superior_name, superior_email, leave_details, approval_password):
    """Send approval request email to superior"""
    try:
        # Get email credentials
        sender_email, sender_password, source = get_email_credentials()
        
        if not sender_email or not sender_password:
            st.warning("⚠️ Email credentials not configured")
            add_debug_log("Email credentials missing", "WARNING")
            return False
            
        # Check if it's a valid email
        if "@" not in superior_email or "." not in superior_email:
            st.warning(f"⚠️ Invalid email format: {superior_email}")
            add_debug_log(f"Invalid email format: {superior_email}", "WARNING")
            return False
        
        # Get app URL
        try:
            app_url = st.secrets["APP_URL"]
        except:
            app_url = "https://hr-application-rtundoncudkzt9efwnscey.streamlit.app/"
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"VOLAR FASHION HR <{sender_email}>"
        msg['To'] = superior_email
        msg['Subject'] = f"Leave Approval Required: {employee_name}"
        
        # Simple HTML email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #673ab7;">Leave Approval Required</h2>
                <p>Dear {superior_name},</p>
                
                <div style="background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3>Employee Leave Request Details:</h3>
                    <p><strong>Employee Name:</strong> {leave_details['employee_name']}</p>
                    <p><strong>Employee Code:</strong> {leave_details['employee_code']}</p>
                    <p><strong>Department:</strong> {leave_details['department']}</p>
                    <p><strong>Leave Type:</strong> {leave_details['leave_type']}</p>
                    <p><strong>From Date:</strong> {leave_details['from_date']}</p>
                    <p><strong>Till Date:</strong> {leave_details['till_date']}</p>
                    <p><strong>Duration:</strong> {leave_details['no_of_days']} days</p>
                    <p><strong>Purpose:</strong> {leave_details['purpose']}</p>
                </div>
                

                
                <div style="margin: 30px 0;">
                    <p><strong>How to Approve/Reject:</strong></p>
                    <ol>
                        <li>Visit: <a href="{app_url}">{app_url}</a></li>
                        <li>Click on "✅ Approval Portal" tab</li>
                        <li>Enter your email: {superior_email}</li>
                        <li>Enter approval code: {approval_password}</li>
                        <li>Select Approve or Reject</li>
                        <li>Click Submit Decision</li>
                    </ol>
                </div>
                
                <hr>
                <p style="color: #666; font-size: 12px;">
                    VOLAR FASHION PVT LTD - HR Department<br>
                    📧 hrvolarfashion@gmail.com<br>
                    This is an automated message.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Create SMTP connection
        server, method = create_smtp_connection(sender_email, sender_password)
        
        if server:
            try:
                server.send_message(msg)
                server.quit()
                add_debug_log(f"Approval email sent to {superior_email} via {method}", "SUCCESS")
                return True
            except Exception as e:
                server.quit()
                add_debug_log(f"Failed to send approval email: {str(e)}", "ERROR")
                return False
        else:
            add_debug_log(f"Could not establish SMTP connection for approval email", "ERROR")
            return False
            
    except Exception as e:
        add_debug_log(f"Error in send_approval_email: {traceback.format_exc()}", "ERROR")
        return False

def update_leave_status(sheet, superior_email, approval_password, status):
    """Update leave status in Google Sheet"""
    try:
        all_records = sheet.get_all_values()
        
        for idx, row in enumerate(all_records):
            if idx == 0:  # Skip header
                continue
            
            if len(row) > 13 and row[10] == superior_email and row[13] == approval_password:
                sheet.update_cell(idx + 1, 12, status)  # Status column
                sheet.update_cell(idx + 1, 13, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Approval date
                sheet.update_cell(idx + 1, 14, "USED")  # Mark password as used
                add_debug_log(f"Updated row {idx + 1} to status: {status}", "INFO")
                return True
        
        add_debug_log("No matching record found for approval", "WARNING")
        return False
        
    except Exception as e:
        st.error(f"❌ Error updating status: {str(e)}")
        add_debug_log(f"Update error: {traceback.format_exc()}", "ERROR")
        return False

# JavaScript for copying to clipboard
copy_js = """
<script>
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        var successElement = document.getElementById('copy-success');
        if (successElement) {
            successElement.style.display = 'block';
            setTimeout(function() {
                successElement.style.display = 'none';
            }, 2000);
        }
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}
</script>
"""

st.markdown(copy_js, unsafe_allow_html=True)

# ============================================
# SIDEBAR - EMAIL TESTING & CONFIGURATION
# ============================================
st.sidebar.title("🔧 Configuration Panel")

# Check current email configuration
email_config = check_email_configuration()

# Display current email status
st.sidebar.markdown("### 📧 Email Configuration")
if email_config["configured"]:
    st.sidebar.success(email_config["message"])
    st.sidebar.info(f"**Sender:** {email_config['sender_email']}")
    if 'password_type' in email_config:
        st.sidebar.info(f"**Password Type:** {email_config['password_type']}")
    st.sidebar.info(f"**Source:** {email_config['source']}")
else:
    st.sidebar.error(email_config["message"])
    st.sidebar.info(email_config["details"])

# Test Google Sheets connection
st.sidebar.markdown("---")
if st.sidebar.button("🔗 Test Google Sheets Connection"):
    with st.sidebar:
        with st.spinner("Testing connection..."):
            sheet = setup_google_sheets()
            if sheet:
                st.success("✅ Connected successfully!")
                st.info(f"Sheet: Leave_Applications")
                st.info(f"Rows: {sheet.row_count}")
            else:
                st.error("❌ Connection failed")

# Email Testing Section
st.sidebar.markdown("---")
st.sidebar.markdown("### 📧 Test Email Configuration")

# Show test email input
test_recipient = st.sidebar.text_input(
    "Test Recipient Email",
    value="",
    placeholder="Enter email to send test to",
    help="Leave empty to send test to yourself"
)

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🚀 Send Test Email", key="test_email_btn", use_container_width=True):
        with st.spinner("Sending test email..."):
            result = test_email_connection(test_recipient)
            st.session_state.test_email_result = result
            
            if result["success"]:
                st.session_state.email_config_status = "Working"
            else:
                st.session_state.email_config_status = "Failed"

with col2:
    if st.button("🔄 Clear Logs", key="clear_logs", use_container_width=True):
        st.session_state.debug_logs = []

# Show last test result if available
if st.session_state.test_email_result:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Last Test Result")
    if st.session_state.test_email_result["success"]:
        st.sidebar.success("✅ Last test: SUCCESS")
        st.sidebar.info(f"**Method:** {st.session_state.test_email_result.get('method', 'Unknown')}")
    else:
        st.sidebar.error("❌ Last test: FAILED")
        with st.sidebar.expander("View Error Details"):
            st.error(st.session_state.test_email_result.get('message', 'No error message'))
            st.info(st.session_state.test_email_result.get('details', 'No details'))

# Debug Logs Section
st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Debug Logs")
if st.sidebar.checkbox("Show Debug Logs", value=False):
    if st.session_state.debug_logs:
        debug_logs_html = "<div class='debug-log'>"
        for log in reversed(st.session_state.debug_logs[-10:]):  # Show last 10 logs
            if "ERROR" in log:
                debug_logs_html += f"<div style='color: #dc3545;'>{log}</div>"
            elif "SUCCESS" in log or "INFO" in log:
                debug_logs_html += f"<div style='color: #28a745;'>{log}</div>"
            elif "WARNING" in log:
                debug_logs_html += f"<div style='color: #ffc107;'>{log}</div>"
            else:
                debug_logs_html += f"<div>{log}</div>"
        debug_logs_html += "</div>"
        st.sidebar.markdown(debug_logs_html, unsafe_allow_html=True)
    else:
        st.sidebar.info("No debug logs yet")

# Email Configuration Help
st.sidebar.markdown("---")
with st.sidebar.expander("📖 Email Setup Guide"):
    st.markdown("""
    **Step-by-Step Gmail Configuration:**
    
    1. **Enable 2-Step Verification:**
       - Go to: https://myaccount.google.com/security
       - Click "2-Step Verification"
       - Follow prompts to enable it
    
    2. **Generate App Password:**
       - Go to: https://myaccount.google.com/apppasswords
       - Select "Mail" as app
       - Select "Other (Custom name)" as device
       - Name it "VOLAR FASHION Streamlit"
       - Click "Generate"
       - **Copy the 16-character password**
    
    3. **Update Streamlit Secrets:**
       - In Streamlit Cloud, go to App Settings → Secrets
       - Add this configuration:
    ```toml
    [EMAIL]
    sender_email = "hrvolarfashion@gmail.com"
    sender_password = "your-16-character-app-password"
    ```
    
    4. **Test Configuration:**
       - Click "Send Test Email" in sidebar
       - Check if test email is received
    
    **Common Issues:**
    - ❌ Using regular Gmail password → Use App Password
    - ❌ 2-Step Verification not enabled → Enable it first
    - ❌ Outdated password → Generate new App Password
    - ❌ Network issues → Wait and retry
    """)

# Email Status in Session State
if 'email_tested' not in st.session_state:
    st.session_state.email_tested = False

# ============================================
# MAIN APPLICATION
# ============================================

# Beautiful Company Header with Floating Animation
st.markdown("""
    <div class="company-header floating-element">
        <h1>VOLAR FASHION</h1>
        <h2>Leave Management System</h2>
    </div>
""", unsafe_allow_html=True)

# Create beautiful tabs
tab1, tab2 = st.tabs(["📝 Submit Leave Application", "✅ Approval Portal"])

with tab1:
    # Email status warning at top of form
    if not email_config["configured"] or st.session_state.email_config_status == "Failed":
        st.markdown(f'''
            <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                        border-left: 4px solid #ff9800; color: #856404;
                        padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 1.5rem; margin-right: 15px;">⚠️</div>
                    <div>
                        <strong>Email Configuration Issue Detected</strong><br>
                        <span style="font-size: 0.95rem;">
                            Emails may not be sent automatically. Please use the manual approval process below if email fails.
                            Test your email configuration in the sidebar.
                        </span>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    elif st.session_state.email_config_status == "Working":
        st.markdown(f'''
            <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                        border-left: 4px solid #28a745; color: #155724;
                        padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 1.5rem; margin-right: 15px;">✅</div>
                    <div>
                        <strong>Email Configuration Working</strong><br>
                        <span style="font-size: 0.95rem;">
                            Email notifications will be sent automatically to managers.
                        </span>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Form Header with Icon
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge">📋</div>
            <div>
                <h3 style="margin: 0;">Leave Application Form</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    Complete all fields below to submit your leave request
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Two-column layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        employee_name = st.text_input(
            "👤 Full Name",
            placeholder="Enter your full name",
            help="Please enter your complete name as per company records"
        )
        employee_code = st.text_input(
            "🔢 Employee ID",
            placeholder="e.g., VF-EMP-001",
            help="Your unique employee identification code"
        )
        department = st.selectbox(
            "🏛️ Department",
            ["Select Department"] + DEPARTMENTS,
            help="Select your department from the list"
        )
    
    with col2:
        leave_type = st.selectbox(
            "📋 Leave Type",
            ["Select Type", "Full Day", "Half Day", "Early Exit"],
            help="Select the type of leave you are requesting"
        )
        from_date = st.date_input(
            "📅 Start Date",
            min_value=datetime.now().date(),
            help="Select the first day of your leave"
        )
        till_date = st.date_input(
            "📅 End Date",
            min_value=datetime.now().date(),
            help="Select the last day of your leave"
        )
    
    # Duration Card with Animation
    if leave_type != "Select Type":
        no_of_days = calculate_days(from_date, till_date, leave_type)
        
        if leave_type != "Early Exit":
            st.markdown(f"""
                <div class="metric-card floating-element">
                    <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500;">Leave Duration</div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a; margin: 10px 0;">
                        {no_of_days}
                    </div>
                    <div style="font-size: 0.9rem; color: #805ad5;">days requested</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="thumbsup-box floating-element">
                    <div class="thumbsup-emoji">👍</div>
                    <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">Early Exit Request</div>
                    <div style="font-size: 0.95rem;">
                        You're requesting to leave early from work today. Only 2 Early Leaves are Permitted per month.
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        no_of_days = "N/A"
    
    # Purpose Section
    st.markdown("""
        <div style="margin-top: 2.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">📝</div>
                <div>
                    <h3 style="margin: 0;">Leave Details</h3>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                        Provide detailed information about your leave request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    purpose = st.text_area(
        "Purpose of Leave",
        placeholder="Please provide a clear and detailed explanation for your leave request...",
        height=120,
        help="Be specific about the reason for your leave"
    )
    
    # Manager Selection
    superior_name = st.selectbox(
        "👔 Reporting Manager",
        ["Select Manager"] + list(SUPERIORS.keys()),
        help="Select your direct reporting manager"
    )
    
    # Information Box
    st.markdown("""
        <div class="info-box">
            <div style="display: flex; align-items: flex-start;">
                <div style="font-size: 1.5rem; margin-right: 15px;">ℹ️</div>
                <div>
                    <strong style="display: block; margin-bottom: 8px;">Important Guidelines</strong>
                    • All fields are required for submission<br>
                    • Your manager will receive a secure approval code via email<br>
                    • Approval decisions are typically made within 24 hours<br>
                    • You'll be notified once a decision is made<br>
                    • For urgent requests, please contact your manager directly
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Submit Button with Beautiful Design
    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        if st.button("🚀 Submit Leave Request", type="primary", use_container_width=True):
            if not all([employee_name, employee_code, department != "Select Department", 
                        leave_type != "Select Type", purpose, superior_name != "Select Manager"]):
                st.markdown('''
                    <div class="error-message">
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <div style="font-size: 1.5rem; margin-right: 10px;">⚠️</div>
                            <div>
                                <strong>Please complete all required fields</strong><br>
                                Ensure all sections are properly filled before submission
                            </div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
            elif from_date > till_date:
                st.markdown('''
                    <div class="error-message">
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <div style="font-size: 1.5rem; margin-right: 10px;">📅</div>
                            <div>
                                <strong>Date Error</strong><br>
                                End date must be after or equal to start date
                            </div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                with st.spinner('Submitting your application...'):
                    # Prepare data
                    submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    superior_email = SUPERIORS[superior_name]
                    approval_password = generate_approval_password()
                    
                    # Prepare leave details
                    leave_details = {
                        "employee_name": employee_name,
                        "employee_code": employee_code,
                        "department": department,
                        "leave_type": leave_type,
                        "no_of_days": no_of_days,
                        "purpose": purpose,
                        "from_date": from_date.strftime("%Y-%m-%d"),
                        "till_date": till_date.strftime("%Y-%m-%d")
                    }
                    
                    # Connect to Google Sheets
                    sheet = setup_google_sheets()
                    
                    if sheet:
                        try:
                            # Prepare row data
                            row_data = [
                                submission_date,
                                employee_name,
                                employee_code,
                                department,
                                leave_type,
                                str(no_of_days),
                                purpose,
                                leave_details['from_date'],
                                leave_details['till_date'],
                                superior_name,
                                superior_email,
                                "Pending",
                                "",  # Approval Date (empty initially)
                                approval_password
                            ]
                            
                            # Write to Google Sheets
                            sheet.append_row(row_data)
                            add_debug_log(f"Data written to Google Sheets for {employee_name}", "SUCCESS")
                            
                            # Try to send email only if configuration is working
                            email_sent = False
                            email_error = ""
                            
                            if email_config["configured"]:
                                try:
                                    email_sent = send_approval_email(
                                        employee_name,
                                        superior_name,
                                        superior_email,
                                        leave_details,
                                        approval_password
                                    )
                                    if not email_sent:
                                        email_error = "Email sending failed - check debug logs"
                                except Exception as e:
                                    email_error = f"Email exception: {str(e)}"
                                    add_debug_log(f"Email exception: {traceback.format_exc()}", "ERROR")
                            
                            if email_sent:
                                st.markdown('''
                                    <div class="success-message">
                                        <div style="font-size: 3rem; margin-bottom: 1rem;">✨</div>
                                        <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 10px; color: #166534;">
                                            Application Submitted Successfully!
                                        </div>
                                        <div style="color: #155724; margin-bottom: 15px;">
                                            Your leave request has been sent to your manager for approval.
                                        </div>
                                        <div style="font-size: 0.95rem; color: #0f5132; opacity: 0.9;">
                                            You will receive a notification once a decision is made.
                                        </div>
                                    </div>
                                ''', unsafe_allow_html=True)
                                
                                st.balloons()
                                time.sleep(3)
                                st.rerun()
                            else:
                                # Show manual approval code section
                                st.session_state.approval_code_to_copy = approval_password
                                st.session_state.show_copy_section = True
                                
                                st.markdown(f'''
                                    <div class="info-box">
                                        <div style="display: flex; align-items: flex-start;">
                                            <div style="font-size: 1.5rem; margin-right: 15px; color: #ff9800;">📧</div>
                                            <div>
                                                <strong style="display: block; margin-bottom: 8px; color: #ff9800;">Email Notification Issue</strong>
                                                Your application was saved to the database successfully!<br>
                                                However, we couldn't send the email notification automatically.<br>
                                                <small>{email_error}</small>
                                            </div>
                                        </div>
                                    </div>
                                ''', unsafe_allow_html=True)
                                
                                # Manual approval code section
                                st.markdown("---")
                                st.markdown("""
                                    <div style="text-align: center; margin: 2rem 0;">
                                        <div style="font-size: 1.3rem; font-weight: 600; color: #673ab7; margin-bottom: 1rem;">
                                            📋 Manual Approval Process
                                        </div>
                                        <p style="color: #718096; margin-bottom: 1.5rem;">
                                            Please share this approval code with your manager <strong>{}</strong>:
                                        </p>
                                    </div>
                                """.format(superior_name), unsafe_allow_html=True)
                                
                                # Approval code display with copy button
                                st.markdown(f"""
                                    <div style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); 
                                                padding: 2rem; border-radius: 16px; text-align: center; 
                                                margin: 1.5rem 0; border: 2px dashed #673ab7;">
                                        <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500; margin-bottom: 10px;">
                                            Approval Code for {superior_name}
                                        </div>
                                        <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a; 
                                                    letter-spacing: 4px; margin: 15px 0; font-family: 'Courier New', monospace;">
                                            {approval_password}
                                        </div>
                                        <div style="font-size: 0.9rem; color: #805ad5; margin-bottom: 20px;">
                                            5-character code (valid for single use)
                                        </div>
                                        
                                        <button class="copy-code-btn" onclick="copyToClipboard('{approval_password}')">
                                            📋 Copy Approval Code
                                        </button>
                                        <div id="copy-success" class="copy-success">✅ Copied to clipboard!</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Instructions for manager
                                st.markdown("""
                                    <div style="background: #e8f5e9; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0;">
                                        <strong style="color: #2e7d32; display: block; margin-bottom: 10px;">
                                            ✅ Instructions for your Manager:
                                        </strong>
                                        <ol style="color: #388e3c; margin-left: 20px;">
                                            <li>Visit: <strong>https://hr-application-rtundoncudkzt9efwnscey.streamlit.app/</strong></li>
                                            <li>Click on "✅ Approval Portal" tab</li>
                                            <li>Enter email: <strong>{}</strong></li>
                                            <li>Enter approval code: <strong>{}</strong></li>
                                            <li>Select Approve or Reject</li>
                                            <li>Click Submit Decision</li>
                                        </ol>
                                    </div>
                                """.format(superior_email, approval_password), unsafe_allow_html=True)
                                
                                st.balloons()
                                
                        except Exception as e:
                            st.markdown(f'''
                                <div class="error-message">
                                    <div style="display: flex; align-items: center; justify-content: center;">
                                        <div style="font-size: 1.5rem; margin-right: 10px;">❌</div>
                                        <div>
                                            <strong>Submission Error</strong><br>
                                            Please try again or contact HR<br>
                                            Error: {str(e)}
                                        </div>
                                    </div>
                                </div>
                            ''', unsafe_allow_html=True)
                            add_debug_log(f"Submission error: {traceback.format_exc()}", "ERROR")
                    else:
                        st.markdown('''
                            <div class="error-message">
                                <div style="display: flex; align-items: center; justify-content: center;">
                                    <div style="font-size: 1.5rem; margin-right: 10px;">📊</div>
                                    <div>
                                        <strong>Database Connection Error</strong><br>
                                        Could not connect to database. Please try again later.
                                    </div>
                                </div>
                            </div>
                        ''', unsafe_allow_html=True)

with tab2:
    # Approval Portal Header
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">✅</div>
            <div>
                <h3 style="margin: 0;">Manager Approval Portal</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    Securely approve or reject leave requests using your approval code
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Security Info
    st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; 
                    border: 1px solid rgba(33, 150, 243, 0.2);">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 1.5rem; margin-right: 15px; color: #2196f3;">🔒</div>
                <div>
                    <strong style="color: #0d47a1;">Secure Authentication Required</strong><br>
                    <span style="color: #1565c0; font-size: 0.95rem;">
                        Use the unique approval code sent to your email for authentication
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Form Fields
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        superior_email_input = st.text_input(
            "📧 Manager Email",
            placeholder="your.email@volarfashion.com",
            help="Enter your registered manager email address"
        )
    
    with col2:
        approval_password_input = st.text_input(
            "🔑 Approval Code",
            type="password",
            placeholder="Enter 5-character code",
            help="Enter the unique code from the approval email"
        )
    
    # Decision Section
    st.markdown("---")
    
    st.markdown("""
        <div style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);">📋</div>
                <div>
                    <h4 style="margin: 0;">Decision</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        Select your decision for this leave request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    action = st.selectbox(
        "Select Action",
        ["Select Decision", "✅ Approve", "❌ Reject"],
        label_visibility="collapsed"
    )
    
    # Submit Decision Button
    if st.button("Submit Decision", type="primary", use_container_width=True):
        if not all([superior_email_input, approval_password_input, action != "Select Decision"]):
            st.markdown('''
                <div class="error-message">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <div style="font-size: 1.5rem; margin-right: 10px;">⚠️</div>
                        <div>
                            <strong>Missing Information</strong><br>
                            Please complete all fields and select a decision
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        elif superior_email_input not in SUPERIORS.values():
            st.markdown('''
                <div class="error-message">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <div style="font-size: 1.5rem; margin-right: 10px;">📧</div>
                        <div>
                            <strong>Unauthorized Access</strong><br>
                            This email is not authorized for approvals
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        elif len(approval_password_input) != 5:
            st.markdown('''
                <div class="error-message">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <div style="font-size: 1.5rem; margin-right: 10px;">🔑</div>
                            <div>
                            <strong>Invalid Code Format</strong><br>
                            Please enter the exact 5-character code from your email
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            with st.spinner("Processing your decision..."):
                sheet = setup_google_sheets()
                if sheet:
                    status = "Approved" if action == "✅ Approve" else "Rejected"
                    success = update_leave_status(sheet, superior_email_input, approval_password_input, status)
                    
                    if success:
                        status_color = "#155724" if status == "Approved" else "#721c24"
                        status_bg = "#d4edda" if status == "Approved" else "#f8d7da"
                        status_icon = "✅" if status == "Approved" else "❌"
                        
                        st.markdown(f'''
                            <div style="background: {status_bg}; border-left: 4px solid {status_color}; 
                                      color: {status_color}; padding: 2rem; border-radius: 16px; 
                                      margin: 2rem 0; text-align: center; animation: slideIn 0.5s ease-out;">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">{status_icon}</div>
                                <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 10px;">
                                    Decision Submitted Successfully!
                                </div>
                                <div style="margin-bottom: 15px;">
                                    The leave request has been <strong>{status.lower()}</strong>.
                                </div>
                                <div style="font-size: 0.95rem; opacity: 0.9;">
                                    The employee has been notified of your decision.
                                </div>
                            </div>
                        ''', unsafe_allow_html=True)
                        
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.markdown('''
                            <div class="error-message">
                                <div style="display: flex; align-items: center; justify-content: center;">
                                    <div style="font-size: 1.5rem; margin-right: 10px;">🔐</div>
                                    <div>
                                        <strong>Authentication Failed</strong><br>
                                        Invalid code or code already used.<br>
                                        Please check your email or contact HR for assistance.
                                    </div>
                                </div>
                            </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.markdown('''
                        <div class="error-message">
                            <div style="display: flex; align-items: center; justify-content: center;">
                                <div style="font-size: 1.5rem; margin-right: 10px;">📊</div>
                                <div>
                                    <strong>Database Connection Error</strong><br>
                                    Could not connect to database. Please try again later.
                                </div>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        <div style="margin-bottom: 1rem;">
            <strong style="color: #673ab7;">VOLAR FASHION PVT LTD</strong><br>
            Human Resources Management System
        </div>
        <div style="font-size: 0.9rem;">
            📧 hrvolarfashion@gmail.com<br>
            © 2024 VOLAR FASHION.
        </div>
    </div>
""", unsafe_allow_html=True)
