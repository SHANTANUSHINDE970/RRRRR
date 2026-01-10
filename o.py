import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import pandas as pd
import time
import secrets
import string
import os
import traceback
import ssl
from email.utils import formataddr
import socket
import uuid
from functools import lru_cache

# Page configuration
st.set_page_config(
    page_title="VOLAR FASHION - Leave Management",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# OPTIMIZED CSS (All design preserved but optimized for performance)
# ============================================
st.markdown("""
<style>
    /* Critical CSS loaded first */
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
    
    .main, .stApp {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        min-height: 100vh;
    }
    
    h1 {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3.2rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    /* Form styling */
    .form-container {
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 24px;
        box-shadow: 0 20px 60px var(--shadow-color);
        margin: 2rem auto;
        max-width: 1000px;
        border: 1px solid rgba(103, 58, 183, 0.1);
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
        transition: all 0.3s;
        box-shadow: 0 8px 25px rgba(103, 58, 183, 0.25);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(103, 58, 183, 0.35);
    }
    
    /* Input styling */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea,
    .stDateInput>div>div>input {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Deferred CSS (loaded after critical content) */
    .form-container:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
    }
    
    .success-message, .error-message, .info-box {
        padding: 1.75rem;
        border-radius: 16px;
        margin: 2rem 0;
        text-align: center;
    }
    
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid var(--success-color);
        color: #155724;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid var(--danger-color);
        color: #721c24;
    }
    
    .warning-message {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 4px solid var(--warning-color);
        color: #856404;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid var(--accent-color);
        color: #0d47a1;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(156, 39, 176, 0.1);
    }
    
    /* Early exit message without thumbs-up animation */
    .early-exit-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 4px solid #4caf50;
        color: #2e7d32;
        padding: 1.75rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(76, 175, 80, 0.1);
        text-align: center;
    }
    
    /* Simple animations (CPU efficient) */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideInUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    .animate-slide-in {
        animation: slideInUp 0.5s ease-out;
    }
    
    /* Optimized floating animation */
    .floating-element {
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); } /* Reduced movement for less GPU usage */
    }
    
    /* Holidays table optimized */
    .holidays-table-wrapper table {
        border-collapse: collapse;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
        background: var(--card-bg);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        h1 { font-size: 2rem; }
        .form-container { padding: 1.5rem; }
        .stButton>button { padding: 0.75rem 2rem; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CACHED DATA LOADING (Reduces recomputation)
# ============================================

@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour, no spinner
def load_static_data():
    """Load static data that rarely changes"""
    SUPERIORS = {
        "Shantanu Shinde": "s37@vfemails.com",
        "Ayushi Jain": "ayushi@volarfashion.in",
        "Akshaya Shinde": "Akshaya@vfemails.com",
        "Vitika Mehta": "vitika@vfemails.com",
        "Manish Gupta": "Manish@vfemails.com",
        "Tahir Siddiqui": "tahir@vfemails.com",
        "Tariq Patel": "dn1@volarfashion.in",
        "HR": "hrvolarfashion@gmail.com",
        "Rajeev Thakur": "Rajeev@vfemails.com",
        "Krishna Yadav": "Krishna@vfemails.com",
        "Sarath Kumar": "Sarath@vfemails.com"
    }
    
    DEPARTMENTS = [
        "Accounts and Finance", "Administration", "Business Development",
        "Content", "E-Commerce", "Factory & Production", "Graphics",
        "Human Resources", "IT", "Social Media", "Bandra Store",
        "Support Staff", "Warehouse", "SEO"
    ]
    
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
    
    return SUPERIORS, DEPARTMENTS, HOLIDAYS_2026

SUPERIORS, DEPARTMENTS, HOLIDAYS_2026 = load_static_data()

# ============================================
# DATE VALIDATION FUNCTIONS
# ============================================

def validate_leave_dates(leave_type, from_date, till_date, cluster_index=1):
    """Validate leave dates with restrictions"""
    warnings = []
    errors = []
    
    # Check if from_date is after till_date
    if from_date > till_date:
        errors.append(f"Period {cluster_index}: Start date cannot be after end date")
    
    # Check for Sunday restrictions
    if leave_type in ["Half Day", "Early Exit"]:
        # Check if date is Sunday
        if from_date.weekday() == 6:  # Sunday
            errors.append(f"Period {cluster_index}: {leave_type} cannot be taken on Sunday. Please change your date.")
        
        # Check if date is Saturday for Half Day
        if leave_type == "Half Day" and from_date.weekday() == 5:  # Saturday
            errors.append(f"Period {cluster_index}: Half Day cannot be taken on Saturday (Saturday is already half day). Please change your date.")
    
    # Check if trying to take leave on company holiday
    for holiday in HOLIDAYS_2026:
        holiday_date_str = f"{holiday['date']}-2026"
        try:
            holiday_date = datetime.strptime(holiday_date_str, "%d-%b-%Y").date()
            if from_date <= holiday_date <= till_date:
                warnings.append(f"Period {cluster_index}: Your leave period includes company holiday ({holiday['holiday']} on {holiday['date']})")
        except:
            pass
    
    return errors, warnings

# ============================================
# OPTIMIZED SESSION STATE (Minimal updates)
# ============================================

# Initialize session state only once
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.clusters = [{
        'cluster_number': 1,
        'leave_type': 'Select Type',
        'from_date': datetime.now().date(),
        'till_date': datetime.now().date(),
    }]
    st.session_state.form_data = {
        'employee_name': '',
        'employee_code': '',
        'department': 'Select Department',
        'purpose': '',
        'superior_name': 'Select Manager',
        'is_cluster': False
    }
    st.session_state.generated_codes = set()
    st.session_state.debug_logs = []
    st.session_state.cached_sheet_data = None
    st.session_state.last_sheet_fetch = 0
    st.session_state.used_codes = set()  # Track used approval codes

# ============================================
# OPTIMIZED FUNCTIONS WITH CACHING
# ============================================

def add_debug_log(message, level="INFO"):
    """Lightweight debug logging"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    st.session_state.debug_logs.append(log_entry)
    # Keep only last 10 logs
    if len(st.session_state.debug_logs) > 10:
        st.session_state.debug_logs.pop(0)

@st.cache_resource(ttl=300, show_spinner=False)  # Cache for 5 minutes
def get_google_sheets_connection():
    """Cached Google Sheets connection"""
    try:
        # Minimal scope
        SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets']
        
        # Get credentials from secrets
        if 'google_credentials' in st.secrets:
            secrets_key = "google_credentials"
        elif 'GOOGLE_CREDENTIALS' in st.secrets:
            secrets_key = "GOOGLE_CREDENTIALS"
        else:
            return None
        
        creds_dict = {
            "type": st.secrets[secrets_key]["type"],
            "project_id": st.secrets[secrets_key]["project_id"],
            "private_key_id": st.secrets[secrets_key]["private_key_id"],
            "private_key": st.secrets[secrets_key]["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets[secrets_key]["client_email"],
            "client_id": st.secrets[secrets_key]["client_id"],
            "auth_uri": st.secrets[secrets_key]["auth_uri"],
            "token_uri": st.secrets[secrets_key]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets[secrets_key]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets[secrets_key]["client_x509_cert_url"]
        }
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open("Leave_Applications")
        return spreadsheet.sheet1
        
    except Exception as e:
        add_debug_log(f"Google Sheets error: {str(e)}")
        return None

def get_cached_sheet_data(force_refresh=False):
    """Get cached sheet data with smart refreshing"""
    current_time = time.time()
    
    # Refresh if forced or cache is older than 2 minutes
    if (force_refresh or st.session_state.cached_sheet_data is None or 
        current_time - st.session_state.last_sheet_fetch > 120):
        
        sheet = get_google_sheets_connection()
        if sheet:
            try:
                # Fetch all records
                st.session_state.cached_sheet_data = sheet.get_all_records()
                st.session_state.last_sheet_fetch = current_time
                
                # Update used codes from sheet
                if st.session_state.cached_sheet_data:
                    for row in st.session_state.cached_sheet_data:
                        if 'Approval Password' in row and row['Approval Password']:
                            st.session_state.used_codes.add(row['Approval Password'])
                
            except Exception as e:
                add_debug_log(f"Error fetching sheet data: {str(e)}")
                st.session_state.cached_sheet_data = []
    
    return st.session_state.cached_sheet_data

def get_existing_codes():
    """Get all existing codes (used + unused)"""
    sheet_data = get_cached_sheet_data()
    existing_codes = set()
    
    if sheet_data:
        for row in sheet_data:
            if 'Approval Password' in row and row['Approval Password']:
                existing_codes.add(row['Approval Password'])
    
    return existing_codes

def get_used_codes():
    """Get only used codes"""
    sheet_data = get_cached_sheet_data()
    used_codes = set()
    
    if sheet_data:
        for row in sheet_data:
            if 'Approval Password' in row and row['Approval Password']:
                # Check if code is marked as used or if status is not pending
                if ('Status' in row and row['Status'] in ['Approved', 'Rejected', 'USED']) or \
                   ('Approval Date' in row and row['Approval Date']):
                    used_codes.add(row['Approval Password'])
    
    return used_codes

def generate_approval_password():
    """Generate unique 5-digit code that hasn't been used"""
    alphabet = string.ascii_uppercase.replace('O', '').replace('I', '').replace('L', '') + '23456789'
    
    # Get all existing codes and used codes
    existing_codes = get_existing_codes()
    used_codes = get_used_codes()
    
    # Combine all codes that should not be reused
    forbidden_codes = existing_codes.union(used_codes).union(st.session_state.generated_codes)
    
    # Try 10 attempts max
    for attempt in range(10):
        password = ''.join(secrets.choice(alphabet) for _ in range(5))
        if password not in forbidden_codes:
            st.session_state.generated_codes.add(password)
            add_debug_log(f"Generated new code: {password}")
            return password
    
    # Fallback with timestamp and random suffix
    timestamp = int(time.time() * 100) % 10000
    random_suffix = secrets.choice(alphabet)
    password = f"{timestamp:04d}{random_suffix}"[:5]
    
    # Ensure it's unique
    if password not in forbidden_codes:
        st.session_state.generated_codes.add(password)
        add_debug_log(f"Generated fallback code: {password}")
        return password
    
    # Last resort - UUID based
    final_code = str(uuid.uuid4().int)[:5].upper()
    final_code = ''.join([c for c in final_code if c in alphabet])
    while len(final_code) < 5:
        final_code = final_code + secrets.choice(alphabet)
    
    st.session_state.generated_codes.add(final_code)
    add_debug_log(f"Generated UUID-based code: {final_code}")
    return final_code

@lru_cache(maxsize=1)
def check_email_configuration():
    """Cached email configuration check"""
    try:
        sender_email = None
        sender_password = None
        
        # Check secrets
        for section in ['EMAIL', 'email']:
            if section in st.secrets:
                sender_email = st.secrets[section].get("sender_email")
                sender_password = st.secrets[section].get("sender_password")
                if sender_email and sender_password:
                    return {
                        "configured": True,
                        "sender_email": sender_email,
                        "sender_password": sender_password
                    }
        
        return {"configured": False}
        
    except Exception as e:
        add_debug_log(f"Email config error: {str(e)}")
        return {"configured": False}

def calculate_working_days(from_date, till_date):
    """Calculate total days INCLUDING Sundays"""
    if from_date > till_date:
        return 0
    
    # Simple difference + 1 to include both start and end dates
    total_days = (till_date - from_date).days + 1
    return total_days

def calculate_days(from_date, till_date, leave_type):
    """Simple days calculation"""
    if leave_type == "Half Day":
        return 0.5
    elif leave_type == "Early Exit":
        return ""
    else:
        # For Full Day, include all days
        return calculate_working_days(from_date, till_date)

def send_email_simple(sender_email, sender_password, recipient, subject, body):
    """Simplified email sending"""
    try:
        msg = MIMEMultipart()
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=5, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        add_debug_log(f"Email error: {str(e)}")
        return False

# ============================================
# OPTIMIZED UI COMPONENTS (Preserves design)
# ============================================

def render_header():
    """Render header with minimal DOM updates"""
    st.markdown("""
        <div class="company-header floating-element">
            <h1>VOLAR FASHION</h1>
            <h2>Leave Management System</h2>
        </div>
    """, unsafe_allow_html=True)

def render_holidays_tab():
    """Render holidays tab efficiently"""
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge">📅</div>
            <div>
                <h3 style="margin: 0;">Company Holidays 2026</h3>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Use cached data
    holidays_data = []
    for holiday in HOLIDAYS_2026:
        day_month = holiday["date"].split("-")
        date_str = f"{day_month[0]} {day_month[1]} 2026"
        holidays_data.append({
            "Date": date_str,
            "Day": holiday["day"],
            "Holiday": holiday["holiday"]
        })
    
    # Render table
    st.markdown(f"""
        <div class="metric-card floating-element">
            <div style="font-size: 3rem; font-weight: 700;">{len(HOLIDAYS_2026)}</div>
            <div style="font-size: 1.2rem;">Official Holidays</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Simple table display
    df = pd.DataFrame(holidays_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================
# MAIN APPLICATION
# ============================================

# Render header
render_header()

# Create tabs
tab1, tab2, tab3 = st.tabs(["📝 Submit Leave", "✅ Approval Portal", "📅 Company Holidays"])

with tab1:
    # Email status check (cached)
    email_config = check_email_configuration()
    
    # Form container
    st.markdown("""
        <div class="form-container animate-slide-in">
            <div class="section-header">
                <div class="icon-badge">📋</div>
                <div>
                    <h3 style="margin: 0;">Leave Application Form</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Simple form layout
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        employee_name = st.text_input("👤 Full Name", 
            placeholder="Enter your full name",
            key="employee_name")
        employee_code = st.text_input("🔢 Employee ID",
            placeholder="e.g., VF-EMP-001",
            key="employee_code")
    
    with col2:
        department = st.selectbox("🏛️ Department", 
            ["Select Department"] + DEPARTMENTS,
            key="department")
        is_cluster = st.checkbox("Is this a Cluster Holiday?", 
            key="is_cluster")
    
    # Date validation warnings
    date_warnings = []
    
    # Cluster handling
    if is_cluster:
        st.markdown("---")
        st.markdown("#### 📅 Cluster Holiday Periods")
        
        # Manage clusters
        for i in range(len(st.session_state.clusters)):
            cols = st.columns([2, 2, 1, 1], gap="medium")
            with cols[0]:
                st.session_state.clusters[i]['leave_type'] = st.selectbox(
                    f"Leave Type {i+1}",
                    ["Select Type", "Full Day", "Half Day", "Early Exit"],
                    key=f"cluster_type_{i}"
                )
            with cols[1]:
                if st.session_state.clusters[i]['leave_type'] in ["Half Day", "Early Exit"]:
                    date_val = st.date_input(f"Date {i+1}", 
                        value=st.session_state.clusters[i]['from_date'],
                        key=f"cluster_date_{i}")
                    st.session_state.clusters[i]['from_date'] = date_val
                    st.session_state.clusters[i]['till_date'] = date_val
                else:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.session_state.clusters[i]['from_date'] = st.date_input(
                            f"From {i+1}",
                            value=st.session_state.clusters[i]['from_date'],
                            key=f"cluster_from_{i}")
                    with col_b:
                        st.session_state.clusters[i]['till_date'] = st.date_input(
                            f"To {i+1}",
                            value=st.session_state.clusters[i]['till_date'],
                            key=f"cluster_to_{i}")
            
            # Validate dates
            if st.session_state.clusters[i]['leave_type'] != "Select Type":
                errors, warnings = validate_leave_dates(
                    st.session_state.clusters[i]['leave_type'],
                    st.session_state.clusters[i]['from_date'],
                    st.session_state.clusters[i]['till_date'],
                    i+1
                )
                
                if errors:
                    for error in errors:
                        st.error(error)
                if warnings:
                    date_warnings.extend(warnings)
            
            # Remove button
            with cols[3]:
                if i > 0 and st.button("❌", key=f"remove_{i}"):
                    st.session_state.clusters.pop(i)
                    st.rerun()
        
        # Add new cluster button
        if st.button("➕ Add Period", key="add_cluster"):
            st.session_state.clusters.append({
                'cluster_number': len(st.session_state.clusters) + 1,
                'leave_type': 'Select Type',
                'from_date': datetime.now().date(),
                'till_date': datetime.now().date(),
            })
            st.rerun()
    
    else:
        # Single holiday
        cols = st.columns(2, gap="large")
        with cols[0]:
            leave_type = st.selectbox("📋 Leave Type",
                ["Select Type", "Full Day", "Half Day", "Early Exit"],
                key="single_type")
        
        with cols[1]:
            if leave_type in ["Half Day", "Early Exit"]:
                date_val = st.date_input("📅 Date", 
                    value=st.session_state.clusters[0]['from_date'],
                    key="single_date")
                from_date = till_date = date_val
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    from_date = st.date_input("📅 From",
                        value=st.session_state.clusters[0]['from_date'],
                        key="single_from")
                with col_b:
                    till_date = st.date_input("📅 To",
                        value=st.session_state.clusters[0]['till_date'],
                        key="single_to")
        
        # Update session state
        st.session_state.clusters[0]['leave_type'] = leave_type
        st.session_state.clusters[0]['from_date'] = from_date
        st.session_state.clusters[0]['till_date'] = till_date
        
        # Validate dates
        if leave_type != "Select Type":
            errors, warnings = validate_leave_dates(
                leave_type, from_date, till_date, 1
            )
            
            if errors:
                for error in errors:
                    st.error(error)
            if warnings:
                date_warnings.extend(warnings)
        
        # Display days (with early exit message)
        if leave_type != "Select Type" and not errors:
            days = calculate_days(from_date, till_date, leave_type)
            
            if leave_type == "Early Exit":
                st.markdown("""
                    <div class="early-exit-box">
                        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">Early Exit Request</div>
                        <div style="font-size: 0.95rem;">
                            You're requesting to leave early from work today. Only 2 Early Leaves are Permitted per month.
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            elif leave_type == "Half Day":
                st.markdown(f"""
                    <div class="metric-card floating-element">
                        <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a;">
                            0.5
                        </div>
                        <div style="font-size: 0.9rem; color: #805ad5;">
                            half day
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="metric-card floating-element">
                        <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a;">
                            {days}
                        </div>
                        <div style="font-size: 0.9rem; color: #805ad5;">
                            total days
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    # Show date warnings if any
    if date_warnings:
        for warning in date_warnings:
            st.markdown(f'<div class="warning-message">{warning}</div>', unsafe_allow_html=True)
    
    # Purpose and manager selection
    purpose = st.text_area("📝 Purpose of Leave",
        placeholder="Please provide detailed explanation...",
        height=100,
        key="purpose")
    
    superior_name = st.selectbox("👔 Reporting Manager",
        ["Select Manager"] + list(SUPERIORS.keys()),
        key="superior")
    
    # Submit button
    st.markdown("</div>", unsafe_allow_html=True)  # Close form container
    
    if st.button("🚀 Submit Leave Request", type="primary", use_container_width=True):
        # Validation
        errors = []
        if not employee_name:
            errors.append("Full Name is required")
        if not employee_code:
            errors.append("Employee ID is required")
        if department == "Select Department":
            errors.append("Please select a department")
        if not purpose:
            errors.append("Purpose is required")
        if superior_name == "Select Manager":
            errors.append("Please select a manager")
        
        # Check for date validation errors
        date_errors = []
        for i, cluster in enumerate(st.session_state.clusters):
            if cluster['leave_type'] == "Select Type":
                errors.append(f"Please select leave type for Period {i+1}")
            else:
                # Validate dates again on submission
                cluster_errors, _ = validate_leave_dates(
                    cluster['leave_type'],
                    cluster['from_date'],
                    cluster['till_date'],
                    i+1
                )
                date_errors.extend(cluster_errors)
        
        if date_errors:
            errors.extend(date_errors)
        
        if errors:
            error_html = "<div class='error-message'><strong>Please fix the following errors:</strong><br>"
            for error in errors:
                error_html += f"• {error}<br>"
            error_html += "</div>"
            st.markdown(error_html, unsafe_allow_html=True)
        else:
            with st.spinner("Submitting your application..."):
                sheet = get_google_sheets_connection()
                if sheet:
                    try:
                        # Generate unique codes
                        cluster_codes = {}
                        for i in range(len(st.session_state.clusters)):
                            code = generate_approval_password()
                            # Double-check code hasn't been used
                            used_codes = get_used_codes()
                            if code in used_codes:
                                # Regenerate if somehow duplicate
                                code = generate_approval_password()
                            cluster_codes[i] = code
                        
                        # Submit each cluster
                        superior_email = SUPERIORS[superior_name]
                        submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        for i, cluster in enumerate(st.session_state.clusters):
                            days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
                            
                            row_data = [
                                submission_date,
                                employee_name,
                                employee_code,
                                department,
                                cluster['leave_type'],
                                str(days),
                                purpose,
                                cluster['from_date'].strftime("%Y-%m-%d"),
                                cluster['till_date'].strftime("%Y-%m-%d"),
                                superior_name,
                                superior_email,
                                "Pending",  # Status
                                "",  # Approval Date
                                cluster_codes[i],  # Approval Password
                                "Yes" if is_cluster else "No",  # Is Cluster Holiday
                                str(i+1) if is_cluster else ""  # Cluster Number
                            ]
                            
                            # Append row
                            sheet.append_row(row_data)
                            add_debug_log(f"Added leave request with code: {cluster_codes[i]}")
                        
                        # Try to send email
                        email_sent = False
                        if email_config["configured"]:
                            subject = f"Leave Approval: {employee_name}"
                            body = f"""
                            Leave request from {employee_name} ({employee_code})
                            
                            Approval Codes:
                            """
                            for i, code in cluster_codes.items():
                                cluster = st.session_state.clusters[i]
                                body += f"\nPeriod {i+1}: {code}"
                                body += f" ({cluster['leave_type']}: {cluster['from_date']} to {cluster['till_date']})"
                            
                            body += "\n\nNote: Each code can only be used once."
                            
                            email_sent = send_email_simple(
                                email_config["sender_email"],
                                email_config["sender_password"],
                                superior_email,
                                subject,
                                body
                            )
                        
                        # Success message
                        st.markdown("""
                            <div class="success-message animate-fade-in">
                                <div style="font-size: 3rem; margin-bottom: 1rem;">✨</div>
                                <div style="font-size: 1.5rem; font-weight: 600;">
                                    Application Submitted Successfully!
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Show manual codes if email failed
                        if not email_sent and email_config["configured"]:
                            st.info("**Manual Approval Codes (save these):**")
                            for i, code in cluster_codes.items():
                                st.code(f"Period {i+1}: {code}")
                        
                        # Clear session state
                        st.session_state.clusters = [{
                            'cluster_number': 1,
                            'leave_type': 'Select Type',
                            'from_date': datetime.now().date(),
                            'till_date': datetime.now().date(),
                        }]
                        
                        # Clear form fields
                        st.session_state.form_data = {
                            'employee_name': '',
                            'employee_code': '',
                            'department': 'Select Department',
                            'purpose': '',
                            'superior_name': 'Select Manager',
                            'is_cluster': False
                        }
                        
                        st.balloons()
                        
                    except Exception as e:
                        st.markdown(f"""
                            <div class="error-message">
                                <strong>Submission Error</strong><br>
                                {str(e)}
                            </div>
                        """, unsafe_allow_html=True)
                        add_debug_log(f"Submission error: {str(e)}")
                else:
                    st.error("Could not connect to database")

with tab2:
    st.markdown("""
        <div class="form-container animate-slide-in">
            <div class="section-header">
                <div class="icon-badge">✅</div>
                <div>
                    <h3 style="margin: 0;">Approval Portal</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    approval_code = st.text_input("🔑 Approval Code", 
        type="password",
        placeholder="Enter 5-character code",
        key="approval_code")
    
    action = st.selectbox("Decision",
        ["Select Decision", "✅ Approve", "❌ Reject"],
        key="decision")
    
    if st.button("Submit Decision", type="primary", use_container_width=True):
        if not approval_code or action == "Select Decision":
            st.error("Please enter code and select decision")
        elif len(approval_code) != 5:
            st.error("Code must be 5 characters")
        else:
            with st.spinner("Processing..."):
                sheet = get_google_sheets_connection()
                if sheet:
                    # Get fresh data to check for used codes
                    sheet_data = get_cached_sheet_data(force_refresh=True)
                    
                    # Check if code has already been used
                    code_already_used = False
                    record_found = False
                    record_row = None
                    record_idx = None
                    
                    for idx, row in enumerate(sheet_data):
                        if 'Approval Password' in row and row['Approval Password'] == approval_code:
                            record_found = True
                            record_row = row
                            record_idx = idx
                            # Check if already approved/rejected
                            if 'Status' in row and row['Status'] in ['Approved', 'Rejected', 'USED']:
                                code_already_used = True
                            if 'Approval Date' in row and row['Approval Date']:
                                code_already_used = True
                            break
                    
                    if not record_found:
                        st.error("Invalid approval code")
                    elif code_already_used:
                        st.error("This approval code has already been used")
                    else:
                        try:
                            status = "Approved" if "Approve" in action else "Rejected"
                            approval_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            # Update the specific cells
                            # Status is column 12, Approval Date is column 13, Approval Password mark as USED is column 14
                            sheet.update_cell(record_idx + 2, 12, status)
                            sheet.update_cell(record_idx + 2, 13, approval_date)
                            sheet.update_cell(record_idx + 2, 14, "USED")
                            
                            # Add to used codes in session state
                            st.session_state.used_codes.add(approval_code)
                            
                            # Clear cache to refresh data
                            st.session_state.cached_sheet_data = None
                            
                            st.success(f"Leave request {action.lower()}d successfully!")
                            add_debug_log(f"Code {approval_code} marked as used - Status: {status}")
                            
                        except Exception as e:
                            st.error(f"Error updating record: {str(e)}")
                            add_debug_log(f"Update error for code {approval_code}: {str(e)}")
                else:
                    st.error("Database connection failed")
    
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    render_holidays_tab()

# ============================================
# OPTIMIZED SIDEBAR (Minimal)
# ============================================

with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Email status
    email_config = check_email_configuration()
    if email_config["configured"]:
        st.success("✅ Email configured")
    else:
        st.warning("⚠️ Email not configured")
    
    # Used codes count
    used_codes_count = len(get_used_codes())
    st.metric("Used Approval Codes", used_codes_count)
    
    # Test connections
    if st.button("Test Connections", use_container_width=True):
        with st.spinner("Testing..."):
            # Test Google Sheets
            sheet = get_google_sheets_connection()
            if sheet:
                try:
                    row_count = len(sheet.get_all_records())
                    st.success(f"✅ Google Sheets: Connected ({row_count} records)")
                except:
                    st.success("✅ Google Sheets: Connected")
            else:
                st.error("❌ Google Sheets: Failed")
            
            # Test email
            if email_config["configured"]:
                st.success("✅ Email: Configured")
            else:
                st.warning("⚠️ Email: Not configured")
    
    # Debug logs
    if st.checkbox("Show Logs", False):
        if st.session_state.debug_logs:
            for log in st.session_state.debug_logs[-5:]:
                st.text(log)
        else:
            st.info("No logs yet")

# Footer
st.markdown("""
    <div class="footer">
        <strong>VOLAR FASHION PVT LTD</strong><br>
        Human Resources Management System<br>
        📧 hrvolarfashion@gmail.com
    </div>
""", unsafe_allow_html=True)
