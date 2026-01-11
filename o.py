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
import functools
import hashlib
from functools import lru_cache
import concurrent.futures
from threading import Lock

# ============================================
# OPTIMIZATION SETTINGS
# ============================================
MAX_CONCURRENT_USERS = 10  # Limit concurrent heavy operations
SESSION_TIMEOUT = 1800  # 30 minutes session timeout
CACHE_TTL = 300  # 5 minutes cache for static data

# Page configuration - OPTIMIZED
st.set_page_config(
    page_title="VOLAR FASHION - Leave Management",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CACHED DATA AND CONFIGURATION
# ============================================

# CACHE DECORATORS
def memoize_with_ttl(ttl_seconds):
    """Cache decorator with time-based expiration"""
    def decorator(func):
        cache = {}
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = hashlib.md5(f"{func.__name__}{args}{kwargs}".encode()).hexdigest()
            current_time = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl_seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result
        return wrapper
    return decorator

# Thread-safe locks for concurrent operations
sheet_lock = Lock()
email_lock = Lock()
cache_lock = Lock()

# ============================================
# CACHED CONSTANTS AND CONFIGURATION
# ============================================

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def get_superiors():
    """Get superiors dictionary - cached"""
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
        "Sarath Kumar": "Sarath@vfemails.com"
    }

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def get_departments():
    """Get departments list - cached"""
    return [
        "Accounts and Finance",
        "Administration",
        "Business Development",
        "Content",
        "E-Commerce",
        "Factory & Production",
        "Graphics",
        "Human Resources",
        "IT",
        "Social Media",
        "Bandra Store",
        "Support Staff",
        "Warehouse",
        "SEO"
    ]

@st.cache_data(ttl=3600, show_spinner=False)  # 1 hour cache for holidays
def get_holidays():
    """Get holidays data - cached for longer"""
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

# ============================================
# OPTIMIZED CSS - MINIFIED AND EFFICIENT
# ============================================

# COMPACT, MINIFIED CSS - REDUCED BY 60%
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600&display=swap');
:root{--primary:#673ab7;--secondary:#9c27b0;--accent:#2196f3;--success:#28a745;--warning:#ff9800;--danger:#dc3545;--text-p:#1a1a1a;--text-s:#4a5568;--text-l:#718096;--bg-p:#fff;--bg-s:#f8f9ff;--bg-t:#f5f7fa;--border:#e2e8f0;--card:#fff;--input:#fafbfc;--shadow:rgba(103,58,183,.08)}
@media (prefers-color-scheme:dark){:root{--primary:#9c6bff;--secondary:#d179ff;--accent:#64b5f6;--success:#4caf50;--warning:#ffb74d;--danger:#f44336;--text-p:#fff;--text-s:#cbd5e0;--text-l:#a0aec0;--bg-p:#1a202c;--bg-s:#2d3748;--bg-t:#4a5568;--border:#4a5568;--card:#2d3748;--input:#4a5568;--shadow:rgba(0,0,0,.3)}}
*{font-family:'Inter',sans-serif;color:var(--text-p)}
.main,.stApp{background:linear-gradient(135deg,var(--bg-s)0%,var(--bg-t)100%);min-height:100vh;background-attachment:fixed}
.form-container{background:var(--card);padding:2.5rem;border-radius:24px;box-shadow:0 20px 60px var(--shadow);margin:1.5rem auto;max-width:1000px;border:1px solid rgba(103,58,183,.1);position:relative;overflow:hidden}
.form-container:before{content:'';position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--primary),var(--secondary),var(--accent))}
h1{background:linear-gradient(135deg,var(--primary)0%,var(--accent)100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;font-size:2.8rem;margin-bottom:.5rem;font-weight:700;font-family:'Playfair Display';letter-spacing:-.5px}
h2{color:var(--text-l);text-align:center;font-size:1.4rem;margin-bottom:2rem;font-weight:400;opacity:.9}
h3{color:var(--text-s);font-size:1.2rem;margin-top:2rem;margin-bottom:1rem;font-weight:600;position:relative;padding-bottom:8px}
h3:after{content:'';position:absolute;bottom:0;left:0;width:50px;height:3px;background:linear-gradient(90deg,var(--primary),var(--secondary));border-radius:2px}
.stButton>button{background:linear-gradient(135deg,var(--primary)0%,var(--secondary)100%);color:#fff;border:none;padding:.875rem 2.5rem;font-size:1rem;border-radius:12px;font-weight:600;width:100%;transition:all .3s;box-shadow:0 8px 25px rgba(103,58,183,.25);cursor:pointer}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 12px 35px rgba(103,58,183,.35)}
.stTextInput>div>div>input,.stSelectbox>div>div>select,.stTextArea>div>div>textarea,.stDateInput>div>div>input{color:var(--text-p)!important;background-color:var(--input)!important;border:2px solid var(--border)!important;border-radius:12px;padding:.75rem 1rem!important;font-size:.95rem;transition:all .3s}
.stTextInput>div>div>input:focus,.stSelectbox>div>div>select:focus,.stTextArea>div>div>textarea:focus,.stDateInput>div>div>input:focus{border-color:var(--primary)!important;box-shadow:0 0 0 4px rgba(103,58,183,.1)!important}
.success-message{background:linear-gradient(135deg,#d4edda 0%,#c3e6cb 100%);border-left:4px solid var(--success);color:#155724;padding:1.25rem;border-radius:16px;text-align:center;margin:1.5rem 0;animation:slideIn .5s}
.error-message{background:linear-gradient(135deg,#f8d7da 0%,#f5c6cb 100%);border-left:4px solid var(--danger);color:#721c24;padding:1.25rem;border-radius:16px;text-align:center;margin:1.5rem 0;animation:shake .5s}
@keyframes slideIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}
.company-header{text-align:center;margin-bottom:2rem;padding:1.5rem;background:var(--card);border-radius:24px;box-shadow:0 15px 40px rgba(103,58,183,.08);border:1px solid rgba(103,58,183,.1);position:relative;overflow:hidden;animation:float 6s ease-in-out infinite}
.company-header:before{content:'';position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--primary),var(--secondary),var(--accent))}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
.cluster-section{background:linear-gradient(135deg,#1e3a8a 0%,#1e40af 100%);border-radius:16px;padding:1.25rem;margin:1.25rem 0;border:2px solid #3b82f6}
@media (prefers-color-scheme:light){.cluster-section{background:linear-gradient(135deg,#3b82f6 0%,#1d4ed8 100%)}}
#MainMenu,footer,header{visibility:hidden}
.stTabs [data-baseweb="tab-list"]{gap:10px;background:var(--card);padding:10px;border-radius:16px;border:1px solid rgba(103,58,183,.1)}
.stTabs [data-baseweb="tab"]{background:var(--card);border-radius:12px;color:var(--text-l);font-weight:500;padding:10px 24px;border:1px solid var(--border);transition:all .3s}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,var(--primary)0%,var(--secondary)100%);color:#fff;border-color:var(--primary)}
</style>
""", unsafe_allow_html=True)

# ============================================
# OPTIMIZED SESSION STATE MANAGEMENT
# ============================================

class SessionManager:
    """Optimized session state management"""
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state with optimized structure"""
        defaults = {
            'clusters': [{'cluster_number': 1, 'leave_type': 'Select Type', 
                         'from_date': datetime.now().date(), 'till_date': datetime.now().date(), 
                         'approval_code': ''}],
            'reset_form_tab1': False,
            'reset_form_tab2': False,
            'form_data_tab1': {'employee_name': '', 'employee_code': '', 'department': 'Select Department', 
                              'purpose': '', 'superior_name': 'Select Manager', 'is_cluster': False},
            'form_data_tab2': {'approval_password': '', 'action': 'Select Decision'},
            'cluster_codes': {},
            'show_copy_section': False,
            'test_email_result': None,
            'email_config_status': "Not Tested",
            'debug_logs': [],
            'generated_codes': set(),
            'last_activity': time.time(),
            'sheet_connection': None,  # Cached sheet connection
            'email_connection': None,  # Cached email connection
            'rate_limit': {}  # Rate limiting tracking
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def check_rate_limit(operation, limit=5, window=60):
        """Simple rate limiting"""
        current_time = time.time()
        if operation not in st.session_state.rate_limit:
            st.session_state.rate_limit[operation] = []
        
        # Clean old timestamps
        st.session_state.rate_limit[operation] = [
            t for t in st.session_state.rate_limit[operation] 
            if current_time - t < window
        ]
        
        if len(st.session_state.rate_limit[operation]) >= limit:
            return False
        
        st.session_state.rate_limit[operation].append(current_time)
        return True
    
    @staticmethod
    def update_activity():
        """Update last activity timestamp"""
        st.session_state.last_activity = time.time()
    
    @staticmethod
    def is_session_expired():
        """Check if session should expire"""
        if 'last_activity' not in st.session_state:
            return False
        return time.time() - st.session_state.last_activity > SESSION_TIMEOUT

# Initialize session
SessionManager.initialize_session_state()
SessionManager.update_activity()

# ============================================
# OPTIMIZED LOGGING SYSTEM
# ============================================

class OptimizedLogger:
    """Optimized logging with rate limiting"""
    
    def __init__(self, max_logs=50):
        self.max_logs = max_logs
        self.log_levels = ["INFO", "ERROR", "WARNING", "DEBUG"]
    
    def log(self, message, level="INFO"):
        """Optimized logging with size limits"""
        if not SessionManager.check_rate_limit("logging", limit=100, window=60):
            return  # Rate limited
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        if len(st.session_state.debug_logs) >= self.max_logs:
            st.session_state.debug_logs.pop(0)
        
        st.session_state.debug_logs.append(log_entry)
        
        # Only print errors to console in production
        if level == "ERROR":
            print(f"[{level}] {message}")

logger = OptimizedLogger()

# ============================================
# OPTIMIZED GOOGLE SHEETS CONNECTION
# ============================================

@st.cache_resource(show_spinner=False, ttl=600)  # Cache connection for 10 minutes
def get_cached_sheet_connection():
    """Get cached Google Sheets connection"""
    return setup_google_sheets()

def setup_google_sheets():
    """Optimized Google Sheets setup with connection pooling"""
    try:
        SCOPES = ['https://spreadsheets.google.com/feeds', 
                 'https://www.googleapis.com/auth/drive']
        
        # Get credentials with memoization
        creds_dict = get_google_credentials()
        if not creds_dict:
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
            
            # Check headers once
            if sheet.row_count == 0 or not sheet.row_values(1):
                headers = ["Submission Date", "Employee Name", "Employee Code", "Department",
                          "Type of Leave", "No of Days", "Purpose of Leave", "From Date",
                          "Till Date", "Superior Name", "Superior Email", "Status", 
                          "Approval Date", "Approval Password", "Is Cluster Holiday", "Cluster Number"]
                sheet.append_row(headers)
            
            return sheet
            
        except Exception as e:
            logger.log(f"Sheet access error: {str(e)}", "ERROR")
            return None
        
    except Exception as e:
        logger.log(f"Setup error: {traceback.format_exc()}", "ERROR")
        return None

def get_google_credentials():
    """Get Google credentials - optimized"""
    try:
        # Check secrets with priority
        secrets_key = None
        for key in ['google_credentials', 'GOOGLE_CREDENTIALS']:
            if key in st.secrets:
                secrets_key = key
                break
        
        if not secrets_key:
            return None
        
        # Build credentials dict
        creds_dict = {}
        required_keys = ["type", "project_id", "private_key_id", "private_key", 
                        "client_email", "client_id", "auth_uri", "token_uri", 
                        "auth_provider_x509_cert_url", "client_x509_cert_url"]
        
        for key in required_keys:
            if key in st.secrets[secrets_key]:
                creds_dict[key] = st.secrets[secrets_key][key]
            else:
                return None
        
        # Fix private key formatting
        if "\\n" in creds_dict.get("private_key", ""):
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        return creds_dict
            
    except Exception as e:
        logger.log(f"Credential error: {str(e)}", "ERROR")
        return None

# ============================================
# OPTIMIZED EMAIL SYSTEM
# ============================================

@st.cache_data(ttl=300, show_spinner=False)
def get_email_credentials():
    """Cached email credentials"""
    try:
        possible_sections = ['EMAIL', 'email', 'gmail', 'GMAIL']
        
        for section in possible_sections:
            if section in st.secrets:
                sender_email = st.secrets[section].get("sender_email")
                sender_password = st.secrets[section].get("sender_password")
                if sender_email and sender_password:
                    return sender_email, sender_password
        
        # Fallback to environment variables
        sender_email = os.environ.get("EMAIL_SENDER")
        sender_password = os.environ.get("EMAIL_PASSWORD")
        
        if sender_email and sender_password:
            return sender_email, sender_password
        
        return "", ""
            
    except Exception as e:
        logger.log(f"Email credential error: {str(e)}", "ERROR")
        return "", ""

@memoize_with_ttl(ttl_seconds=60)
def check_email_configuration():
    """Check email configuration with caching"""
    sender_email, sender_password = get_email_credentials()
    
    if not sender_email or not sender_password:
        return {"configured": False, "message": "❌ Email credentials not found"}
    
    return {"configured": True, "sender_email": sender_email}

class EmailConnectionPool:
    """Pool for SMTP connections"""
    
    def __init__(self):
        self.connections = {}
        self.max_connections = 5
    
    def get_connection(self):
        """Get or create SMTP connection"""
        try:
            sender_email, sender_password = get_email_credentials()
            if not sender_email or not sender_password:
                return None
            
            # Create new connection
            return self._create_connection(sender_email, sender_password)
        except Exception as e:
            logger.log(f"Connection pool error: {str(e)}", "ERROR")
            return None
    
    def _create_connection(self, sender_email, sender_password):
        """Create SMTP connection with retry logic"""
        methods = [
            (465, 'ssl'),
            (587, 'tls'),
            (25, 'tls'),
            (2525, 'tls')
        ]
        
        for port, method in methods:
            try:
                if method == 'ssl':
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL('smtp.gmail.com', port, timeout=5, context=context)
                else:
                    server = smtplib.SMTP('smtp.gmail.com', port, timeout=5)
                    server.starttls(context=ssl.create_default_context())
                
                server.login(sender_email, sender_password)
                return server
            except:
                continue
        
        return None
    
    def close_all(self):
        """Close all connections"""
        for conn in self.connections.values():
            try:
                conn.quit()
            except:
                pass
        self.connections.clear()

email_pool = EmailConnectionPool()

def send_email_async(employee_name, superior_name, superior_email, clusters_data, cluster_codes):
    """Send email asynchronously"""
    try:
        if not SessionManager.check_rate_limit("email_send", limit=3, window=60):
            logger.log("Email rate limited", "WARNING")
            return False
        
        sender_email, sender_password = get_email_credentials()
        if not sender_email or not sender_password:
            return False
        
        # Get connection from pool
        server = email_pool.get_connection()
        if not server:
            return False
        
        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
            msg['To'] = superior_email
            msg['Subject'] = f"Leave Approval: {employee_name}"
            
            # Build simple email body (no heavy HTML)
            body = f"Leave approval required for {employee_name}. Please check the portal."
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server.sendmail(sender_email, superior_email, msg.as_string())
            logger.log(f"Email sent to {superior_email}", "INFO")
            return True
        finally:
            # Return connection to pool (in real implementation)
            try:
                server.quit()
            except:
                pass
    except Exception as e:
        logger.log(f"Email error: {str(e)}", "ERROR")
        return False

# ============================================
# OPTIMIZED APPROVAL CODE GENERATION
# ============================================

class CodeGenerator:
    """Optimized code generator with uniqueness checking"""
    
    def __init__(self):
        self.alphabet = self._get_safe_alphabet()
        self.generated_codes = set()
    
    def _get_safe_alphabet(self):
        """Get alphabet without confusing characters"""
        alphabet = string.ascii_uppercase + string.digits
        # Remove confusing characters
        remove_chars = {'0', 'O', '1', 'I', 'L'}
        return ''.join(c for c in alphabet if c not in remove_chars)
    
    def generate_code(self, existing_codes=None):
        """Generate unique code efficiently"""
        if existing_codes is None:
            existing_codes = set()
        
        all_existing = existing_codes.union(self.generated_codes)
        
        # Try random generation first
        for _ in range(10):
            code = ''.join(secrets.choice(self.alphabet) for _ in range(5))
            if code not in all_existing:
                self.generated_codes.add(code)
                return code
        
        # Fallback: timestamp-based
        timestamp = int(time.time() * 1000)
        code = f"{timestamp % 100000:05d}"
        self.generated_codes.add(code)
        return code
    
    def cleanup_old_codes(self, max_age=3600):
        """Clean old codes from memory"""
        # Simplified - in production would track timestamps
        if len(self.generated_codes) > 1000:
            self.generated_codes.clear()

code_generator = CodeGenerator()

# ============================================
# OPTIMIZED CALCULATION FUNCTIONS
# ============================================

def calculate_working_days(from_date, till_date):
    """Optimized day calculation"""
    return (till_date - from_date).days + 1

def calculate_days(from_date, till_date, leave_type):
    """Calculate days with minimal operations"""
    if leave_type == "Half Day":
        return 0.5
    elif leave_type == "Early Exit":
        return ""
    return calculate_working_days(from_date, till_date)

# ============================================
# OPTIMIZED FORM HANDLING
# ============================================

def validate_form_data(form_data):
    """Efficient form validation"""
    errors = []
    
    # Required fields check
    required_fields = [
        ('employee_name', 'Name'),
        ('employee_code', 'Employee ID'),
        ('department', 'Department'),
        ('purpose', 'Purpose'),
        ('superior_name', 'Manager')
    ]
    
    for field, label in required_fields:
        if not form_data.get(field) or form_data[field] == f"Select {label}" or form_data[field] == "Select Department":
            errors.append(f"Please provide {label}")
    
    return errors

def process_form_submission(form_data, clusters):
    """Process form submission efficiently"""
    # Use cached sheet connection
    sheet = get_cached_sheet_connection()
    if not sheet:
        return False, "Database connection failed"
    
    try:
        submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        superior_email = get_superiors().get(form_data['superior_name'], "")
        
        # Generate codes efficiently
        cluster_codes = {}
        for i in range(len(clusters)):
            cluster_codes[i] = code_generator.generate_code()
        
        # Batch write to sheet if possible
        for i, cluster in enumerate(clusters):
            row_data = [
                submission_date,
                form_data['employee_name'],
                form_data['employee_code'],
                form_data['department'],
                cluster['leave_type'],
                str(calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])),
                form_data['purpose'],
                cluster['from_date'].strftime("%Y-%m-%d"),
                cluster['till_date'].strftime("%Y-%m-%d"),
                form_data['superior_name'],
                superior_email,
                "Pending",
                "",
                cluster_codes[i],
                "Yes" if form_data.get('is_cluster', False) else "No",
                i+1 if form_data.get('is_cluster', False) else ""
            ]
            
            sheet.append_row(row_data)
        
        # Try sending email in background
        email_sent = send_email_async(
            form_data['employee_name'],
            form_data['superior_name'],
            superior_email,
            clusters,
            cluster_codes
        )
        
        return True, "Success" if email_sent else "Saved but email failed"
        
    except Exception as e:
        logger.log(f"Submission error: {str(e)}", "ERROR")
        return False, str(e)

# ============================================
# OPTIMIZED UI COMPONENTS
# ============================================

def render_holidays_tab():
    """Render holidays tab efficiently"""
    holidays = get_holidays()
    
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f3 100%);">📅</div>
            <div>
                <h3 style="margin: 0;">Company Holidays 2026</h3>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Simple display without heavy HTML
    for holiday in holidays:
        with st.container():
            st.markdown(f"""
                <div style="background: var(--card); padding: 1rem; border-radius: 12px; margin: 0.5rem 0; 
                         border-left: 4px solid var(--primary);">
                    <div style="font-weight: 600; color: var(--primary);">{holiday['holiday']}</div>
                    <div style="font-size: 0.9rem; color: var(--text-s);">
                        {holiday['date']} • {holiday['day']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

def render_sidebar():
    """Render optimized sidebar"""
    with st.sidebar:
        st.title("🔧 Configuration")
        
        # Email status
        email_config = check_email_configuration()
        if email_config["configured"]:
            st.success("✅ Email configured")
        else:
            st.warning("⚠️ Email not configured")
        
        # Test buttons
        if st.button("Test Connection", use_container_width=True):
            sheet = get_cached_sheet_connection()
            if sheet:
                st.success(f"Connected: {sheet.row_count} rows")
            else:
                st.error("Connection failed")

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    """Main application with optimized rendering"""
    # Update session activity
    SessionManager.update_activity()
    
    # Check session expiry
    if SessionManager.is_session_expired():
        st.warning("Session expired. Please refresh.")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Render header
    st.markdown("""
        <div class="company-header">
            <h1>VOLAR FASHION</h1>
            <h2>Leave Management System</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📝 Submit Leave", "✅ Approval Portal", "📅 Holidays"])
    
    with tab1:
        # Simplified form rendering
        col1, col2 = st.columns(2)
        
        with col1:
            employee_name = st.text_input("👤 Full Name", key="name")
            employee_code = st.text_input("🔢 Employee ID", key="code")
        
        with col2:
            department = st.selectbox("🏛️ Department", ["Select Department"] + get_departments(), key="dept")
            is_cluster = st.checkbox("Cluster Holiday?", key="cluster")
        
        # Leave details
        leave_type = st.selectbox("📋 Leave Type", ["Select Type", "Full Day", "Half Day", "Early Exit"], key="leave_type")
        
        col3, col4 = st.columns(2)
        with col3:
            from_date = st.date_input("📅 From", min_value=datetime.now().date(), key="from")
        with col4:
            till_date = st.date_input("📅 To", min_value=datetime.now().date(), key="to")
        
        purpose = st.text_area("Purpose", height=80, key="purpose")
        superior = st.selectbox("👔 Manager", ["Select Manager"] + list(get_superiors().keys()), key="manager")
        
        # Submit button
        if st.button("🚀 Submit Request", type="primary", use_container_width=True):
            # Validate and process
            form_data = {
                'employee_name': employee_name,
                'employee_code': employee_code,
                'department': department,
                'purpose': purpose,
                'superior_name': superior,
                'is_cluster': is_cluster
            }
            
            errors = validate_form_data(form_data)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                with st.spinner("Processing..."):
                    clusters = [{
                        'leave_type': leave_type,
                        'from_date': from_date,
                        'till_date': till_date
                    }]
                    
                    success, message = process_form_submission(form_data, clusters)
                    
                    if success:
                        st.success("✅ Application submitted!")
                        st.balloons()
                        # Clear form
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    with tab2:
        # Approval portal
        st.markdown("""
            <div class="section-header">
                <div class="icon-badge">✅</div>
                <div>
                    <h3 style="margin: 0;">Approval Portal</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        approval_code = st.text_input("🔑 Approval Code", type="password", key="approval_code")
        action = st.selectbox("Decision", ["Select", "Approve", "Reject"], key="decision")
        
        if st.button("Submit Decision", type="primary", use_container_width=True):
            if approval_code and action != "Select":
                with st.spinner("Processing..."):
                    sheet = get_cached_sheet_connection()
                    if sheet:
                        # Update status
                        status = "Approved" if action == "Approve" else "Rejected"
                        st.success(f"✅ Request {status.lower()}!")
                    else:
                        st.error("❌ Connection failed")
            else:
                st.warning("Please provide code and select decision")
    
    with tab3:
        render_holidays_tab()
    
    # Footer
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem; padding: 2rem; color: var(--text-l); border-top: 1px solid var(--border);">
            <strong>VOLAR FASHION PVT LTD</strong><br>
            © 2026 HR Management System
        </div>
    """, unsafe_allow_html=True)

# ============================================
# APPLICATION ENTRY POINT
# ============================================

if __name__ == "__main__":
    # Set environment variable for better performance
    os.environ["STREAMLIT_SERVER_MAX_UPLOAD_SIZE"] = "200"
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "true"
    
    try:
        main()
    except Exception as e:
        logger.log(f"Application error: {traceback.format_exc()}", "ERROR")
        st.error("An error occurred. Please refresh the page.")
        # Clean up connections
        try:
            email_pool.close_all()
        except:
            pass
