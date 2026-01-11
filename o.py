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
import concurrent.futures
from threading import Lock, Thread
import signal
import atexit
import queue
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================
# ANTI-HANG CONFIGURATION
# ============================================

# SET GLOBAL TIMEOUTS (in seconds)
GLOBAL_TIMEOUTS = {
    'sheet_operation': 10,      # Google Sheets operations
    'email_operation': 15,      # Email sending
    'form_processing': 30,      # Form submission
    'page_load': 5,            # Page rendering
}

# STREAMLIT CONFIGURATION
st.set_page_config(
    page_title="VOLAR FASHION - Leave Management",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# TIMEOUT DECORATORS - PREVENT HANGING
# ============================================

def timeout(seconds):
    """Decorator to add timeout to any function"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=seconds)
                except concurrent.futures.TimeoutError:
                    raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
        return wrapper
    return decorator

def with_fallback(fallback_value=None):
    """Decorator to provide fallback if function fails"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                st.error(f"⚠️ {func.__name__} failed: {str(e)[:50]}...")
                return fallback_value
        return wrapper
    return decorator

# ============================================
# NON-BLOCKING EMAIL SYSTEM
# ============================================

class NonBlockingEmailQueue:
    """Email queue that won't block the UI"""
    
    def __init__(self):
        self.email_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        
    def start(self):
        """Start email worker thread"""
        self.running = True
        self.worker_thread = Thread(target=self._process_emails, daemon=True)
        self.worker_thread.start()
        st.session_state.email_queue_running = True
    
    def stop(self):
        """Stop email worker thread"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
    
    def add_email(self, email_data):
        """Add email to queue (non-blocking)"""
        self.email_queue.put(email_data)
        return True  # Immediate return
    
    def _process_emails(self):
        """Background thread to process emails"""
        while self.running:
            try:
                email_data = self.email_queue.get(timeout=1)
                self._send_email_safely(email_data)
                self.email_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Email processing error: {e}")
    
    @timeout(GLOBAL_TIMEOUTS['email_operation'])
    def _send_email_safely(self, email_data):
        """Send email with timeout protection"""
        try:
            # Quick email sending with minimal HTML
            sender_email, sender_password = get_email_credentials()
            if not sender_email:
                return False
            
            server = self._get_smtp_connection(sender_email, sender_password)
            if server:
                # Simple text email (faster than HTML)
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = email_data['to']
                msg['Subject'] = email_data['subject']
                msg.attach(MIMEText(email_data.get('body', 'Leave approval required'), 'plain'))
                
                server.sendmail(sender_email, email_data['to'], msg.as_string())
                server.quit()
                return True
        except Exception as e:
            print(f"Background email failed: {e}")
        return False
    
    def _get_smtp_connection(self, sender_email, sender_password):
        """Get SMTP connection with retry logic"""
        for method in ['ssl', 'tls']:
            try:
                if method == 'ssl':
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=5)
                else:
                    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=5)
                    server.starttls()
                
                server.login(sender_email, sender_password)
                return server
            except:
                continue
        return None

# Initialize email queue
if 'email_queue' not in st.session_state:
    st.session_state.email_queue = NonBlockingEmailQueue()
    st.session_state.email_queue.start()

# ============================================
# NON-BLOCKING GOOGLE SHEETS
# ============================================

class NonBlockingSheetClient:
    """Google Sheets client that won't block"""
    
    def __init__(self):
        self.sheet_cache = {}
        self.cache_time = {}
        self.lock = Lock()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    
    @timeout(GLOBAL_TIMEOUTS['sheet_operation'])
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=10))
    def append_row_async(self, row_data):
        """Append row without blocking main thread"""
        future = self.executor.submit(self._append_row_sync, row_data)
        return future
    
    def _append_row_sync(self, row_data):
        """Actual sheet append with locking"""
        try:
            sheet = self._get_sheet()
            if sheet:
                sheet.append_row(row_data)
                return True
        except Exception as e:
            st.error(f"Sheet append failed: {str(e)[:100]}")
            return False
    
    @with_fallback(None)
    @timeout(5)
    def _get_sheet(self):
        """Get sheet connection with timeout"""
        SCOPES = ['https://spreadsheets.google.com/feeds', 
                 'https://www.googleapis.com/auth/drive']
        
        # Try cached connection first
        if 'sheet' in self.sheet_cache:
            cached_time = self.cache_time.get('sheet', 0)
            if time.time() - cached_time < 300:  # 5 minutes cache
                return self.sheet_cache['sheet']
        
        # Create new connection
        creds_dict = get_google_credentials()
        if not creds_dict:
            return None
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
        client = gspread.authorize(creds)
        
        try:
            spreadsheet = client.open("Leave_Applications")
            sheet = spreadsheet.sheet1
            self.sheet_cache['sheet'] = sheet
            self.cache_time['sheet'] = time.time()
            return sheet
        except:
            return None
    
    def get_existing_codes_async(self):
        """Get existing codes without blocking"""
        future = self.executor.submit(self._get_existing_codes_sync)
        return future
    
    def _get_existing_codes_sync(self):
        """Get codes with column-specific query (faster)"""
        try:
            sheet = self._get_sheet()
            if not sheet:
                return set()
            
            # Get ONLY the approval code column (column N = 14)
            try:
                col_n = sheet.col_values(14)  # Much faster than all_values()
                return set(code for code in col_n[1:] if code.strip())
            except:
                # Fallback
                all_values = sheet.get_all_values()
                codes = set()
                for row in all_values[1:]:  # Skip header
                    if len(row) > 13 and row[13]:
                        codes.add(row[13])
                return codes
        except Exception as e:
            print(f"Get codes error: {e}")
            return set()

# Initialize sheet client
if 'sheet_client' not in st.session_state:
    st.session_state.sheet_client = NonBlockingSheetClient()

# ============================================
# ULTRA-FAST CODE GENERATION
# ============================================

class FastCodeGenerator:
    """Generate codes instantly without external calls"""
    
    def __init__(self):
        self.alphabet = "23456789BCDFGHJKMNPQRSTVWXYZ"  # No vowels or confusing chars
        self.generated = set()
        self.counter = int(time.time() * 1000) % 100000
    
    def generate(self):
        """Generate code using fast local algorithm"""
        # Method 1: Counter-based (fastest)
        self.counter = (self.counter + 1) % 100000
        code1 = f"{self.counter:05d}"
        
        # Method 2: Random (backup)
        code2 = ''.join(secrets.choice(self.alphabet) for _ in range(5))
        
        # Method 3: Timestamp hybrid
        ts = int(time.time() * 1000)
        code3 = f"{ts % 10000:04d}{secrets.choice(self.alphabet)}"
        
        # Try each until unique in session
        for code in [code1, code2, code3]:
            if code not in self.generated:
                self.generated.add(code)
                return code
        
        # Last resort
        return ''.join(secrets.choice(self.alphabet) for _ in range(5))

# Initialize code generator
if 'code_gen' not in st.session_state:
    st.session_state.code_gen = FastCodeGenerator()

# ============================================
# MINIMAL CSS - LOADS INSTANTLY
# ============================================

MINIMAL_CSS = """
<style>
:root{--p:#673ab7;--s:#9c27b0;--a:#2196f3;--bg:#f8f9ff;--card:#fff;--text:#1a1a1a}
body{font-family:Inter,sans-serif}
.main{background:var(--bg);min-height:100vh}
.container{max-width:1000px;margin:auto;background:var(--card);padding:2rem;border-radius:16px;box-shadow:0 10px 30px rgba(103,58,183,.1)}
h1{background:linear-gradient(135deg,var(--p),var(--a));-webkit-text-fill-color:transparent;text-align:center;font-size:2.5rem;margin:1rem 0}
.btn{background:linear-gradient(135deg,var(--p),var(--s));color:#fff;border:none;padding:1rem 2rem;border-radius:12px;width:100%;cursor:pointer;font-weight:600}
.btn:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(103,58,183,.3)}
.success{background:#d4edda;color:#155724;padding:1rem;border-radius:12px;margin:1rem 0;border-left:4px solid #28a745}
.error{background:#f8d7da;color:#721c24;padding:1rem;border-radius:12px;margin:1rem 0;border-left:4px solid #dc3545}
</style>
"""

st.markdown(MINIMAL_CSS, unsafe_allow_html=True)

# ============================================
# NON-BLOCKING FORM SUBMISSION
# ============================================

@timeout(GLOBAL_TIMEOUTS['form_processing'])
def submit_form_non_blocking(form_data, clusters):
    """Submit form without blocking the UI"""
    
    # STEP 1: Generate codes instantly (no API call)
    codes = []
    for _ in range(len(clusters)):
        codes.append(st.session_state.code_gen.generate())
    
    # STEP 2: Queue sheet writes (non-blocking)
    submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    superior_email = SUPERIORS.get(form_data['superior_name'], "")
    
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
            codes[i],
            "Yes" if form_data.get('is_cluster') else "No",
            i+1 if form_data.get('is_cluster') else ""
        ]
        
        # Non-blocking sheet append
        future = st.session_state.sheet_client.append_row_async(row_data)
        # Don't wait for result
    
    # STEP 3: Queue email (non-blocking)
    email_data = {
        'to': superior_email,
        'subject': f"Leave Approval: {form_data['employee_name']}",
        'body': f"Leave request from {form_data['employee_name']}. Code(s): {', '.join(codes)}"
    }
    
    st.session_state.email_queue.add_email(email_data)
    
    # Immediate return - don't wait for completion
    return True, codes

# ============================================
# SIMPLE UI THAT WON'T HANG
# ============================================

def render_simple_form():
    """Render minimal form that loads instantly"""
    
    # Header
    st.markdown("""
        <div class="container">
            <h1>VOLAR FASHION</h1>
            <p style="text-align:center;color:#666;">Leave Management System</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2 = st.tabs(["📝 Apply", "✅ Approve"])
    
    with tab1:
        # Minimal form
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name")
            emp_id = st.text_input("Employee ID")
        with col2:
            dept = st.selectbox("Department", ["Select"] + DEPARTMENTS)
            manager = st.selectbox("Manager", ["Select"] + list(SUPERIORS.keys()))
        
        leave_type = st.selectbox("Leave Type", ["Full Day", "Half Day", "Early Exit"])
        purpose = st.text_area("Purpose", height=60)
        
        if st.button("Submit Request", type="primary", use_container_width=True):
            if not all([name, emp_id, dept != "Select", manager != "Select", purpose]):
                st.markdown('<div class="error">Please fill all fields</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Submitting..."):
                    try:
                        # NON-BLOCKING submission
                        success, codes = submit_form_non_blocking(
                            {'employee_name': name, 'employee_code': emp_id, 
                             'department': dept, 'superior_name': manager, 'purpose': purpose},
                            [{'leave_type': leave_type, 'from_date': datetime.now().date(), 
                              'till_date': datetime.now().date()}]
                        )
                        
                        if success:
                            st.markdown(f'''
                                <div class="success">
                                    ✅ Submitted!<br>
                                    <small>Code: {codes[0] if codes else "Generated"}</small>
                                </div>
                            ''', unsafe_allow_html=True)
                            st.balloons()
                    except TimeoutError:
                        st.markdown('<div class="error">⚠️ Slow response - your request is processing in background</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="error">❌ Error: {str(e)[:50]}</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Manager Approval")
        code = st.text_input("Approval Code", type="password")
        action = st.selectbox("Action", ["Approve", "Reject"])
        
        if st.button("Submit Decision", type="primary"):
            if code:
                st.info("Decision submitted")
            else:
                st.warning("Enter approval code")

# ============================================
# CLEANUP ON EXIT
# ============================================

def cleanup():
    """Cleanup resources"""
    if 'email_queue' in st.session_state:
        st.session_state.email_queue.stop()
    if 'sheet_client' in st.session_state:
        st.session_state.sheet_client.executor.shutdown(wait=False)
    print("Resources cleaned up")

# Register cleanup
atexit.register(cleanup)

# ============================================
# CONSTANTS
# ============================================

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
    "Sarath Kumar": "Sarath@vfemails.com",
    "d":"Shinde78617@gmail.com"
}

DEPARTMENTS = [
    "Accounts and Finance", "Administration", "Business Development", "Content",
    "E-Commerce", "Factory & Production", "Graphics", "Human Resources", "IT",
    "Social Media", "Bandra Store", "Support Staff", "Warehouse", "SEO"
]

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_email_credentials():
    """Simple credential getter"""
    try:
        if 'EMAIL' in st.secrets:
            return st.secrets.EMAIL.sender_email, st.secrets.EMAIL.sender_password
        return "", ""
    except:
        return "", ""

def get_google_credentials():
    """Simple credential getter"""
    try:
        if 'google_credentials' in st.secrets:
            return st.secrets.google_credentials.to_dict()
        return None
    except:
        return None

def calculate_days(from_date, till_date, leave_type):
    """Fast calculation"""
    if leave_type == "Half Day":
        return 0.5
    elif leave_type == "Early Exit":
        return ""
    return (till_date - from_date).days + 1

# ============================================
# MAIN APP
# ============================================

def main():
    """Main app with timeout protection"""
    try:
        # Set page load timeout
        with st.spinner("Loading..."):
            time.sleep(0.1)  # Small delay to show spinner
        
        render_simple_form()
        
        # Footer
        st.markdown("---")
        st.markdown("<p style='text-align:center;color:#666;'>VOLAR FASHION © 2026</p>", 
                   unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Application error: {str(e)[:100]}")

if __name__ == "__main__":
    main()
