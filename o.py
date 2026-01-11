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
from functools import lru_cache

# Page configuration
st.set_page_config(
    page_title="VOLAR FASHION - Leave Management",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# COMPRESSED CSS - Reduced by 30% while keeping all animations
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root {
    --primary-color: #673ab7; --secondary-color: #9c27b0; --accent-color: #2196f3;
    --success-color: #28a745; --warning-color: #ff9800; --danger-color: #dc3545;
    --text-primary: #1a1a1a; --text-secondary: #4a5568; --text-light: #718096;
    --bg-primary: #ffffff; --bg-secondary: #f8f9ff; --bg-tertiary: #f5f7fa;
    --border-color: #e2e8f0; --card-bg: #ffffff; --input-bg: #fafbfc;
    --shadow-color: rgba(103, 58, 183, 0.08);
}
@media (prefers-color-scheme: dark) {
    :root {
        --primary-color: #9c6bff; --secondary-color: #d179ff; --accent-color: #64b5f6;
        --success-color: #4caf50; --warning-color: #ffb74d; --danger-color: #f44336;
        --text-primary: #ffffff; --text-secondary: #cbd5e0; --text-light: #a0aec0;
        --bg-primary: #1a202c; --bg-secondary: #2d3748; --bg-tertiary: #4a5568;
        --border-color: #4a5568; --card-bg: #2d3748; --input-bg: #4a5568;
        --shadow-color: rgba(0, 0, 0, 0.3);
    }
    .stApp { background-color: var(--bg-primary) !important; }
    .main { background-color: var(--bg-primary) !important; }
    .stTextInput input, .stSelectbox select, .stTextArea textarea,
    .stDateInput input, .stNumberInput input {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border-color: var(--border-color) !important;
    }
}
* { font-family: 'Inter', sans-serif; color: var(--text-primary); }
.main, .stApp { background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%); }
.form-container {
    background: var(--card-bg); padding: 2.5rem; border-radius: 24px;
    box-shadow: 0 20px 60px var(--shadow-color); margin: 2rem auto;
    max-width: 1000px; border: 1px solid rgba(103, 58, 183, 0.1);
    position: relative; overflow: hidden;
}
.form-container:before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
}
h1 {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; font-size: 2.8rem; margin-bottom: 0.5rem; font-weight: 700;
}
h2 { color: var(--text-light); text-align: center; font-size: 1.4rem; margin-bottom: 2rem; }
.stButton>button {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    color: white; border: none; padding: 0.875rem 2.5rem; font-size: 1rem;
    border-radius: 12px; width: 100%; transition: all 0.3s;
    box-shadow: 0 8px 25px rgba(103, 58, 183, 0.25);
}
.stButton>button:hover { transform: translateY(-2px); box-shadow: 0 12px 35px rgba(103, 58, 183, 0.35); }
.stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea,
.stDateInput>div>div>input {
    color: var(--text-primary) !important; background-color: var(--input-bg) !important;
    border: 2px solid var(--border-color) !important; border-radius: 12px;
    padding: 0.75rem 1rem !important; font-size: 0.95rem; transition: all 0.3s;
}
.stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus,
.stTextArea>div>div>textarea:focus, .stDateInput>div>div>input:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 4px rgba(103, 58, 183, 0.1) !important;
}
.success-message, .error-message, .info-box, .thumbsup-box, .metric-card, .approval-card {
    padding: 1.5rem; border-radius: 16px; margin: 1.5rem 0; text-align: center;
    animation: slideIn 0.5s ease-out;
}
.success-message { background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border-left: 4px solid var(--success-color); }
.error-message { background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); border-left: 4px solid var(--danger-color); }
.info-box { background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-left: 4px solid var(--accent-color); }
.thumbsup-box { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-left: 4px solid #4caf50; }
.metric-card { background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); }
.approval-card { background: var(--card-bg); border: 1px solid var(--border-color); }
@keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes shake { 0%,100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
.company-header { text-align: center; margin-bottom: 2rem; padding: 1.5rem;
    background: var(--card-bg); border-radius: 24px; box-shadow: 0 15px 40px rgba(103, 58, 183, 0.08);
    border: 1px solid rgba(103, 58, 183, 0.1); position: relative; overflow: hidden;
}
.company-header:before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
}
.icon-badge { display: inline-flex; align-items: center; justify-content: center;
    width: 40px; height: 40px; border-radius: 12px;
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    color: white; margin-right: 12px; font-size: 1.2rem;
}
.cluster-section { background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
    border-radius: 16px; padding: 1.25rem; margin: 1.25rem 0;
    border: 2px solid #3b82f6; box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
}
.holidays-table-container { background: var(--card-bg); border-radius: 24px; padding: 2rem;
    box-shadow: 0 20px 60px var(--shadow-color); border: 1px solid rgba(103, 58, 183, 0.1);
    margin: 2rem auto; max-width: 1000px;
}
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# CACHED DATA - Reduce repeated computations
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_superiors():
    return {
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
        "Sarath Kumar": "Sarath@vfemails.com",
        "d":"shinde78617@gmail.com"
    }

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_departments():
    return [
        "Accounts and Finance", "Administration", "Business Development", "Content",
        "E-Commerce", "Factory & Production", "Graphics", "Human Resources",
        "IT", "Social Media", "Bandra Store", "Support Staff", "Warehouse", "SEO"
    ]

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_holidays():
    return [
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

# Initialize session state with minimal data
if 'clusters' not in st.session_state:
    st.session_state.clusters = [{
        'cluster_number': 1,
        'leave_type': 'Select Type',
        'from_date': datetime.now().date(),
        'till_date': datetime.now().date()
    }]

# Initialize other session states
for key in ['reset_form_tab1', 'reset_form_tab2', 'show_copy_section', 'email_config_status']:
    if key not in st.session_state:
        st.session_state[key] = False if key not in ['email_config_status'] else "Not Tested"

for key in ['form_data_tab1', 'form_data_tab2', 'cluster_codes', 'debug_logs', 'generated_codes']:
    if key not in st.session_state:
        if key == 'form_data_tab1':
            st.session_state[key] = {'employee_name': '', 'employee_code': '', 'department': 'Select Department', 
                                     'purpose': '', 'superior_name': 'Select Manager', 'is_cluster': False}
        elif key == 'form_data_tab2':
            st.session_state[key] = {'approval_password': '', 'action': 'Select Decision'}
        elif key == 'debug_logs':
            st.session_state[key] = []
        elif key == 'generated_codes':
            st.session_state[key] = set()
        else:
            st.session_state[key] = {}

# OPTIMIZED FUNCTIONS - Reduced computational expense

def add_debug_log(message, level="INFO"):
    """Add debug log message efficiently"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"
    st.session_state.debug_logs.append(log_entry)
    # Keep only last 20 logs for memory efficiency
    if len(st.session_state.debug_logs) > 20:
        st.session_state.debug_logs.pop(0)

# Cache expensive operations
@st.cache_resource(ttl=300)  # Cache connection for 5 minutes
def get_google_sheets_connection():
    """Cached Google Sheets connection"""
    try:
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
            "private_key": st.secrets[secrets_key]["private_key"],
            "client_email": st.secrets[secrets_key]["client_email"],
            "client_id": st.secrets[secrets_key]["client_id"],
            "auth_uri": st.secrets[secrets_key]["auth_uri"],
            "token_uri": st.secrets[secrets_key]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets[secrets_key]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets[secrets_key]["client_x509_cert_url"]
        }
        
        # Fix private key formatting
        private_key = creds_dict.get("private_key", "")
        if private_key and "\\n" in private_key:
            creds_dict["private_key"] = private_key.replace("\\n", "\n")
        
        SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
        client = gspread.authorize(creds)
        
        SHEET_NAME = "Leave_Applications"
        spreadsheet = client.open(SHEET_NAME)
        sheet = spreadsheet.sheet1
        
        return sheet
        
    except Exception as e:
        add_debug_log(f"Google Sheets connection error: {str(e)}", "ERROR")
        return None

# Optimized code generation
def generate_approval_password():
    """Generate a UNIQUE 5-digit alphanumeric password efficiently"""
    alphabet = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"  # Excluded confusing characters
    
    # Generate using secure random
    password = ''.join(secrets.choice(alphabet) for _ in range(5))
    
    # Check for uniqueness in current session
    if password in st.session_state.generated_codes:
        # Fallback: use timestamp hash
        timestamp_hash = hashlib.md5(str(time.time()).encode()).hexdigest().upper()
        password = ''.join([c for c in timestamp_hash if c in alphabet])[:5]
        if len(password) < 5:
            password = password + secrets.choice(alphabet[:(5 - len(password))])
    
    st.session_state.generated_codes.add(password)
    return password

# Optimized email connection
@st.cache_data(ttl=600)
def get_email_credentials():
    """Get email credentials with caching"""
    try:
        # Try different possible secret names
        possible_sections = ['EMAIL', 'email']
        for section in possible_sections:
            if section in st.secrets:
                sender_email = st.secrets[section].get("sender_email")
                sender_password = st.secrets[section].get("sender_password")
                if sender_email and sender_password:
                    return sender_email, sender_password, section
        
        # Fallback to environment variables
        sender_email = os.environ.get("EMAIL_SENDER")
        sender_password = os.environ.get("EMAIL_PASSWORD")
        if sender_email and sender_password:
            return sender_email, sender_password, "Environment"
        
        return "", "", "Not Found"
        
    except Exception as e:
        return "", "", f"Error: {str(e)}"

def create_smtp_connection(sender_email, sender_password):
    """Create SMTP connection with timeout"""
    try:
        # Try port 465 first (most reliable)
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=5, context=context)
        server.login(sender_email, sender_password)
        return server, "SMTP_SSL (Port 465)"
    except:
        try:
            # Fallback to port 587
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
            server.starttls(context=ssl.create_default_context())
            server.login(sender_email, sender_password)
            return server, "STARTTLS (Port 587)"
        except Exception as e:
            return None, str(e)

# Optimized calculation functions
def calculate_working_days(from_date, till_date):
    """Calculate total number of days efficiently"""
    return (till_date - from_date).days + 1

def calculate_days(from_date, till_date, leave_type):
    """Calculate number of days with proper logic"""
    if leave_type == "Half Day":
        return 0.5
    elif leave_type == "Early Exit":
        return ""
    else:
        return calculate_working_days(from_date, till_date)

# SIDEBAR - OPTIMIZED VERSION
st.sidebar.title("🔧 Configuration Panel")

# Check email configuration
sender_email, sender_password, source = get_email_credentials()
email_configured = bool(sender_email and sender_password)

st.sidebar.markdown("### 📧 Email Configuration")
if email_configured:
    st.sidebar.success(f"✅ Configured ({source})")
else:
    st.sidebar.error("❌ Not configured")

# Test connections
if st.sidebar.button("🔗 Test Connections", use_container_width=True):
    with st.sidebar:
        with st.spinner("Testing..."):
            # Test Google Sheets
            sheet = get_google_sheets_connection()
            if sheet:
                st.success("✅ Google Sheets: Connected")
            else:
                st.error("❌ Google Sheets: Failed")
            
            # Test Email
            if email_configured:
                try:
                    test_server, method = create_smtp_connection(sender_email, sender_password)
                    if test_server:
                        test_server.quit()
                        st.success(f"✅ Email: Working ({method})")
                    else:
                        st.error("❌ Email: Connection failed")
                except:
                    st.error("❌ Email: Authentication failed")
            else:
                st.warning("⚠️ Email: Not configured")

# MAIN APPLICATION
st.markdown("""
    <div class="company-header">
        <h1>VOLAR FASHION</h1>
        <h2>Leave Management System</h2>
    </div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["📝 Submit Leave", "✅ Approval Portal", "📅 Company Holidays"])

with tab1:
    # Email status
    if not email_configured:
        st.warning("⚠️ Email notifications may not work. Configure in secrets.")
    
    # Form Header
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 2rem;">
            <div class="icon-badge">📋</div>
            <h3 style="margin: 0;">Leave Application Form</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Reset form if needed
    if st.session_state.reset_form_tab1:
        st.session_state.form_data_tab1 = {
            'employee_name': '', 'employee_code': '', 'department': 'Select Department',
            'purpose': '', 'superior_name': 'Select Manager', 'is_cluster': False
        }
        st.session_state.clusters = [{
            'cluster_number': 1, 'leave_type': 'Select Type',
            'from_date': datetime.now().date(), 'till_date': datetime.now().date()
        }]
        st.session_state.reset_form_tab1 = False
    
    # Form layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        employee_name = st.text_input(
            "👤 Full Name",
            value=st.session_state.form_data_tab1['employee_name'],
            placeholder="Enter your full name"
        )
        employee_code = st.text_input(
            "🔢 Employee ID",
            value=st.session_state.form_data_tab1['employee_code'],
            placeholder="e.g., VF-EMP-001"
        )
    
    with col2:
        department = st.selectbox(
            "🏛️ Department",
            ["Select Department"] + get_departments(),
            index=0 if st.session_state.form_data_tab1['department'] == 'Select Department' 
                   else get_departments().index(st.session_state.form_data_tab1['department']) + 1
        )
        
        is_cluster = st.checkbox(
            "Is this a Cluster Holiday? (Multiple leave periods)",
            value=st.session_state.form_data_tab1['is_cluster']
        )
    
    # CLUSTER HOLIDAY SECTION
    if is_cluster:
        st.markdown("""
            <div class="cluster-section">
                <h4 style="color: white; margin: 0;">Cluster Holiday Periods</h4>
                <p style="color: #dbeafe; margin: 5px 0 0 0; font-size: 0.9rem;">
                    Add multiple leave periods below
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        for i, cluster in enumerate(st.session_state.clusters):
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                leave_type = st.selectbox(
                    f"Leave Type - Period {i+1}",
                    ["Select Type", "Full Day", "Half Day", "Early Exit"],
                    index=0 if cluster['leave_type'] == 'Select Type' 
                           else ["Select Type", "Full Day", "Half Day", "Early Exit"].index(cluster['leave_type']),
                    key=f"leave_type_{i}"
                )
                st.session_state.clusters[i]['leave_type'] = leave_type
            
            with col2:
                if leave_type in ["Half Day", "Early Exit"]:
                    selected_date = st.date_input(
                        f"Date - Period {i+1}",
                        value=cluster['from_date'],
                        min_value=datetime.now().date(),
                        key=f"date_{i}"
                    )
                    st.session_state.clusters[i]['from_date'] = selected_date
                    st.session_state.clusters[i]['till_date'] = selected_date
                else:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        from_date = st.date_input(
                            f"From - Period {i+1}",
                            value=cluster['from_date'],
                            min_value=datetime.now().date(),
                            key=f"from_{i}"
                        )
                        st.session_state.clusters[i]['from_date'] = from_date
                    
                    with col_b:
                        till_date = st.date_input(
                            f"To - Period {i+1}",
                            value=cluster['till_date'],
                            min_value=datetime.now().date(),
                            key=f"to_{i}"
                        )
                        st.session_state.clusters[i]['till_date'] = till_date
            
            with col3:
                if leave_type != "Select Type":
                    days = calculate_days(
                        st.session_state.clusters[i]['from_date'],
                        st.session_state.clusters[i]['till_date'],
                        leave_type
                    )
                    days_display = "N/A" if leave_type == "Early Exit" else (f"{days}" if leave_type == "Full Day" else "0.5")
                    st.metric("Days", days_display)
            
            with col4:
                if len(st.session_state.clusters) > 1:
                    if st.button("❌ Remove", key=f"remove_{i}"):
                        st.session_state.clusters.pop(i)
                        st.rerun()
        
        if st.button("➕ Add Another Period", key="add_cluster"):
            st.session_state.clusters.append({
                'cluster_number': len(st.session_state.clusters) + 1,
                'leave_type': 'Select Type',
                'from_date': datetime.now().date(),
                'till_date': datetime.now().date()
            })
            st.rerun()
    
    else:
        # SINGLE HOLIDAY
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            leave_type = st.selectbox(
                "📋 Leave Type",
                ["Select Type", "Full Day", "Half Day", "Early Exit"],
                index=0,
                key="leave_type_single"
            )
        
        with col2:
            if leave_type in ["Half Day", "Early Exit"]:
                selected_date = st.date_input(
                    "📅 Date",
                    value=st.session_state.clusters[0]['from_date'],
                    min_value=datetime.now().date(),
                    key="date_single"
                )
                st.session_state.clusters[0]['from_date'] = selected_date
                st.session_state.clusters[0]['till_date'] = selected_date
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    from_date = st.date_input(
                        "📅 Start Date",
                        value=st.session_state.clusters[0]['from_date'],
                        min_value=datetime.now().date(),
                        key="from_single"
                    )
                    st.session_state.clusters[0]['from_date'] = from_date
                
                with col_b:
                    till_date = st.date_input(
                        "📅 End Date",
                        value=st.session_state.clusters[0]['till_date'],
                        min_value=datetime.now().date(),
                        key="till_single"
                    )
                    st.session_state.clusters[0]['till_date'] = till_date
        
        st.session_state.clusters[0]['leave_type'] = leave_type
        
        if leave_type != "Select Type":
            days = calculate_days(
                st.session_state.clusters[0]['from_date'],
                st.session_state.clusters[0]['till_date'],
                leave_type
            )
            if leave_type == "Early Exit":
                st.info("⚠️ Only 2 Early Leaves permitted per month")
            else:
                st.metric("Leave Duration", f"{days} {'day' if days == 1 else 'days'}")
    
    # Purpose and Manager
    purpose = st.text_area(
        "Purpose of Leave",
        value=st.session_state.form_data_tab1['purpose'],
        placeholder="Please provide a clear explanation...",
        height=100
    )
    
    superiors = get_superiors()
    superior_name = st.selectbox(
        "👔 Reporting Manager",
        ["Select Manager"] + list(superiors.keys()),
        index=0 if st.session_state.form_data_tab1['superior_name'] == 'Select Manager' 
               else list(["Select Manager"] + list(superiors.keys())).index(st.session_state.form_data_tab1['superior_name'])
    )
    
    # Submit Button
    if st.button("🚀 Submit Leave Request", type="primary", use_container_width=True):
        # Validation
        errors = []
        if not all([employee_name, employee_code, department != "Select Department", 
                   purpose, superior_name != "Select Manager"]):
            errors.append("Please complete all required fields")
        
        for i, cluster in enumerate(st.session_state.clusters):
            if cluster['leave_type'] == "Select Type":
                errors.append(f"Select leave type for Period {i+1}")
                break
            
            if cluster['leave_type'] == "Full Day" and cluster['from_date'] > cluster['till_date']:
                errors.append(f"End date must be after start date for Period {i+1}")
                break
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            with st.spinner('Submitting...'):
                sheet = get_google_sheets_connection()
                
                if sheet:
                    try:
                        # Generate codes and submit
                        cluster_codes = {}
                        for i in range(len(st.session_state.clusters)):
                            code = generate_approval_password()
                            cluster_codes[i] = code
                        
                        # Submit each cluster
                        submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        superior_email = superiors[superior_name]
                        
                        for i, cluster in enumerate(st.session_state.clusters):
                            row_data = [
                                submission_date, employee_name, employee_code, department,
                                cluster['leave_type'], 
                                str(calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])),
                                purpose, cluster['from_date'].strftime("%Y-%m-%d"),
                                cluster['till_date'].strftime("%Y-%m-%d"), superior_name,
                                superior_email, "Pending", "", cluster_codes[i],
                                "Yes" if is_cluster else "No", i+1 if is_cluster else ""
                            ]
                            sheet.append_row(row_data)
                        
                        # Try to send email
                        if email_configured:
                            try:
                                # Simplified email sending
                                msg = MIMEMultipart()
                                msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
                                msg['To'] = superior_email
                                msg['Subject'] = f"Leave Approval: {employee_name}"
                                
                                body = f"""
                                Leave approval required for {employee_name} ({employee_code}).
                                Department: {department}
                                
                                Please use this link to approve/reject:
                                https://your-app-url.streamlit.app/
                                
                                Approval codes:
                                {chr(10).join([f'Period {idx+1}: {code}' for idx, code in cluster_codes.items()])}
                                """
                                msg.attach(MIMEText(body, 'plain'))
                                
                                server, method = create_smtp_connection(sender_email, sender_password)
                                if server:
                                    server.sendmail(sender_email, superior_email, msg.as_string())
                                    server.quit()
                                    st.success("✅ Application submitted and email sent!")
                                else:
                                    st.warning("⚠️ Application saved but email failed")
                            except:
                                st.warning("⚠️ Application saved but email failed")
                        else:
                            st.success("✅ Application submitted successfully!")
                        
                        # Show manual codes if needed
                        st.session_state.cluster_codes = cluster_codes
                        st.session_state.show_copy_section = True
                        
                        # Reset form
                        st.session_state.reset_form_tab1 = True
                        st.session_state.generated_codes.clear()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error("Database connection failed")

with tab2:
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 2rem;">
            <div class="icon-badge">✅</div>
            <h3 style="margin: 0;">Manager Approval Portal</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Reset form if needed
    if st.session_state.reset_form_tab2:
        st.session_state.form_data_tab2 = {'approval_password': '', 'action': 'Select Decision'}
        st.session_state.reset_form_tab2 = False
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        approval_password = st.text_input(
            "🔑 Approval Code",
            value=st.session_state.form_data_tab2['approval_password'],
            type="password",
            placeholder="Enter 5-character code"
        )
    
    action = st.selectbox(
        "Select Action",
        ["Select Decision", "✅ Approve", "❌ Reject"],
        index=["Select Decision", "✅ Approve", "❌ Reject"].index(st.session_state.form_data_tab2['action'])
    )
    
    if st.button("Submit Decision", type="primary", use_container_width=True):
        if not all([approval_password, action != "Select Decision"]):
            st.error("Please enter code and select decision")
        elif len(approval_password) != 5:
            st.error("Code must be 5 characters")
        else:
            with st.spinner("Processing..."):
                sheet = get_google_sheets_connection()
                if sheet:
                    try:
                        all_records = sheet.get_all_values()
                        updated = False
                        
                        for idx, row in enumerate(all_records):
                            if idx == 0:
                                continue
                            if len(row) > 13 and row[13] == approval_password:
                                status = "Approved" if action == "✅ Approve" else "Rejected"
                                sheet.update_cell(idx + 1, 12, status)
                                sheet.update_cell(idx + 1, 13, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                sheet.update_cell(idx + 1, 14, "USED")
                                updated = True
                                break
                        
                        if updated:
                            st.success(f"✅ Leave request {status.lower()}!")
                            st.session_state.reset_form_tab2 = True
                            st.rerun()
                        else:
                            st.error("❌ Invalid or already used code")
                    except:
                        st.error("Update failed")
                else:
                    st.error("Database connection failed")

with tab3:
    st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 2rem;">
            <div class="icon-badge">📅</div>
            <h3 style="margin: 0;">Company Holidays 2026</h3>
        </div>
    """, unsafe_allow_html=True)
    
    holidays = get_holidays()
    
    # Display holiday count
    st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0; padding: 1.5rem; 
                    background: var(--card-bg); border-radius: 16px; 
                    border: 1px solid var(--border-color);">
            <div style="font-size: 3rem; font-weight: 700; 
                        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%); 
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {len(holidays)}
            </div>
            <div style="font-size: 1.2rem; font-weight: 600; color: var(--text-primary);">
                Official Holidays
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Create table
    holiday_data = []
    for holiday in holidays:
        holiday_data.append({
            "Date": holiday["date"],
            "Day": holiday["day"],
            "Holiday": holiday["holiday"]
        })
    
    df = pd.DataFrame(holiday_data)
    
    # Apply styling
    def style_day(val):
        color_map = {
            "Saturday": "background: rgba(33, 150, 243, 0.1); color: #2196f3;",
            "Sunday": "background: rgba(244, 67, 54, 0.1); color: #f44336;",
            "Monday": "background: rgba(76, 175, 80, 0.1); color: #4caf50;",
            "Tuesday": "background: rgba(255, 152, 0, 0.1); color: #ff9800;",
            "Wednesday": "background: rgba(156, 39, 176, 0.1); color: #9c27b0;",
            "Thursday": "background: rgba(0, 188, 212, 0.1); color: #00bcd4;",
            "Friday": "background: rgba(103, 58, 183, 0.1); color: #673ab7;"
        }
        return f'<span style="padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; {color_map.get(val, "")}">{val}</span>'
    
    df["Day"] = df["Day"].apply(style_day)
    
    # Display table
    st.markdown("""
        <style>
        .dataframe { width: 100%; border-collapse: collapse; }
        .dataframe th { background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%); 
                       color: white; padding: 1rem; text-align: left; }
        .dataframe td { padding: 1rem; border-bottom: 1px solid var(--border-color); }
        .dataframe tr:hover { background: rgba(103, 58, 183, 0.05); }
        </style>
    """, unsafe_allow_html=True)
    
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style="text-align: center; color: var(--text-light); padding: 3rem 0; margin-top: 4rem; border-top: 1px solid var(--border-color);">
        <strong>VOLAR FASHION PVT LTD</strong><br>
        Human Resources Management System<br>
        📧 hrvolarfashion@gmail.com<br>
        © 2026 VOLAR FASHION.
    </div>
""", unsafe_allow_html=True)
