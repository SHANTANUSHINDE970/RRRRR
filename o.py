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
from email.utils import formataddr
import socket
import uuid
import hashlib

# Page configuration
st.set_page_config(
    page_title="VOLAR FASHION - Leave Management",
    page_icon="\u2728",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Beautiful Elegant CSS with Premium Design - DARK MODE COMPATIBLE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600&display=swap');
    
    :root {
        --primary-color: #673ab7;
        --secondary-color: #9c27b0;
        --accent-color: #2196f3;
        --success-color: #28a745;
        --warning-color: #ff9800;
        --danger-color: #dc3545;
        --text-primary: #1a1a1a;
        --text-secondary: #4a5568;
        --text-light: #718096;
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9ff;
        --bg-tertiary: #f5f7fa;
        --border-color: #e2e8f0;
        --card-bg: #ffffff;
        --input-bg: #fafbfc;
        --shadow-color: rgba(103, 58, 183, 0.08);
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-color: #9c6bff;
            --secondary-color: #d179ff;
            --accent-color: #64b5f6;
            --success-color: #4caf50;
            --warning-color: #ffb74d;
            --danger-color: #f44336;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e0;
            --text-light: #a0aec0;
            --bg-primary: #1a202c;
            --bg-secondary: #2d3748;
            --bg-tertiary: #4a5568;
            --border-color: #4a5568;
            --card-bg: #2d3748;
            --input-bg: #4a5568;
            --shadow-color: rgba(0, 0, 0, 0.3);
        }
    }
    
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: var(--bg-primary) !important; }
        .main { background-color: var(--bg-primary) !important; }
        .stTextInput input,
        .stSelectbox select,
        .stTextArea textarea,
        .stDateInput input,
        .stNumberInput input {
            color: var(--text-primary) !important;
            background-color: var(--input-bg) !important;
            border-color: var(--border-color) !important;
        }
        .stTextInput label,
        .stSelectbox label,
        .stTextArea label,
        .stDateInput label,
        .stNumberInput label { color: var(--text-secondary) !important; }
        .stTextInput input::placeholder,
        .stSelectbox select::placeholder,
        .stTextArea textarea::placeholder,
        .stDateInput input::placeholder {
            color: var(--text-light) !important;
            opacity: 0.7;
        }
    }
    
    * { font-family: 'Inter', sans-serif; color: var(--text-primary); }
    
    .main {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        background-attachment: fixed;
    }
    
    .form-container {
        background: var(--card-bg);
        padding: 3.5rem;
        border-radius: 24px;
        box-shadow: 0 20px 60px var(--shadow-color);
        margin: 2rem auto;
        max-width: 1000px;
        border: 1px solid rgba(103, 58, 183, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .form-container:before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
    }
    
    h1 {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
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
        color: var(--text-light);
        text-align: center;
        font-size: 1.6rem;
        margin-bottom: 3rem;
        font-weight: 400;
        font-family: 'Inter', sans-serif;
        opacity: 0.9;
    }
    
    h3 {
        color: var(--text-secondary);
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
        bottom: 0; left: 0;
        width: 60px; height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: 2px;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
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
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(103, 58, 183, 0.35);
    }
    
    .stTextInput>div>div>input {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stSelectbox>div>div>select {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
    }
    
    .stTextArea>div>div>textarea {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
    }
    
    .stDateInput>div>div>input {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus,
    .stDateInput>div>div>input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 4px rgba(103, 58, 183, 0.1) !important;
        background: var(--card-bg) !important;
        outline: none !important;
    }
    
    .stTextInput>div>label,
    .stSelectbox>div>label,
    .stTextArea>div>label,
    .stDateInput>div>label {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
    }
    
    p, span, div, li { color: var(--text-primary); }
    
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid var(--success-color);
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
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid var(--danger-color);
        color: #721c24;
        padding: 1.75rem;
        border-radius: 16px;
        text-align: center;
        font-weight: 500;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(220, 53, 69, 0.1);
    }
    
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid var(--accent-color);
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
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border: 1px solid var(--border-color);
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
        color: var(--text-secondary) !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
        display: block;
    }
    
    .footer {
        text-align: center;
        color: var(--text-light);
        padding: 3rem 2rem;
        margin-top: 4rem;
        position: relative;
    }
    
    .footer:before {
        content: '';
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 200px; height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: var(--card-bg);
        padding: 12px;
        border-radius: 16px;
        border: 1px solid rgba(103, 58, 183, 0.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--card-bg);
        border-radius: 12px;
        color: var(--text-light);
        font-weight: 500;
        padding: 12px 28px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border-color: var(--primary-color);
        box-shadow: 0 4px 12px rgba(103, 58, 183, 0.2);
    }
    
    .company-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem;
        background: var(--card-bg);
        border-radius: 24px;
        box-shadow: 0 15px 40px rgba(103, 58, 183, 0.08);
        border: 1px solid rgba(103, 58, 183, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .company-header:before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
    }
    
    .icon-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px; height: 40px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        margin-right: 12px;
        font-size: 1.2rem;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .floating-element { animation: float 6s ease-in-out infinite; }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-tertiary); border-radius: 4px; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 4px;
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
    
    .cluster-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 2px solid #3b82f6;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
    }
    
    .cluster-header h3 { color: #ffffff !important; margin: 0; }
    .cluster-header p { color: #dbeafe !important; margin: 5px 0 0 0; font-size: 0.95rem; }
    
    .holidays-table-wrapper {
        display: flex;
        justify-content: center;
        width: 100%;
        margin: 2rem 0;
    }
    
    .holidays-table-wrapper table {
        border-collapse: collapse;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        max-width: 800px;
        background-color: var(--card-bg);
    }
    
    .holidays-table-wrapper th {
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        color: white;
        font-weight: 600;
        padding: 1rem 1.5rem;
        text-align: left;
        font-size: 1rem;
    }
    
    .holidays-table-wrapper td {
        padding: 1rem 1.5rem;
        font-size: 0.95rem;
        border-bottom: 1px solid var(--border-color);
        color: var(--text-primary);
    }
    
    .holidays-table-wrapper tr:last-child td { border-bottom: none; }
    .holidays-table-wrapper tr:nth-child(even) { background-color: rgba(103, 58, 183, 0.05); }
    .holidays-table-wrapper tr:hover { background-color: rgba(103, 58, 183, 0.1); }
    
    .day-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .day-saturday { background: rgba(33, 150, 243, 0.1); color: #2196f3; border: 1px solid rgba(33, 150, 243, 0.2); }
    .day-sunday { background: rgba(244, 67, 54, 0.1); color: #f44336; border: 1px solid rgba(244, 67, 54, 0.2); }
    .day-weekday { background: rgba(76, 175, 80, 0.1); color: #4caf50; border: 1px solid rgba(76, 175, 80, 0.2); }
    
    .debug-log {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 10px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        max-height: 200px;
        overflow-y: auto;
    }
    
    @media (prefers-color-scheme: dark) {
        section[data-testid="stSidebar"] { background-color: var(--bg-secondary) !important; }
        section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
    }
    </style>
""", unsafe_allow_html=True)

# Superior details dictionary
SUPERIORS = {
    "Jaya Tahilramani": "hrvolarfashion@gmail.com",
    "Sandip Gawankar": "hrvolarfashion@gmail.com",
    "Tariq Patel": "dn1@vfemails.com",
    "Sarath Kumar": "Sarath@vfemails.com",
    "Rajeev Thakur": "Rajeev@vfemails.com",
    "Ayushi Jain": "ayushi@volarfashion.in",
    "Akshaya Shinde": "Akshaya@vfemails.com",
    "Vitika Mehta": "vitika@vfemails.com",
    "Mohammed Tahir": "tahir@vfemails.com",
    "Hr": "hrvolarfashion@gmail.com",
    "Krishna Yadav": "Krishna@vfemails.com",
    "Manish Gupta": "Manish@vfemails.com",
    "Shantanu Shinde": "s37@vfemails.com"
}

DEPARTMENTS = [
    "Accounts and Finance", "Administration", "Business Development", "Content",
    "E-Commerce", "Factory & Production", "Graphics", "Human Resources", "IT",
    "Social Media", "Bandra Store", "Support Staff", "Warehouse", "SEO"
]

WFH_APPROVALS = ["Select Approval", "Jaya Mam", "Sandip Sir", "Verbal from HR"]

HOLIDAYS_2026 = [
    {"date": "01-Jan", "day": "Thursday", "holiday": "New Year"},
    {"date": "26-Jan", "day": "Monday", "holiday": "Republic Day"},
    {"date": "04-Mar", "day": "Wednesday", "holiday": "Holi"},
    {"date": "20-Mar", "day": "Friday", "holiday": "Ramzan Eid"},
    {"date": "01-May", "day": "Friday", "holiday": "Maharashtra Day"},
    {"date": "15-Aug", "day": "Saturday", "holiday": "Independence Day"},
    {"date": "14-Sep", "day": "Monday", "holiday": "Ganesh Chaturthi"},
    {"date": "02-Oct", "day": "Friday", "holiday": "Gandhi Jayanti"},
    {"date": "21-Oct", "day": "Wednesday", "holiday": "Vijaydashmi"},
    {"date": "08-Nov", "day": "Sunday", "holiday": "Diwali"},
    {"date": "11-Nov", "day": "Wednesday", "holiday": "Bhai Dooj"},
    {"date": "25-Dec", "day": "Friday", "holiday": "Christmas"}
]

# Initialize session state
if 'clusters' not in st.session_state:
    st.session_state.clusters = [{
        'cluster_number': 1, 'leave_type': 'Select Type',
        'from_date': datetime.now().date(), 'till_date': datetime.now().date(), 'approval_code': ''
    }]
if 'reset_form_tab1' not in st.session_state: st.session_state.reset_form_tab1 = False
if 'reset_form_tab2' not in st.session_state: st.session_state.reset_form_tab2 = False
if 'reset_form_tab4' not in st.session_state: st.session_state.reset_form_tab4 = False
if 'form_data_tab1' not in st.session_state:
    st.session_state.form_data_tab1 = {
        'employee_name': '', 'employee_code': '', 'employee_email': '',
        'department': 'Select Department', 'purpose': '',
        'superior_name': 'Select Manager', 'is_cluster': False
    }
if 'form_data_tab2' not in st.session_state:
    st.session_state.form_data_tab2 = {'approval_password': '', 'action': 'Select Decision'}
if 'form_data_tab4' not in st.session_state:
    st.session_state.form_data_tab4 = {
        'employee_name': '', 'employee_code': '', 'request_type': 'Select Type',
        'start_date': datetime.now().date(), 'end_date': datetime.now().date(),
        'reason': '', 'approval_from': 'Select Approval'
    }
if 'cluster_codes' not in st.session_state: st.session_state.cluster_codes = {}
if 'show_copy_section' not in st.session_state: st.session_state.show_copy_section = False
if 'test_email_result' not in st.session_state: st.session_state.test_email_result = None
if 'email_config_status' not in st.session_state: st.session_state.email_config_status = "Not Tested"
if 'debug_logs' not in st.session_state: st.session_state.debug_logs = []
if 'generated_codes' not in st.session_state: st.session_state.generated_codes = set()
if 'submission_in_progress' not in st.session_state: st.session_state.submission_in_progress = False
if 'submission_completed' not in st.session_state: st.session_state.submission_completed = False
if 'last_submission_hash' not in st.session_state: st.session_state.last_submission_hash = None
if 'submission_timestamp' not in st.session_state: st.session_state.submission_timestamp = None
if 'last_wfh_submission_hash' not in st.session_state: st.session_state.last_wfh_submission_hash = None
if 'wfh_submission_timestamp' not in st.session_state: st.session_state.wfh_submission_timestamp = None


def add_debug_log(message, level="INFO"):
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"
    st.session_state.debug_logs.append(log_entry)
    if len(st.session_state.debug_logs) > 50:
        st.session_state.debug_logs.pop(0)
    print(f"[{level}] {message}")


def log_debug(message):
    add_debug_log(message, "DEBUG")
    st.sidebar.text(f"{datetime.now().strftime('%H:%M:%S')}: {message}")


def get_existing_codes_from_sheet(sheet):
    try:
        if not sheet:
            return set()
        all_records = sheet.get_all_values()
        existing_codes = set()
        for idx, row in enumerate(all_records):
            if idx == 0:
                continue
            if len(row) > 14 and row[14]:
                existing_codes.add(row[14])
        log_debug(f"Found {len(existing_codes)} existing codes in sheet")
        return existing_codes
    except Exception as e:
        log_debug(f"Error getting existing codes: {str(e)}")
        return set()


def generate_approval_password(sheet=None):
    alphabet = string.ascii_uppercase + string.digits
    alphabet = alphabet.replace('0', '').replace('O', '').replace('1', '').replace('I', '').replace('L', '')
    existing_codes = set()
    if sheet:
        existing_codes = get_existing_codes_from_sheet(sheet)
    existing_codes.update(st.session_state.generated_codes)
    max_attempts = 20
    for attempt in range(max_attempts):
        password = ''.join(secrets.choice(alphabet) for _ in range(5))
        if password not in existing_codes:
            st.session_state.generated_codes.add(password)
            log_debug(f"Generated unique approval password: {password} (attempt {attempt + 1})")
            return password
    log_debug(f"Could not generate unique random code after {max_attempts} attempts, using fallback method")
    timestamp = int(time.time() * 1000)
    base36 = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
    code = ""
    temp_timestamp = timestamp
    while temp_timestamp > 0 and len(code) < 3:
        temp_timestamp, remainder = divmod(temp_timestamp, 36)
        code = base36[remainder] + code
    while len(code) < 5:
        code = code + secrets.choice(base36)
    if code not in existing_codes:
        st.session_state.generated_codes.add(code)
        return code
    for i in range(1, 100):
        fallback_code = f"{code[:4]}{i}"
        if fallback_code not in existing_codes:
            st.session_state.generated_codes.add(fallback_code)
            return fallback_code
    final_code = str(uuid.uuid4().int)[:5].upper()
    final_code = ''.join([c for c in final_code if c in alphabet])
    while len(final_code) < 5:
        final_code = final_code + secrets.choice(alphabet)
    st.session_state.generated_codes.add(final_code)
    return final_code


def get_google_credentials():
    try:
        log_debug("Loading Google credentials from Streamlit secrets...")
        creds_dict = None
        if 'google_credentials' in st.secrets:
            log_debug("Found google_credentials in secrets")
            try:
                creds_dict = {
                    "type": st.secrets["google_credentials"]["type"],
                    "project_id": st.secrets["google_credentials"]["project_id"],
                    "private_key_id": st.secrets["google_credentials"]["private_key_id"],
                    "private_key": st.secrets["google_credentials"]["private_key"],
                    "client_email": st.secrets["google_credentials"]["client_email"],
                    "client_id": st.secrets["google_credentials"]["client_id"],
                    "auth_uri": st.secrets["google_credentials"]["auth_uri"],
                    "token_uri": st.secrets["google_credentials"]["token_uri"],
                    "auth_provider_x509_cert_url": st.secrets["google_credentials"]["auth_provider_x509_cert_url"],
                    "client_x509_cert_url": st.secrets["google_credentials"]["client_x509_cert_url"]
                }
            except KeyError as e:
                log_debug(f"Missing key in google_credentials: {str(e)}")
                st.error(f"Missing credential field in google_credentials: {str(e)}")
                return None
        elif 'google' in st.secrets:
            log_debug("Found google in secrets")
            try:
                creds_dict = {
                    "type": st.secrets["google"]["type"],
                    "project_id": st.secrets["google"]["project_id"],
                    "private_key_id": st.secrets["google"]["private_key_id"],
                    "private_key": st.secrets["google"]["private_key"],
                    "client_email": st.secrets["google"]["client_email"],
                    "client_id": st.secrets["google"]["client_id"],
                    "auth_uri": st.secrets["google"]["auth_uri"],
                    "token_uri": st.secrets["google"]["token_uri"],
                    "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
                    "client_x509_cert_url": st.secrets["google"]["client_x509_cert_url"]
                }
            except KeyError as e:
                log_debug(f"Missing key in google: {str(e)}")
                st.error(f"Missing credential field in google: {str(e)}")
                return None
        else:
            log_debug("Google credentials not found in secrets")
            st.error("Google credentials not found in Streamlit secrets")
            return None

        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        missing_fields = [field for field in required_fields if not creds_dict.get(field)]
        if missing_fields:
            log_debug(f"Missing Google credential fields: {missing_fields}")
            st.error(f"Missing Google credential fields: {', '.join(missing_fields)}")
            return None

        private_key = creds_dict.get("private_key", "")
        if private_key:
            if "-----BEGIN PRIVATE KEY-----" not in private_key:
                if "\\n" in private_key:
                    private_key = private_key.replace("\\n", "\n")
                elif "MII" in private_key[:100]:
                    private_key = f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----"
            if "\n" not in private_key and "\\n" in private_key:
                private_key = private_key.replace("\\n", "\n")
            creds_dict["private_key"] = private_key
            log_debug("Processed private key formatting")

        log_debug(f"Google credentials loaded for: {creds_dict['client_email']}")
        return creds_dict
    except Exception as e:
        log_debug(f"Error getting Google credentials: {traceback.format_exc()}")
        st.error(f"Error loading Google credentials: {str(e)}")
        return None


def setup_google_sheets():
    try:
        log_debug("Setting up Google Sheets connection...")
        SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = get_google_credentials()
        if not creds_dict:
            st.error("No Google credentials found")
            return None
        if not creds_dict.get("private_key"):
            st.error("Google private key not found in credentials")
            return None
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
            log_debug("Successfully created ServiceAccountCredentials")
        except Exception as cred_error:
            log_debug(f"Error creating credentials: {str(cred_error)}")
            raise cred_error
        client = gspread.authorize(creds)
        SHEET_NAME = "Leave_Applications"
        try:
            spreadsheet = client.open(SHEET_NAME)
            sheet = spreadsheet.sheet1
            log_debug(f"Successfully connected to sheet: {SHEET_NAME}")
            try:
                if sheet.row_count == 0 or not sheet.row_values(1):
                    headers = [
                        "Submission Date", "Employee Code", "Employee Name", "Department",
                        "Type of Leave", "No of Days", "Purpose of Leave", "From Date",
                        "To Date", "Superior or Team leader Name", "Superior or Team leader Email",
                        "Status", "Approval Date", "Approval Password", "Cluster (Yes/No)",
                        "Cluster leave Number", "Employee email"
                    ]
                    sheet.append_row(headers)
                    log_debug("Added headers to sheet")
            except Exception as e:
                log_debug(f"Warning: Could not check/add headers: {str(e)}")
            return sheet
        except gspread.SpreadsheetNotFound:
            st.error(f"Google Sheet '{SHEET_NAME}' not found!")
            st.info(f"Please create a sheet named '{SHEET_NAME}' and share it with: {creds_dict.get('client_email', 'service account email')}")
            return None
        except Exception as e:
            st.error(f"Error accessing sheet: {str(e)}")
            return None
    except Exception as e:
        st.error(f"Error in setup_google_sheets: {str(e)}")
        log_debug(f"setup_google_sheets error: {traceback.format_exc()}")
        return None


def setup_wfh_sheet():
    try:
        log_debug("Setting up WFH Google Sheets connection...")
        SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = get_google_credentials()
        if not creds_dict:
            log_debug("No Google credentials found")
            return None
        if not creds_dict.get("private_key"):
            log_debug("Google private key not found in credentials")
            return None
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
            log_debug("Successfully created ServiceAccountCredentials for WFH")
        except Exception as cred_error:
            log_debug(f"Error creating credentials for WFH: {str(cred_error)}")
            raise cred_error
        client = gspread.authorize(creds)
        SHEET_NAME = "Leave_Applications"
        try:
            spreadsheet = client.open(SHEET_NAME)
            try:
                sheet = spreadsheet.worksheet("Sheet2")
                log_debug(f"Successfully connected to Sheet2 in: {SHEET_NAME}")
            except gspread.exceptions.WorksheetNotFound:
                log_debug("Sheet2 not found, creating new sheet...")
                sheet = spreadsheet.add_worksheet(title="Sheet2", rows=100, cols=20)
                log_debug("Created Sheet2 successfully")
            try:
                if sheet.row_count == 0 or not sheet.row_values(1):
                    headers = [
                        "Submission Date", "Employee Name", "Employee Code", "Request Type",
                        "Start Date", "End Date", "Reason", "Approval From", "Status", "Approval Date"
                    ]
                    sheet.append_row(headers)
                    log_debug("Added headers to WFH sheet (Sheet2)")
            except Exception as e:
                log_debug(f"Warning: Could not check/add headers to WFH sheet: {str(e)}")
            return sheet
        except gspread.SpreadsheetNotFound:
            log_debug(f"Google Sheet '{SHEET_NAME}' not found!")
            st.error(f"Google Sheet '{SHEET_NAME}' not found!")
            return None
        except Exception as e:
            log_debug(f"Error accessing WFH sheet: {str(e)}")
            st.error(f"Error accessing WFH sheet: {str(e)}")
            return None
    except Exception as e:
        log_debug(f"setup_wfh_sheet error: {traceback.format_exc()}")
        st.error(f"Error in setup_wfh_sheet: {str(e)}")
        return None


def get_email_credentials():
    try:
        log_debug("Getting email credentials from secrets...")
        possible_sections = ['EMAIL', 'email', 'gmail', 'GMAIL']
        sender_email = None
        sender_password = None
        source = ""
        for section in possible_sections:
            if section in st.secrets:
                log_debug(f"Found email section: {section}")
                try:
                    if isinstance(st.secrets[section], dict):
                        sender_email = st.secrets[section].get("sender_email") or st.secrets[section].get("email") or st.secrets[section].get("EMAIL")
                        sender_password = st.secrets[section].get("sender_password") or st.secrets[section].get("password") or st.secrets[section].get("PASSWORD")
                    else:
                        sender_email = st.secrets[section]
                    if sender_email and sender_password:
                        source = section
                        break
                except Exception as e:
                    log_debug(f"Error reading {section} section: {str(e)}")
        if not sender_email or not sender_password:
            log_debug("Trying direct secret names...")
            sender_email = st.secrets.get("EMAIL_SENDER") or st.secrets.get("sender_email") or st.secrets.get("email")
            sender_password = st.secrets.get("EMAIL_PASSWORD") or st.secrets.get("sender_password") or st.secrets.get("password")
            if sender_email and sender_password:
                source = "Direct Secrets"
        if sender_email and sender_password:
            log_debug(f"Email credentials loaded for: {sender_email}")
            log_debug(f"Password length: {len(sender_password)} characters")
            if len(sender_password) == 16:
                log_debug("Password appears to be a Gmail App Password (16 chars)")
            elif " " in sender_password:
                log_debug("WARNING: Password contains spaces")
            return sender_email, sender_password, source
        else:
            log_debug("Email credentials not found in secrets")
            return "", "", "Not Found"
    except Exception as e:
        log_debug(f"Error getting email credentials: {str(e)}")
        return "", "", f"Error: {str(e)}"


def check_email_configuration():
    sender_email, sender_password, source = get_email_credentials()
    if not sender_email or not sender_password:
        return {"configured": False, "message": "Email credentials not found", "details": "Please check your Streamlit secrets", "source": source}
    if "@" not in sender_email or "." not in sender_email:
        return {"configured": False, "message": "Invalid email format", "details": f"Email '{sender_email}' doesn't look valid", "source": source}
    if len(sender_password) == 16 and ' ' not in sender_password:
        password_type = "App Password"
    elif len(sender_password) > 0:
        password_type = "Regular Password"
    else:
        password_type = "Unknown"
    return {
        "configured": True, "sender_email": sender_email, "source": source,
        "password_type": password_type, "password_length": len(sender_password),
        "message": f"Email credentials found ({password_type})"
    }


def create_smtp_connection(sender_email, sender_password):
    server = None
    connection_method = ""
    error_messages = []
    try:
        log_debug("Trying SMTP_SSL on port 465...")
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10, context=context)
        server.login(sender_email, sender_password)
        connection_method = "SMTP_SSL (Port 465)"
        log_debug(f"Connection successful via {connection_method}")
        return server, connection_method
    except Exception as e1:
        error_messages.append(f"Port 465 failed: {str(e1)}")
        log_debug(f"Port 465 failed: {str(e1)}")
        if server:
            try: server.quit()
            except: pass
    try:
        log_debug("Trying STARTTLS on port 587...")
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(sender_email, sender_password)
        connection_method = "STARTTLS (Port 587)"
        log_debug(f"Connection successful via {connection_method}")
        return server, connection_method
    except Exception as e2:
        error_messages.append(f"Port 587 failed: {str(e2)}")
        log_debug(f"Port 587 failed: {str(e2)}")
        if server:
            try: server.quit()
            except: pass
    for port in [25, 2525]:
        try:
            log_debug(f"Trying port {port}...")
            if port in [465]:
                server = smtplib.SMTP_SSL('smtp.gmail.com', port, timeout=10)
            else:
                server = smtplib.SMTP('smtp.gmail.com', port, timeout=10)
                server.starttls(context=ssl.create_default_context())
            server.login(sender_email, sender_password)
            connection_method = f"Port {port}"
            return server, connection_method
        except Exception as e:
            error_messages.append(f"Port {port} failed: {str(e)}")
            if server:
                try: server.quit()
                except: pass
    return None, f"All methods failed: {' | '.join(error_messages)}"


def test_email_connection(test_recipient=None):
    try:
        log_debug("Starting email connection test...")
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            return {"success": False, "message": "Email credentials not configured",
                    "details": "Please check your Streamlit secrets",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        recipient = test_recipient or sender_email
        log_debug(f"Recipient: {recipient}")
        msg = MIMEMultipart()
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = recipient
        msg['Subject'] = "VOLAR FASHION - Email Configuration Test"
        test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = f"""
        This is a test email from VOLAR FASHION Leave and WFH / Out of office request.

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
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, recipient, msg.as_string())
                server.quit()
                return {"success": True, "message": f"Email sent successfully via {method}",
                        "details": f"Test email sent to {recipient} at {test_time}",
                        "method": method, "sender": sender_email, "timestamp": test_time}
            except Exception as e:
                try: server.quit()
                except: pass
                error_msg = str(e)
                log_debug(f"Error sending test email: {error_msg}")
                return {"success": False, "message": "Failed to send email",
                        "details": f"Error: {error_msg}", "sender": sender_email, "timestamp": test_time}
        else:
            return {"success": False, "message": "SMTP Connection Failed",
                    "details": f"Error: {method}", "sender": sender_email, "timestamp": test_time}
    except Exception as e:
        log_debug(f"Unexpected error in test_email_connection: {traceback.format_exc()}")
        return {"success": False, "message": "Unexpected Error",
                "details": f"Error: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


def calculate_working_days(from_date, till_date):
    total_days = (till_date - from_date).days + 1
    return total_days


def calculate_days(from_date, till_date, leave_type):
    if leave_type == "Half Day":
        return 0.5
    elif leave_type == "Early Exit":
        return ""
    else:
        return calculate_working_days(from_date, till_date)


def add_data_to_sheet1(sheet, row_data):
    try:
        log_debug(f"Looking for next empty row in Sheet1...")
        all_records = sheet.get_all_values()
        next_row = 2
        found_empty_row = False
        if len(all_records) > 1:
            for i in range(1, len(all_records)):
                row = all_records[i]
                if not any(cell.strip() for cell in row):
                    next_row = i + 1
                    found_empty_row = True
                    log_debug(f"Found empty row at position {next_row}")
                    break
            if not found_empty_row:
                next_row = len(all_records) + 1
                log_debug(f"No empty rows found, adding at row {next_row}")
        else:
            next_row = 2
            log_debug(f"Only header exists, adding at row {next_row}")
        log_debug(f"Inserting data at row {next_row}")
        sheet.insert_row(row_data, index=next_row)
        log_debug(f"Data inserted at row {next_row}")
        return True
    except Exception as e:
        log_debug(f"Error adding data to Sheet1: {str(e)}")
        log_debug(f"Error details: {traceback.format_exc()}")
        return False


def add_data_to_sheet2(sheet, row_data):
    try:
        log_debug(f"Looking for next empty row in Sheet2...")
        all_records = sheet.get_all_values()
        next_row = 2
        found_empty_row = False
        if len(all_records) > 1:
            for i in range(1, len(all_records)):
                row = all_records[i]
                if not any(cell.strip() for cell in row):
                    next_row = i + 1
                    found_empty_row = True
                    log_debug(f"Found empty row at position {next_row}")
                    break
            if not found_empty_row:
                next_row = len(all_records) + 1
                log_debug(f"No empty rows found, adding at row {next_row}")
        else:
            next_row = 2
            log_debug(f"Only header exists, adding at row {next_row}")
        log_debug(f"Inserting data at row {next_row}")
        sheet.insert_row(row_data, index=next_row)
        log_debug(f"Data inserted at row {next_row}")
        return True
    except Exception as e:
        log_debug(f"Error adding data to Sheet2: {str(e)}")
        log_debug(f"Error details: {traceback.format_exc()}")
        return False


def send_approval_email(employee_name, superior_name, superior_email, employee_email, clusters_data, cluster_codes):
    try:
        log_debug(f"Preparing to send approval email to {superior_email}")
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            st.warning("Email credentials not configured")
            return False
        if "@" not in superior_email or "." not in superior_email:
            st.warning(f"Invalid superior email format: {superior_email}")
            return False
        try:
            app_url = st.secrets.get("APP_URL", "https://9yq6u8fklhfba8uggnjr7h.streamlit.app/")
        except:
            app_url = "https://9yq6u8fklhfba8uggnjr7h.streamlit.app/"

        # Build clusters details HTML
        clusters_html = ""
        for i, cluster in enumerate(clusters_data):
            days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
            days_display = "N/A" if cluster['leave_type'] == "Early Exit" else (f"{days} days" if cluster['leave_type'] == "Full Day" else "0.5 day")
            clusters_html += f"""
            <div style="background: {'#f8f9ff' if i % 2 == 0 else '#f0f2ff'}; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4dabf7;">
                <h4 style="margin-top: 0; color: #339af0;">Period {i+1}</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 5px; width: 40%;"><strong>Leave Type:</strong></td><td style="padding: 5px;">{cluster['leave_type']}</td></tr>
                    <tr><td style="padding: 5px;"><strong>From Date:</strong></td><td style="padding: 5px;">{cluster['from_date'].strftime('%Y-%m-%d')}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Till Date:</strong></td><td style="padding: 5px;">{cluster['till_date'].strftime('%Y-%m-%d')}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Duration:</strong></td><td style="padding: 5px;">{days_display}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Approval Code:</strong></td>
                        <td style="padding: 5px;"><span style="background: #fff3cd; padding: 5px 10px; border-radius: 4px; font-family: 'Courier New', monospace; font-weight: bold; letter-spacing: 2px;">{cluster_codes.get(i, 'CODE MISSING')}</span></td>
                    </tr>
                </table>
            </div>
            """

        msg_superior = MIMEMultipart('alternative')
        msg_superior['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg_superior['To'] = superior_email
        if len(clusters_data) > 1:
            msg_superior['Subject'] = f"CLUSTER LEAVE: {employee_name} - {len(clusters_data)} periods"
        else:
            msg_superior['Subject'] = f"Leave Approval Required: {employee_name}"

        html_body_superior = f"""
        <html><head><style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
        .instructions {{ background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style></head><body>
        <div class="container">
            <div class="header"><h2 style="margin: 0;">Leave Approval Required</h2><p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p></div>
            <p>Dear {superior_name},</p>
            <div class="info-box">
                <h3 style="margin-top: 0; color: #673ab7;">Employee Information</h3>
                <p><strong>Employee Name:</strong> {employee_name}</p>
                <p><strong>Employee Email:</strong> {employee_email if employee_email else 'Not provided'}</p>
                <p><strong>Employee Code:</strong> {clusters_data[0].get('employee_code', 'N/A')}</p>
                <p><strong>Department:</strong> {clusters_data[0].get('department', 'N/A')}</p>
                <p><strong>Total Periods:</strong> {len(clusters_data)}</p>
                <p><strong>Purpose:</strong> {clusters_data[0].get('purpose', 'N/A')}</p>
            </div>
            <h3 style="color: #339af0;">Leave Periods Details</h3>
            {clusters_html}
            <div class="instructions">
                <h4 style="margin-top: 0; color: #2e7d32;">How to Approve/Reject:</h4>
                <ol>
                    <li>Visit: <a href="{app_url}">{app_url}</a></li>
                    <li>Click on "Approval Portal" tab</li>
                    <li>For each period: Enter the specific approval code mentioned above</li>
                    <li>Select Approve or Reject for that period</li>
                    <li>Click Submit Decision</li>
                    <li>Repeat for each period with its specific code</li>
                </ol>
                <p><strong>Note:</strong> Each code can only be used once for its specific period.</p>
            </div>
            <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com<br>This is an automated message.</div>
        </div></body></html>
        """
        msg_superior.attach(MIMEText(html_body_superior, 'html'))

        # Employee confirmation email
        msg_employee = None
        if employee_email and "@" in employee_email:
            msg_employee = MIMEMultipart('alternative')
            msg_employee['From'] = formataddr(("VOLAR FASHION HR", sender_email))
            msg_employee['To'] = employee_email
            if len(clusters_data) > 1:
                msg_employee['Subject'] = f"Leave Application Submitted: {len(clusters_data)} periods"
            else:
                msg_employee['Subject'] = "Leave Application Submitted Successfully"

            employee_clusters_html = ""
            for i, cluster in enumerate(clusters_data):
                days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
                days_display = "N/A" if cluster['leave_type'] == "Early Exit" else (f"{days} days" if cluster['leave_type'] == "Full Day" else "0.5 day")
                employee_clusters_html += f"""
                <div style="background: {'#f8f9ff' if i % 2 == 0 else '#f0f2ff'}; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4dabf7;">
                    <h4 style="margin-top: 0; color: #339af0;">Period {i+1}</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 5px; width: 40%;"><strong>Leave Type:</strong></td><td style="padding: 5px;">{cluster['leave_type']}</td></tr>
                        <tr><td style="padding: 5px;"><strong>From Date:</strong></td><td style="padding: 5px;">{cluster['from_date'].strftime('%Y-%m-%d')}</td></tr>
                        <tr><td style="padding: 5px;"><strong>Till Date:</strong></td><td style="padding: 5px;">{cluster['till_date'].strftime('%Y-%m-%d')}</td></tr>
                        <tr><td style="padding: 5px;"><strong>Duration:</strong></td><td style="padding: 5px;">{days_display}</td></tr>
                    </table>
                </div>
                """

            html_body_employee = f"""
            <html><head><style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
            .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
            .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
            </style></head><body>
            <div class="container">
                <div class="header"><h2 style="margin: 0;">Leave Application Confirmation</h2><p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p></div>
                <p>Dear {employee_name},</p>
                <div class="info-box">
                    <h3 style="margin-top: 0; color: #4caf50;">Application Submitted Successfully</h3>
                    <p>Your leave application has been submitted and sent to your manager for approval.</p>
                    <p><strong>Employee Code:</strong> {clusters_data[0].get('employee_code', 'N/A')}</p>
                    <p><strong>Department:</strong> {clusters_data[0].get('department', 'N/A')}</p>
                    <p><strong>Reporting Manager:</strong> {superior_name}</p>
                    <p><strong>Purpose:</strong> {clusters_data[0].get('purpose', 'N/A')}</p>
                    <p><strong>Total Periods:</strong> {len(clusters_data)}</p>
                </div>
                <h3 style="color: #339af0;">Your Leave Periods</h3>
                {employee_clusters_html}
                <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2196f3;">
                    <h4 style="margin-top: 0; color: #0d47a1;">Next Steps:</h4>
                    <ol>
                        <li>Your manager <strong>{superior_name}</strong> has been notified</li>
                        <li>You will receive another email once your leave is approved or rejected</li>
                        <li>Each period will be approved/rejected separately</li>
                        <li>Please check your email regularly for updates</li>
                    </ol>
                </div>
                <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com<br>This is an automated confirmation email.</div>
            </div></body></html>
            """
            msg_employee.attach(MIMEText(html_body_employee, 'html'))

        log_debug(f"Creating SMTP connection for emails")
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, superior_email, msg_superior.as_string())
                log_debug(f"Approval email sent to {superior_email}")
                if msg_employee and employee_email and "@" in employee_email:
                    try:
                        server.sendmail(sender_email, employee_email, msg_employee.as_string())
                        log_debug(f"Confirmation email sent to {employee_email}")
                    except Exception as e:
                        log_debug(f"Could not send confirmation to employee: {str(e)}")
                server.quit()
                return True
            except Exception as e:
                try: server.quit()
                except: pass
                log_debug(f"Failed to send emails: {str(e)}")
                st.error(f"Failed to send emails: {str(e)}")
                return False
        else:
            log_debug(f"Could not establish SMTP connection: {method}")
            st.error(f"Could not establish SMTP connection: {method}")
            return False
    except Exception as e:
        log_debug(f"Error in send_approval_email: {traceback.format_exc()}")
        st.error(f"Email sending error: {str(e)}")
        return False


def send_decision_email_to_employee(employee_name, employee_email, superior_name, status, cluster_info=None, cluster_number=None, total_clusters=None):
    try:
        log_debug(f"Preparing to send decision email to employee: {employee_email}")
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            return False
        if not employee_email or "@" not in employee_email:
            return False
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = employee_email
        if cluster_number and total_clusters and total_clusters > 1:
            msg['Subject'] = f"Leave Period {cluster_number}/{total_clusters} {status} - {employee_name}"
        else:
            msg['Subject'] = f"Leave Application {status} - {employee_name}"
        status_color = "#4caf50" if status == "Approved" else "#f44336"
        status_bg = "#e8f5e9" if status == "Approved" else "#ffebee"
        status_icon = "Approved" if status == "Approved" else "Rejected"
        cluster_details = ""
        if cluster_info:
            days = calculate_days(
                datetime.strptime(cluster_info['from_date'], "%Y-%m-%d").date() if isinstance(cluster_info['from_date'], str) else cluster_info['from_date'],
                datetime.strptime(cluster_info['till_date'], "%Y-%m-%d").date() if isinstance(cluster_info['till_date'], str) else cluster_info['till_date'],
                cluster_info['leave_type']
            )
            days_display = "N/A" if cluster_info['leave_type'] == "Early Exit" else (f"{days} days" if cluster_info['leave_type'] == "Full Day" else "0.5 day")
            from_date_str = cluster_info['from_date'].strftime('%Y-%m-%d') if hasattr(cluster_info['from_date'], 'strftime') else cluster_info['from_date']
            till_date_str = cluster_info['till_date'].strftime('%Y-%m-%d') if hasattr(cluster_info['till_date'], 'strftime') else cluster_info['till_date']
            cluster_label = f"Period {cluster_number}" if cluster_number and total_clusters and total_clusters > 1 else "Leave Period"
            cluster_details = f"""
            <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4dabf7;">
                <h4 style="margin-top: 0; color: #339af0;">{cluster_label} Details</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 5px; width: 40%;"><strong>Leave Type:</strong></td><td style="padding: 5px;">{cluster_info['leave_type']}</td></tr>
                    <tr><td style="padding: 5px;"><strong>From Date:</strong></td><td style="padding: 5px;">{from_date_str}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Till Date:</strong></td><td style="padding: 5px;">{till_date_str}</td></tr>
                    <tr><td style="padding: 5px;"><strong>Duration:</strong></td><td style="padding: 5px;">{days_display}</td></tr>
                </table>
            </div>
            """
        if status == "Approved":
            status_message = """<div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50;">
                <h4 style="margin-top: 0; color: #2e7d32;">Approval Confirmation</h4>
                <p>Your leave request has been approved. You can proceed with your leave plans as scheduled.</p></div>"""
        else:
            status_message = f"""<div style="background: #ffebee; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #f44336;">
                <h4 style="margin-top: 0; color: #c62828;">Rejection Notification</h4>
                <p>Your leave request has been rejected. Please contact <strong>{superior_name}</strong> for more information.</p></div>"""
        html_body = f"""
        <html><head><style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, {status_color} 0%, {status_color}80 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .info-box {{ background: {status_bg}; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style></head><body>
        <div class="container">
            <div class="header"><h2 style="margin: 0;">Leave Application {status_icon}</h2><p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p></div>
            <p>Dear {employee_name},</p>
            <div class="info-box">
                <h3 style="margin-top: 0; color: {status_color};">Your leave request has been {status.lower()}</h3>
                <p><strong>Decision:</strong> <span style="color: {status_color}; font-weight: bold;">{status}</span></p>
                <p><strong>Approved/Rejected by:</strong> {superior_name}</p>
                <p><strong>Decision Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                {cluster_details}
                {status_message}
                <div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 8px; border-left: 4px solid #2196f3;">
                    <h4 style="margin-top: 0; color: #0d47a1;">Next Steps:</h4>
                    {'<p>You can proceed with your leave plans as scheduled.</p>' if status == 'Approved' else '<p>Please contact your manager for more information or to discuss alternative arrangements.</p>'}
                </div>
            </div>
            <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com<br>This is an automated notification.</div>
        </div></body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, employee_email, msg.as_string())
                server.quit()
                log_debug(f"Decision email sent to employee: {employee_email}")
                return True
            except Exception as e:
                try: server.quit()
                except: pass
                log_debug(f"Failed to send decision email to employee: {str(e)}")
                return False
        return False
    except Exception as e:
        log_debug(f"Error in send_decision_email_to_employee: {traceback.format_exc()}")
        return False


def send_decision_email_to_superior(employee_name, employee_email, superior_name, superior_email, status, approval_password):
    try:
        log_debug(f"Preparing to send decision confirmation email to superior: {superior_email}")
        sender_email, sender_password, source = get_email_credentials()
        if not sender_email or not sender_password:
            return False
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = superior_email
        msg['Subject'] = f"Leave Decision Recorded: {employee_name} - {status}"
        html_body = f"""
        <html><head><style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .success-box {{ background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50; }}
        .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
        </style></head><body>
        <div class="container">
            <div class="header"><h2 style="margin: 0;">Decision Confirmation</h2><p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p></div>
            <p>Dear {superior_name},</p>
            <div class="success-box">
                <h3 style="margin-top: 0; color: #2e7d32;">Decision Successfully Recorded</h3>
                <p>You have successfully <strong>{status.lower()}</strong> the leave request for <strong>{employee_name}</strong>.</p>
            </div>
            <div class="info-box">
                <h3 style="margin-top: 0; color: #673ab7;">Decision Details</h3>
                <p><strong>Employee Name:</strong> {employee_name}</p>
                <p><strong>Employee Email:</strong> {employee_email if employee_email else 'Not provided'}</p>
                <p><strong>Decision:</strong> <span style="color: {'#4caf50' if status == 'Approved' else '#f44336'}; font-weight: bold;">{status}</span></p>
                <p><strong>Approval Code Used:</strong> {approval_password}</p>
                <p><strong>Decision Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div class="footer">VOLAR FASHION PVT LTD - HR Department<br>hrvolarfashion@gmail.com<br>This is an automated confirmation.</div>
        </div></body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        server, method = create_smtp_connection(sender_email, sender_password)
        if server:
            try:
                server.sendmail(sender_email, superior_email, msg.as_string())
                server.quit()
                log_debug(f"Decision confirmation sent to superior: {superior_email}")
                return True
            except Exception as e:
                try: server.quit()
                except: pass
                log_debug(f"Failed to send decision email to superior: {str(e)}")
                return False
        return False
    except Exception as e:
        log_debug(f"Error in send_decision_email_to_superior: {traceback.format_exc()}")
        return False


def update_leave_status(sheet, approval_password, status):
    try:
        all_records = sheet.get_all_values()
        for idx, row in enumerate(all_records):
            if idx == 0:
                continue
            if len(row) > 13 and row[13] == approval_password:
                sheet.update_cell(idx + 1, 12, status)
                sheet.update_cell(idx + 1, 13, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                employee_name = row[2] if len(row) > 2 else ""
                employee_email = row[16] if len(row) > 16 else ""
                superior_name = row[9] if len(row) > 9 else ""
                superior_email = row[10] if len(row) > 10 else ""
                cluster_info = None
                if len(row) > 4:
                    cluster_info = {
                        'leave_type': row[4] if len(row) > 4 else "",
                        'from_date': row[7] if len(row) > 7 else "",
                        'till_date': row[8] if len(row) > 8 else ""
                    }
                is_cluster = row[14] if len(row) > 14 else "No"
                cluster_number = None
                if is_cluster == "Yes" and len(row) > 15:
                    cluster_number = row[15] if row[15] else None
                total_clusters = None
                if is_cluster == "Yes" and employee_name:
                    total_clusters = 0
                    for record in all_records[1:]:
                        if len(record) > 2 and record[2] == employee_name and len(record) > 14 and record[14] == "Yes":
                            total_clusters += 1
                log_debug(f"Updated row {idx + 1} to status: {status}")
                if employee_email and "@" in employee_email:
                    send_decision_email_to_employee(employee_name, employee_email, superior_name, status, cluster_info, cluster_number, total_clusters)
                if superior_email and "@" in superior_email:
                    send_decision_email_to_superior(employee_name, employee_email, superior_name, superior_email, status, approval_password)
                return True
        log_debug("No matching record found for approval")
        return False
    except Exception as e:
        st.error(f"Error updating status: {str(e)}")
        log_debug(f"Update error: {traceback.format_exc()}")
        return False


def submit_wfh_request(employee_name, employee_code, request_type, start_date, end_date, reason, approval_from):
    try:
        log_debug(f"Submitting WFH/Out of Office request for: {employee_name}")
        sheet = setup_wfh_sheet()
        if not sheet:
            log_debug("Failed to connect to WFH Google Sheet (Sheet2)")
            return False, "Database connection failed. Please check your Google Sheets setup."
        submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [
            submission_date, employee_name.strip(), employee_code.strip(),
            request_type.strip(), start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"),
            reason.strip(), approval_from.strip(), "Submitted", ""
        ]
        try:
            write_success = add_data_to_sheet2(sheet, row_data)
            if write_success:
                log_debug(f"WFH request written to Sheet2 for {employee_name}")
                try:
                    sender_email, sender_password, source = get_email_credentials()
                    if sender_email and sender_password:
                        msg = MIMEMultipart()
                        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
                        msg['To'] = sender_email
                        if request_type == "Work From Home":
                            msg['Subject'] = f"WFH Request Submitted: {employee_name}"
                        else:
                            msg['Subject'] = f"Out of Office Request Submitted: {employee_name}"
                        body = f"""
New WFH/Out of Office Request Submitted:

Employee Name: {employee_name}
Employee Code: {employee_code}
Request Type: {request_type}
Start Date: {start_date.strftime('%Y-%m-%d')}
End Date: {end_date.strftime('%Y-%m-%d')}
Duration: {(end_date - start_date).days + 1} day(s)
Approval From: {approval_from}
Submission Date: {submission_date}

Reason:
{reason}

--
VOLAR FASHION HR System
                        """
                        msg.attach(MIMEText(body, 'plain'))
                        server, method = create_smtp_connection(sender_email, sender_password)
                        if server:
                            server.sendmail(sender_email, sender_email, msg.as_string())
                            server.quit()
                            log_debug("Notification email sent to HR")
                except Exception as email_error:
                    log_debug(f"Could not send notification email: {str(email_error)}")
                return True, "Request submitted successfully!"
            else:
                return False, "Error submitting request to database"
        except Exception as e:
            log_debug(f"Error in write operation to WFH Google Sheets: {str(e)}")
            return False, f"Error submitting request: {str(e)}"
    except Exception as e:
        log_debug(f"Error in submit_wfh_request: {traceback.format_exc()}")
        return False, f"Error: {str(e)}"


def generate_submission_hash(form_data):
    data_string = f"{form_data['employee_name']}_{form_data['employee_code']}_{form_data['purpose']}_{datetime.now().strftime('%Y%m%d')}"
    return hashlib.md5(data_string.encode()).hexdigest()


def check_duplicate_submission(form_data):
    current_hash = generate_submission_hash(form_data)
    if st.session_state.last_submission_hash == current_hash:
        if st.session_state.submission_timestamp:
            time_diff = (datetime.now() - st.session_state.submission_timestamp).total_seconds()
            if time_diff < 30:
                return True, "You have already submitted this form. Please wait before submitting again."
    return False, ""


def generate_wfh_hash(form_data):
    data_string = f"{form_data['employee_name']}_{form_data['employee_code']}_{form_data['request_type']}_{form_data['start_date']}_{form_data['end_date']}_{form_data['reason']}_{datetime.now().strftime('%Y%m%d')}"
    return hashlib.md5(data_string.encode()).hexdigest()


def check_duplicate_wfh_submission(form_data):
    current_hash = generate_wfh_hash(form_data)
    if st.session_state.get('last_wfh_submission_hash') == current_hash:
        if st.session_state.get('wfh_submission_timestamp'):
            time_diff = (datetime.now() - st.session_state.wfh_submission_timestamp).total_seconds()
            if time_diff < 30:
                return True, "You have already submitted this WFH/Out of Office form. Please wait before submitting again."
    return False, ""


# ============================================
# SIDEBAR
# ============================================
st.sidebar.title("Configuration Panel")
email_config = check_email_configuration()
st.sidebar.markdown("### Email Configuration")
if email_config["configured"]:
    st.sidebar.success(email_config["message"])
    st.sidebar.info(f"**Sender:** {email_config['sender_email']}")
    if 'password_type' in email_config:
        st.sidebar.info(f"**Password Type:** {email_config['password_type']}")
    if 'password_length' in email_config:
        st.sidebar.info(f"**Password Length:** {email_config['password_length']} chars")
    st.sidebar.info(f"**Source:** {email_config['source']}")
else:
    st.sidebar.error(email_config["message"])
    st.sidebar.info(email_config["details"])

st.sidebar.markdown("---")
if st.sidebar.button("Test Google Sheets Connection"):
    with st.sidebar:
        with st.spinner("Testing connection..."):
            sheet = setup_google_sheets()
            if sheet:
                st.success("Connected successfully!")
                st.info(f"Sheet: Leave_Applications")
                st.info(f"Rows: {sheet.row_count}")
            else:
                st.error("Connection failed")

st.sidebar.markdown("---")
st.sidebar.markdown("### Test Email Configuration")
test_recipient = st.sidebar.text_input(
    "Test Recipient Email", value="",
    placeholder="Enter email to send test to",
    help="Leave empty to send test to yourself"
)
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Send Test Email", key="test_email_btn", use_container_width=True):
        with st.spinner("Sending test email..."):
            result = test_email_connection(test_recipient)
            st.session_state.test_email_result = result
            if result["success"]:
                st.session_state.email_config_status = "Working"
                st.sidebar.success("Test email sent successfully!")
            else:
                st.session_state.email_config_status = "Failed"
                st.sidebar.error("Test email failed")
with col2:
    if st.button("Clear Logs", key="clear_logs", use_container_width=True):
        st.session_state.debug_logs = []

if st.session_state.test_email_result:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Last Test Result")
    if st.session_state.test_email_result["success"]:
        st.sidebar.success("Last test: SUCCESS")
        st.sidebar.info(f"**Method:** {st.session_state.test_email_result.get('method', 'Unknown')}")
    else:
        st.sidebar.error("Last test: FAILED")
        with st.sidebar.expander("View Error Details"):
            st.error(st.session_state.test_email_result.get('message', 'No error message'))
            st.info(st.session_state.test_email_result.get('details', 'No details'))

st.sidebar.markdown("---")
st.sidebar.markdown("### Debug Logs")
if st.sidebar.checkbox("Show Debug Logs", value=False):
    if st.session_state.debug_logs:
        debug_logs_html = "<div class='debug-log'>"
        for log in reversed(st.session_state.debug_logs[-10:]):
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

st.sidebar.markdown("---")
with st.sidebar.expander("Email Setup Guide"):
    st.markdown("""
    **Step-by-Step Gmail Configuration:**

    1. **Enable 2-Step Verification:**
       - Go to: https://myaccount.google.com/security

    2. **Generate App Password:**
       - Go to: https://myaccount.google.com/apppasswords
       - Select "Mail" and "Other (Custom name)"
       - Name it "VOLAR FASHION Streamlit"
       - Copy the 16-character password

    3. **Update Streamlit Secrets:**
    ```toml
    [EMAIL]
    sender_email = "hrvolarfashion@gmail.com"
    sender_password = "your-16-character-app-password"
    ```

    4. **Test Configuration:** Click "Send Test Email" in sidebar
    """)

# ============================================
# MAIN APPLICATION
# ============================================
st.markdown("""
    <div class="company-header floating-element">
        <h1>VOLAR FASHION</h1>
        <h2>Leave and WFH / Out of office request</h2>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "\U0001f4dd Submit Leave Application",
    "\u2705 Approval Portal",
    "\U0001f4c5 Company Holidays",
    "\U0001f3e0 WFH / Out of Office"
])

# ============================================
# TAB 1: SUBMIT LEAVE APPLICATION
# ============================================
with tab1:
    if not email_config["configured"] or st.session_state.email_config_status == "Failed":
        st.markdown("""
            <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                        border-left: 4px solid #ff9800; color: #856404;
                        padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 1.5rem; margin-right: 15px;">&#x26A0;&#xFE0F;</div>
                    <div>
                        <strong>Email Configuration Issue Detected</strong><br>
                        <span style="font-size: 0.95rem;">
                            Emails may not be sent automatically. Please use the manual approval process below if email fails.
                            Test your email configuration in the sidebar.
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif st.session_state.email_config_status == "Working":
        st.markdown("""
            <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                        border-left: 4px solid #28a745; color: #155724;
                        padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 1.5rem; margin-right: 15px;">&#x2705;</div>
                    <div>
                        <strong>Email Configuration Working</strong><br>
                        <span style="font-size: 0.95rem;">
                            Email notifications will be sent automatically to managers and employees.
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="section-header">
            <div class="icon-badge">&#x1F4CB;</div>
            <div>
                <h3 style="margin: 0;">Leave Application Form</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    Complete all fields below to submit your leave request
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.reset_form_tab1:
        st.session_state.form_data_tab1 = {
            'employee_name': '', 'employee_code': '', 'employee_email': '',
            'department': 'Select Department', 'purpose': '',
            'superior_name': 'Select Manager', 'is_cluster': False
        }
        st.session_state.clusters = [{
            'cluster_number': 1, 'leave_type': 'Select Type',
            'from_date': datetime.now().date(), 'till_date': datetime.now().date(), 'approval_code': ''
        }]
        st.session_state.cluster_codes = {}
        st.session_state.reset_form_tab1 = False
        st.session_state.submission_in_progress = False
        st.session_state.submission_completed = True

    col1, col2, col3 = st.columns([1, 1, 1], gap="large")
    with col1:
        employee_name = st.text_input(
            "Full Name", value=st.session_state.form_data_tab1['employee_name'],
            placeholder="Enter your full name", key="employee_name_input"
        )
    with col2:
        employee_code = st.text_input(
            "Employee ID", value=st.session_state.form_data_tab1['employee_code'],
            placeholder="e.g., VF-EMP-001", key="employee_code_input"
        )
    with col3:
        employee_email = st.text_input(
            "Employee Email", value=st.session_state.form_data_tab1['employee_email'],
            placeholder="your.email@company.com", key="employee_email_input"
        )

    col4, col5 = st.columns([1, 1], gap="large")
    with col4:
        department = st.selectbox(
            "Department", ["Select Department"] + DEPARTMENTS, index=0,
            help="Select your department from the list", key="department_select"
        )
    with col5:
        is_cluster = st.checkbox(
            "Is this a Cluster Holiday? (Multiple leave periods)",
            value=st.session_state.form_data_tab1['is_cluster'],
            help="Check this if you need to apply for multiple separate leave periods",
            key="is_cluster_checkbox"
        )

    if is_cluster:
        st.markdown("""
            <div class="cluster-section">
                <div class="cluster-header">
                    <div class="icon-badge" style="background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);">&#x1F4C5;</div>
                    <div>
                        <h3 style="margin: 0; color: #ffffff !important;">Cluster Holiday Periods</h3>
                        <p style="margin: 5px 0 0 0; color: #4dabf7; font-size: 0.95rem;">
                            Add multiple leave periods below (each will have separate approval code)
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        total_clusters = len(st.session_state.clusters)
        for i, cluster in enumerate(st.session_state.clusters):
            st.markdown(f"<h4 style='color: #339af0;'>Period {i+1}</h4>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                leave_type = st.selectbox(
                    f"Leave Type - Period {i+1}",
                    ["Select Type", "Full Day", "Half Day", "Early Exit"],
                    index=0 if cluster['leave_type'] == 'Select Type' else ["Select Type", "Full Day", "Half Day", "Early Exit"].index(cluster['leave_type']),
                    key=f"leave_type_cluster_{i}"
                )
                st.session_state.clusters[i]['leave_type'] = leave_type
            with col2:
                if leave_type in ["Half Day", "Early Exit"]:
                    selected_date = st.date_input(
                        f"Date - Period {i+1}", value=cluster['from_date'],
                        min_value=datetime.now().date(), key=f"date_cluster_{i}"
                    )
                    st.session_state.clusters[i]['from_date'] = selected_date
                    st.session_state.clusters[i]['till_date'] = selected_date
                else:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        from_date = st.date_input(
                            f"From - Period {i+1}", value=cluster['from_date'],
                            min_value=datetime.now().date(), key=f"from_date_cluster_{i}"
                        )
                        st.session_state.clusters[i]['from_date'] = from_date
                    with col_b:
                        till_date = st.date_input(
                            f"To - Period {i+1}", value=cluster['till_date'],
                            min_value=datetime.now().date(), key=f"till_date_cluster_{i}"
                        )
                        st.session_state.clusters[i]['till_date'] = till_date
            with col3:
                if leave_type != "Select Type":
                    no_of_days = calculate_days(
                        st.session_state.clusters[i]['from_date'],
                        st.session_state.clusters[i]['till_date'], leave_type
                    )
                    days_display = "N/A" if leave_type == "Early Exit" else ("0.5" if leave_type == "Half Day" else str(no_of_days))
                    st.markdown(f"""
                        <div style="background: #e3f2fd; padding: 10px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 0.8rem; color: #1976d2;">Days</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: #0d47a1;">{days_display}</div>
                        </div>
                    """, unsafe_allow_html=True)
            with col4:
                if total_clusters > 1:
                    if st.button("Remove", key=f"remove_cluster_{i}"):
                        st.session_state.clusters.pop(i)
                        st.rerun()

        if st.button("Add Another Period", key="add_cluster"):
            new_cluster_number = len(st.session_state.clusters) + 1
            st.session_state.clusters.append({
                'cluster_number': new_cluster_number, 'leave_type': 'Select Type',
                'from_date': datetime.now().date(), 'till_date': datetime.now().date(), 'approval_code': ''
            })
            st.rerun()

        total_days = 0
        for cluster in st.session_state.clusters:
            if cluster['leave_type'] == "Full Day":
                total_days += calculate_working_days(cluster['from_date'], cluster['till_date'])
            elif cluster['leave_type'] == "Half Day":
                total_days += 0.5

        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);
                        color: white; padding: 1rem; border-radius: 12px; text-align: center; margin: 1rem 0;">
                <div style="font-size: 0.9rem;">Total Working Days</div>
                <div style="font-size: 2rem; font-weight: bold;">{total_days}</div>
                <div style="font-size: 0.8rem;">across {len(st.session_state.clusters)} period(s)</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="margin-top: 2rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">&#x1F4C5;</div>
                    <div>
                        <h3 style="margin: 0;">Leave Details</h3>
                        <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                            Enter your leave period details
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            leave_type = st.selectbox(
                "Leave Type", ["Select Type", "Full Day", "Half Day", "Early Exit"],
                index=0, help="Select the type of leave you are requesting", key="leave_type_single"
            )
        with col2:
            if leave_type in ["Half Day", "Early Exit"]:
                selected_date = st.date_input(
                    "Date", value=st.session_state.clusters[0]['from_date'],
                    min_value=datetime.now().date(),
                    help="Select the date for your leave", key="date_single"
                )
                from_date = selected_date
                till_date = selected_date
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    from_date = st.date_input(
                        "Start Date", value=st.session_state.clusters[0]['from_date'],
                        min_value=datetime.now().date(),
                        help="Select the first day of your leave", key="from_date_single"
                    )
                with col_b:
                    till_date = st.date_input(
                        "End Date", value=st.session_state.clusters[0]['till_date'],
                        min_value=datetime.now().date(),
                        help="Select the last day of your leave", key="till_date_single"
                    )

        st.session_state.clusters[0]['leave_type'] = leave_type
        st.session_state.clusters[0]['from_date'] = from_date
        st.session_state.clusters[0]['till_date'] = till_date

        if leave_type != "Select Type":
            no_of_days = calculate_days(from_date, till_date, leave_type)
            if leave_type == "Early Exit":
                st.markdown("""
                    <div class="thumbsup-box floating-element">
                        <div class="thumbsup-emoji">&#x1F44D;</div>
                        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">Early Exit Request</div>
                        <div style="font-size: 0.95rem;">
                            You are requesting to leave early. Only 1 Early Leave is permitted per month.
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            elif leave_type == "Half Day":
                st.markdown("""
                    <div class="metric-card floating-element">
                        <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500;">Leave Duration</div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a; margin: 10px 0;">0.5</div>
                        <div style="font-size: 0.9rem; color: #805ad5;">half day</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="metric-card floating-element">
                        <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500;">Leave Duration</div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a; margin: 10px 0;">{no_of_days}</div>
                        <div style="font-size: 0.9rem; color: #805ad5;">working days</div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("""
        <div style="margin-top: 2.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">&#x1F4DD;</div>
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
        "Purpose of Leave", value=st.session_state.form_data_tab1['purpose'],
        placeholder="Please provide a clear and detailed explanation for your leave request...",
        height=120, help="Be specific about the reason for your leave", key="purpose_textarea"
    )

    superior_name = st.selectbox(
        "Reporting Manager or Team Leader",
        ["Select Manager"] + list(SUPERIORS.keys()), index=0,
        help="Select your direct reporting manager", key="superior_select"
    )

    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        submit_button_disabled = st.session_state.get('submission_in_progress', False)
        if submit_button_disabled:
            st.info("Processing your submission... Please wait.")
        submit_button = st.button(
            "Submit Leave Request", type="primary", use_container_width=True,
            key="submit_leave_request", disabled=submit_button_disabled
        )

        if submit_button and not submit_button_disabled:
            st.session_state.submission_in_progress = True
            st.session_state.submission_completed = False
            form_data_for_check = {
                'employee_name': employee_name, 'employee_code': employee_code, 'purpose': purpose
            }
            is_duplicate, duplicate_message = check_duplicate_submission(form_data_for_check)
            if is_duplicate:
                st.session_state.submission_in_progress = False
                st.markdown(f"""
                    <div class="error-message">
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <div style="font-size: 1.5rem; margin-right: 10px;">&#x26A0;&#xFE0F;</div>
                            <div>
                                <strong>Duplicate Submission Detected</strong><br>
                                {duplicate_message}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                validation_passed = True
                error_messages = []
                if not all([employee_name, employee_code, employee_email,
                            department != "Select Department", purpose, superior_name != "Select Manager"]):
                    validation_passed = False
                    error_messages.append("Please complete all required fields")
                if employee_email and ("@" not in employee_email or "." not in employee_email):
                    validation_passed = False
                    error_messages.append("Please enter a valid email address")
                for i, cluster in enumerate(st.session_state.clusters):
                    if cluster['leave_type'] == "Select Type":
                        validation_passed = False
                        error_messages.append(f"Please select leave type for Period {i+1}")
                        break
                    if cluster['leave_type'] == "Full Day":
                        if cluster['from_date'] > cluster['till_date']:
                            validation_passed = False
                            error_messages.append(f"End date must be after or equal to start date for Period {i+1}")
                            break
                if not validation_passed:
                    st.session_state.submission_in_progress = False
                    error_html = "<div class='error-message'><div style='display: flex; align-items: center; justify-content: center;'><div style='font-size: 1.5rem; margin-right: 10px;'>&#x26A0;&#xFE0F;</div><div><strong>Validation Error</strong><br>"
                    for error in error_messages:
                        error_html += f"{error}<br>"
                    error_html += "</div></div></div>"
                    st.markdown(error_html, unsafe_allow_html=True)
                else:
                    with st.spinner('Submitting your application...'):
                        submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        superior_email = SUPERIORS[superior_name]
                        sheet = setup_google_sheets()
                        if sheet:
                            try:
                                cluster_codes = {}
                                for i in range(len(st.session_state.clusters)):
                                    code = generate_approval_password(sheet)
                                    cluster_codes[i] = code
                                    log_debug(f"Generated unique code for period {i+1}: {code}")
                                for i, cluster in enumerate(st.session_state.clusters):
                                    no_of_days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
                                    row_data = [
                                        submission_date, employee_code.strip(), employee_name.strip(),
                                        department.strip(), cluster['leave_type'].strip(),
                                        str(no_of_days) if no_of_days is not None else "",
                                        purpose.strip(), cluster['from_date'].strftime("%Y-%m-%d"),
                                        cluster['till_date'].strftime("%Y-%m-%d"), superior_name.strip(),
                                        superior_email.strip(), "Pending", "", cluster_codes[i],
                                        "Yes" if is_cluster else "No",
                                        str(i+1) if is_cluster else "", employee_email.strip()
                                    ]
                                    log_debug(f"Row data for period {i+1}: {row_data}")
                                    if len(row_data) != 17:
                                        log_debug(f"Warning: Row data has {len(row_data)} columns, expected 17")
                                        while len(row_data) < 17: row_data.append("")
                                        row_data = row_data[:17]
                                    for j, item in enumerate(row_data):
                                        if not isinstance(item, str):
                                            row_data[j] = str(item) if item is not None else ""
                                    write_success = add_data_to_sheet1(sheet, row_data)
                                    if write_success:
                                        log_debug(f"Data written for {employee_name} - Period {i+1} - Code: {cluster_codes[i]}")
                                    else:
                                        log_debug(f"Error writing to Google Sheets for period {i+1}")
                                        st.error(f"Error writing to Google Sheets for period {i+1}")
                                        raise Exception(f"Failed to write to Google Sheets for period {i+1}")

                                email_sent = False
                                email_error = ""
                                if email_config["configured"]:
                                    try:
                                        clusters_for_email = []
                                        for cluster in st.session_state.clusters:
                                            cluster_copy = cluster.copy()
                                            cluster_copy['employee_code'] = employee_code
                                            cluster_copy['department'] = department
                                            cluster_copy['purpose'] = purpose
                                            clusters_for_email.append(cluster_copy)
                                        email_sent = send_approval_email(
                                            employee_name, superior_name, superior_email,
                                            employee_email, clusters_for_email, cluster_codes
                                        )
                                        if not email_sent:
                                            email_error = "Email sending failed - check debug logs"
                                    except Exception as e:
                                        email_error = f"Email exception: {str(e)}"
                                        log_debug(f"Email exception: {traceback.format_exc()}")

                                st.session_state.last_submission_hash = generate_submission_hash(form_data_for_check)
                                st.session_state.submission_timestamp = datetime.now()
                                st.session_state.submission_in_progress = False
                                st.session_state.submission_completed = True

                                if email_sent:
                                    st.markdown("""
                                        <div class="success-message">
                                            <div style="font-size: 3rem; margin-bottom: 1rem;">&#x2728;</div>
                                            <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 10px; color: #166534;">
                                                Application Submitted Successfully!
                                            </div>
                                            <div style="color: #155724; margin-bottom: 15px;">
                                                Your leave request has been sent to your manager for approval.
                                            </div>
                                            <div style="font-size: 0.95rem; color: #0f5132; opacity: 0.9;">
                                                Confirmation email sent to your email address.
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    st.balloons()
                                    st.session_state.generated_codes.clear()
                                    st.session_state.reset_form_tab1 = True
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.session_state.cluster_codes = cluster_codes
                                    st.session_state.show_copy_section = True
                                    st.markdown(f"""
                                        <div class="info-box">
                                            <div style="display: flex; align-items: flex-start;">
                                                <div style="font-size: 1.5rem; margin-right: 15px; color: #ff9800;">&#x1F4E7;</div>
                                                <div>
                                                    <strong style="display: block; margin-bottom: 8px; color: #ff9800;">Email Notification Issue</strong>
                                                    Your application was saved to the database successfully!<br>
                                                    However, we could not send the email notification automatically.<br>
                                                    <small>{email_error}</small>
                                                </div>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    st.markdown("---")
                                    st.markdown(f"""
                                        <div style="text-align: center; margin: 2rem 0;">
                                            <div style="font-size: 1.3rem; font-weight: 600; color: #673ab7; margin-bottom: 1rem;">
                                                Manual Approval Process
                                            </div>
                                            <p style="color: #718096; margin-bottom: 1.5rem;">
                                                Please share these approval codes with your manager <strong>{superior_name}</strong>:
                                            </p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    for i, cluster in enumerate(st.session_state.clusters):
                                        code = cluster_codes[i]
                                        days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
                                        days_display = "N/A" if cluster['leave_type'] == "Early Exit" else (f"{days} days" if cluster['leave_type'] == "Full Day" else "0.5 day")
                                        st.markdown(f"""
                                            <div style="background: {'#f8f9ff' if i % 2 == 0 else '#f0f2ff'}; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border-left: 4px solid #4dabf7;">
                                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                                    <div>
                                                        <div style="font-size: 1.1rem; font-weight: 600; color: #339af0;">Period {i+1}</div>
                                                        <div style="font-size: 0.9rem; color: #718096;">
                                                            {cluster['from_date'].strftime('%Y-%m-%d')} to {cluster['till_date'].strftime('%Y-%m-%d')} &bull; {cluster['leave_type']} &bull; {days_display}
                                                        </div>
                                                    </div>
                                                    <div style="text-align: center;">
                                                        <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500; margin-bottom: 5px;">Approval Code</div>
                                                        <div style="font-size: 2rem; font-weight: 700; color: #553c9a; letter-spacing: 4px; font-family: 'Courier New', monospace;">
                                                            {code}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        """, unsafe_allow_html=True)
                                    st.markdown("""
                                        <div style="background: #e8f5e9; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0;">
                                            <strong style="color: #2e7d32; display: block; margin-bottom: 10px;">Instructions for your Manager:</strong>
                                            <ol style="color: #388e3c; margin-left: 20px;">
                                                <li>Visit the leave management app</li>
                                                <li>Click on the "Approval Portal" tab</li>
                                                <li>For each period: Enter the specific approval code</li>
                                                <li>Select Approve or Reject for that period</li>
                                                <li>Click Submit Decision</li>
                                                <li>Repeat for each period with its specific code</li>
                                            </ol>
                                            <p style="color: #2e7d32; font-size: 0.9rem; margin-top: 10px;">
                                                <strong>Note:</strong> Each code can only be used once for its specific period.
                                            </p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    st.balloons()
                                    st.session_state.generated_codes.clear()
                                    st.session_state.reset_form_tab1 = True
                                    time.sleep(2)
                                    st.rerun()

                            except Exception as e:
                                st.session_state.submission_in_progress = False
                                st.markdown(f"""
                                    <div class="error-message">
                                        <div style="display: flex; align-items: center; justify-content: center;">
                                            <div style="font-size: 1.5rem; margin-right: 10px;">&#x274C;</div>
                                            <div>
                                                <strong>Submission Error</strong><br>
                                                Please try again or contact HR<br>
                                                Error: {str(e)}
                                            </div>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                                log_debug(f"Submission error: {traceback.format_exc()}")
                        else:
                            st.session_state.submission_in_progress = False
                            st.markdown("""
                                <div class="error-message">
                                    <div style="display: flex; align-items: center; justify-content: center;">
                                        <div style="font-size: 1.5rem; margin-right: 10px;">&#x1F4CA;</div>
                                        <div>
                                            <strong>Database Connection Error</strong><br>
                                            Could not connect to database. Please try again later.
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

# ============================================
# TAB 2: APPROVAL PORTAL
# ============================================
with tab2:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">&#x2705;</div>
            <div>
                <h3 style="margin: 0;">Manager or Team Leader Approval Portal</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    Securely approve or reject leave requests using the approval code
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;
                    border: 1px solid rgba(33, 150, 243, 0.2);">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 1.5rem; margin-right: 15px; color: #2196f3;">&#x1F512;</div>
                <div>
                    <strong style="color: #0d47a1;">Secure Authentication Required</strong><br>
                    <span style="color: #1565c0; font-size: 0.95rem;">
                        Use the unique 5-character approval code sent via email for authentication
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.reset_form_tab2:
        st.session_state.form_data_tab2 = {'approval_password': '', 'action': 'Select Decision'}
        st.session_state.reset_form_tab2 = False
        st.session_state.submission_in_progress = False

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        approval_password_input = st.text_input(
            "Approval Code", value=st.session_state.form_data_tab2['approval_password'],
            type="password", placeholder="Enter 5-character code",
            help="Enter the unique code from the approval email", key="approval_code_input"
        )

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);">&#x1F4CB;</div>
                <div>
                    <h4 style="margin: 0;">Decision</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        Select your decision for this leave request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    action_options = ["Select Decision", "Approve", "Reject"]
    action = st.selectbox(
        "Select Action", action_options, index=0,
        label_visibility="collapsed", key="action_select"
    )

    submit_decision_disabled = st.session_state.get('submission_in_progress', False)
    if submit_decision_disabled:
        st.info("Processing your decision... Please wait.")
    submit_decision_button = st.button(
        "Submit Decision", type="primary", use_container_width=True,
        key="submit_decision_button", disabled=submit_decision_disabled
    )

    if submit_decision_button and not submit_decision_disabled:
        st.session_state.submission_in_progress = True
        if not all([approval_password_input, action != "Select Decision"]):
            st.session_state.submission_in_progress = False
            st.markdown("""
                <div class="error-message">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <div style="font-size: 1.5rem; margin-right: 10px;">&#x26A0;&#xFE0F;</div>
                        <div>
                            <strong>Missing Information</strong><br>
                            Please enter approval code and select a decision
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        elif len(approval_password_input) != 5:
            st.session_state.submission_in_progress = False
            st.markdown("""
                <div class="error-message">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <div style="font-size: 1.5rem; margin-right: 10px;">&#x1F511;</div>
                        <div>
                            <strong>Invalid Code Format</strong><br>
                            Please enter the exact 5-character code from the approval email
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Processing your decision..."):
                sheet = setup_google_sheets()
                if sheet:
                    status = "Approved" if action == "Approve" else "Rejected"
                    success = update_leave_status(sheet, approval_password_input, status)
                    if success:
                        st.session_state.submission_in_progress = False
                        status_color = "#155724" if status == "Approved" else "#721c24"
                        status_bg = "#d4edda" if status == "Approved" else "#f8d7da"
                        status_icon = "&#x2705;" if status == "Approved" else "&#x274C;"
                        st.markdown(f"""
                            <div style="background: {status_bg}; border-left: 4px solid {status_color};
                                      color: {status_color}; padding: 2rem; border-radius: 16px;
                                      margin: 2rem 0; text-align: center;">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">{status_icon}</div>
                                <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 10px;">
                                    Decision Submitted Successfully!
                                </div>
                                <div style="margin-bottom: 15px;">
                                    The leave request has been <strong>{status.lower()}</strong>.
                                </div>
                                <div style="font-size: 0.95rem; opacity: 0.9;">
                                    Status email sent to employee<br>
                                    Confirmation email sent to you
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        st.session_state.reset_form_tab2 = True
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.session_state.submission_in_progress = False
                        st.markdown("""
                            <div class="error-message">
                                <div style="display: flex; align-items: center; justify-content: center;">
                                    <div style="font-size: 1.5rem; margin-right: 10px;">&#x1F510;</div>
                                    <div>
                                        <strong>Authentication Failed</strong><br>
                                        Invalid code or code already used.<br>
                                        Please check your approval code or contact HR for assistance.
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.session_state.submission_in_progress = False
                    st.markdown("""
                        <div class="error-message">
                            <div style="display: flex; align-items: center; justify-content: center;">
                                <div style="font-size: 1.5rem; margin-right: 10px;">&#x1F4CA;</div>
                                <div>
                                    <strong>Database Connection Error</strong><br>
                                    Could not connect to database. Please try again later.
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# ============================================
# TAB 3: COMPANY HOLIDAYS
# ============================================
with tab3:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">&#x1F4C5;</div>
            <div>
                <h3 style="margin: 0;">Company Holidays 2026</h3>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0; padding: 1.5rem;
                    background: var(--card-bg); border-radius: 16px;
                    border: 1px solid var(--border-color); box-shadow: 0 4px 12px var(--shadow-color);">
            <div style="font-size: 3rem; font-weight: 700; background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {len(HOLIDAYS_2026)}
            </div>
            <div style="font-size: 1.2rem; font-weight: 600; color: var(--text-primary); margin-top: 0.5rem;">
                Official Holidays in 2026
            </div>
        </div>
    """, unsafe_allow_html=True)

    holidays_data = []
    for holiday in HOLIDAYS_2026:
        day_month = holiday["date"].split("-")
        date_str = f"{day_month[0]} {day_month[1]} 2026"
        holidays_data.append({
            "Date": date_str,
            "Day": holiday["day"],
            "Holiday": holiday["holiday"]
        })

    df = pd.DataFrame(holidays_data)

    def style_day(val):
        if val == "Saturday":
            return f'<span class="day-badge day-saturday">{val}</span>'
        elif val == "Sunday":
            return f'<span class="day-badge day-sunday">{val}</span>'
        else:
            return f'<span class="day-badge day-weekday">{val}</span>'

    df["Day"] = df["Day"].apply(style_day)
    html_table = df.to_html(escape=False, index=False)
    centered_table = f"""
    <div class="holidays-table-wrapper">
        {html_table}
    </div>
    """
    st.markdown(centered_table, unsafe_allow_html=True)

# ============================================
# TAB 4: WFH / OUT OF OFFICE
# ============================================
with tab4:
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #38d9a9 0%, #20c997 100%);">&#x1F3E0;</div>
            <div>
                <h3 style="margin: 0;">Work From Home / Out of Office Request</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    Submit requests for remote work or official out-of-office assignments
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;
                    border: 1px solid rgba(33, 150, 243, 0.2);">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 1.5rem; margin-right: 15px; color: #2196f3;">&#x2139;&#xFE0F;</div>
                <div>
                    <strong style="color: #0d47a1;">Information</strong><br>
                    <span style="color: #1565c0; font-size: 0.95rem;">
                        Use this form to request Work From Home or report official out-of-office work.
                        Please ensure you have necessary approvals before submitting.
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.reset_form_tab4:
        st.session_state.form_data_tab4 = {
            'employee_name': '', 'employee_code': '', 'request_type': 'Select Type',
            'start_date': datetime.now().date(), 'end_date': datetime.now().date(),
            'reason': '', 'approval_from': 'Select Approval'
        }
        st.session_state.reset_form_tab4 = False
        st.session_state.submission_in_progress = False

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        employee_name = st.text_input(
            "Employee Name", value=st.session_state.form_data_tab4['employee_name'],
            placeholder="Enter your full name", key="wfh_employee_name"
        )
    with col2:
        employee_code = st.text_input(
            "Employee Code", value=st.session_state.form_data_tab4['employee_code'],
            placeholder="e.g., VF-EMP-001", key="wfh_employee_code"
        )

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);">&#x1F4CB;</div>
                <div>
                    <h4 style="margin: 0;">Request Type</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        Select the type of request you are submitting
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    request_type = st.selectbox(
        "Select Request Type",
        ["Select Type", "Work From Home", "Out of Office for Official Work"],
        index=0, key="wfh_request_type"
    )

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);">&#x1F4C5;</div>
                <div>
                    <h4 style="margin: 0;">Date Range</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        Select the start and end dates for your request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns([1, 1], gap="large")
    with col3:
        start_date = st.date_input(
            "Start Date", value=st.session_state.form_data_tab4['start_date'],
            min_value=datetime.now().date(), key="wfh_start_date"
        )
    with col4:
        end_date = st.date_input(
            "End Date", value=st.session_state.form_data_tab4['end_date'],
            min_value=datetime.now().date(), key="wfh_end_date"
        )

    if start_date and end_date:
        if end_date < start_date:
            st.error("End date cannot be before start date")
        else:
            total_days = (end_date - start_date).days + 1
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);
                            color: white; padding: 1rem; border-radius: 12px; text-align: center; margin: 1rem 0;">
                    <div style="font-size: 0.9rem;">Total Duration</div>
                    <div style="font-size: 2rem; font-weight: bold;">{total_days}</div>
                    <div style="font-size: 0.8rem;">day(s)</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);">&#x1F4DD;</div>
                <div>
                    <h4 style="margin: 0;">Reason for Request</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        Provide detailed explanation for your request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    reason = st.text_area(
        "Reason / Purpose", value=st.session_state.form_data_tab4['reason'],
        placeholder="Please provide a clear and detailed explanation for your request...",
        height=150, key="wfh_reason"
    )

    st.markdown("---")
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div class="icon-badge" style="background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%);">&#x2705;</div>
                <div>
                    <h4 style="margin: 0;">Approval Received From</h4>
                    <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.9rem;">
                        Select who has approved this request
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    approval_from = st.selectbox(
        "Select Approval Authority", WFH_APPROVALS, index=0,
        help="Select the person who has approved this request", key="wfh_approval_from"
    )

    st.markdown("---")
    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        submit_button_disabled = st.session_state.get('submission_in_progress', False)
        if submit_button_disabled:
            st.info("Processing your submission... Please wait.")
        submit_button = st.button(
            "Submit Request", type="primary", use_container_width=True,
            key="submit_wfh_request", disabled=submit_button_disabled
        )

        if submit_button and not submit_button_disabled:
            st.session_state.submission_in_progress = True
            wfh_form_data = {
                'employee_name': employee_name, 'employee_code': employee_code,
                'request_type': request_type, 'start_date': start_date,
                'end_date': end_date, 'reason': reason
            }
            is_duplicate, duplicate_message = check_duplicate_wfh_submission(wfh_form_data)
            if is_duplicate:
                st.session_state.submission_in_progress = False
                st.markdown(f"""
                    <div class="error-message">
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <div style="font-size: 1.5rem; margin-right: 10px;">&#x26A0;&#xFE0F;</div>
                            <div>
                                <strong>Duplicate Submission Detected</strong><br>
                                {duplicate_message}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                validation_passed = True
                error_messages = []
                if not all([employee_name, employee_code, request_type != "Select Type",
                            reason, approval_from != "Select Approval"]):
                    validation_passed = False
                    error_messages.append("Please complete all required fields")
                if end_date < start_date:
                    validation_passed = False
                    error_messages.append("End date cannot be before start date")
                if not validation_passed:
                    st.session_state.submission_in_progress = False
                    error_html = "<div class='error-message'><div style='display: flex; align-items: center; justify-content: center;'><div style='font-size: 1.5rem; margin-right: 10px;'>&#x26A0;&#xFE0F;</div><div><strong>Validation Error</strong><br>"
                    for error in error_messages:
                        error_html += f"{error}<br>"
                    error_html += "</div></div></div>"
                    st.markdown(error_html, unsafe_allow_html=True)
                else:
                    with st.spinner('Submitting your request...'):
                        success, message = submit_wfh_request(
                            employee_name, employee_code, request_type,
                            start_date, end_date, reason, approval_from
                        )
                        if success:
                            st.session_state.last_wfh_submission_hash = generate_wfh_hash(wfh_form_data)
                            st.session_state.wfh_submission_timestamp = datetime.now()
                            st.session_state.submission_in_progress = False
                            duration = (end_date - start_date).days + 1
                            st.markdown(f"""
                                <div class="success-message">
                                    <div style="font-size: 3rem; margin-bottom: 1rem;">&#x2728;</div>
                                    <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 10px; color: #166534;">
                                        Request Submitted Successfully!
                                    </div>
                                    <div style="color: #155724; margin-bottom: 15px;">
                                        Your {request_type.lower()} request has been submitted successfully.
                                    </div>
                                    <div style="font-size: 0.95rem; color: #0f5132; opacity: 0.9;">
                                        Request Type: {request_type}<br>
                                        Duration: {duration} day(s)<br>
                                        Approval From: {approval_from}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                            st.session_state.reset_form_tab4 = True
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.session_state.submission_in_progress = False
                            st.markdown(f"""
                                <div class="error-message">
                                    <div style="display: flex; align-items: center; justify-content: center;">
                                        <div style="font-size: 1.5rem; margin-right: 10px;">&#x274C;</div>
                                        <div>
                                            <strong>Submission Error</strong><br>
                                            {message}<br>
                                            Please try again or contact HR for assistance.
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        <div style="margin-bottom: 1rem;">
            <strong style="color: #673ab7;">VOLAR FASHION PVT LTD</strong><br>
            Human Resources Management System
        </div>
        <div style="font-size: 0.9rem;">
            hrvolarfashion@gmail.com<br>
            &copy; 2026 VOLAR FASHION.
        </div>
    </div>
""", unsafe_allow_html=True)
