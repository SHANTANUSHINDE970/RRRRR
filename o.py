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

# Page configuration
st.set_page_config(
    page_title="VOLAR FASHION - Leave Management",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Beautiful Elegant CSS with Premium Design - DARK MODE COMPATIBLE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600&display=swap');
    
    /* CSS Variables for Theme Switching */
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
    
    /* Dark Theme Variables */
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
    
    /* Streamlit Dark Mode Override */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: var(--bg-primary) !important;
        }
        
        .main {
            background-color: var(--bg-primary) !important;
        }
        
        /* Ensure form text is visible */
        .stTextInput input,
        .stSelectbox select,
        .stTextArea textarea,
        .stDateInput input,
        .stNumberInput input {
            color: var(--text-primary) !important;
            background-color: var(--input-bg) !important;
            border-color: var(--border-color) !important;
        }
        
        /* Labels should be visible */
        .stTextInput label,
        .stSelectbox label,
        .stTextArea label,
        .stDateInput label,
        .stNumberInput label {
            color: var(--text-secondary) !important;
        }
        
        /* Placeholder text */
        .stTextInput input::placeholder,
        .stSelectbox select::placeholder,
        .stTextArea textarea::placeholder,
        .stDateInput input::placeholder {
            color: var(--text-light) !important;
            opacity: 0.7;
        }
    }
    
    * {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
    }
    
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
        top: 0;
        left: 0;
        right: 0;
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
        bottom: 0;
        left: 0;
        width: 60px;
        height: 3px;
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
    
    /* FORM ELEMENTS - DARK MODE COMPATIBLE */
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
        transition: all 0.3s ease;
    }
    
    .stTextArea>div>div>textarea {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stDateInput>div>div>input {
        color: var(--text-primary) !important;
        background-color: var(--input-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 0.875rem 1rem !important;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    /* Focus states */
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stTextArea>div>div>textarea:focus,
    .stDateInput>div>div>input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 4px rgba(103, 58, 183, 0.1) !important;
        background: var(--card-bg) !important;
        outline: none !important;
    }
    
    /* Labels */
    .stTextInput>div>label,
    .stSelectbox>div>label,
    .stTextArea>div>label,
    .stDateInput>div>label {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
    }
    
    /* Placeholder text for dark mode */
    @media (prefers-color-scheme: dark) {
        .stTextInput input::placeholder,
        .stSelectbox select::placeholder,
        .stTextArea textarea::placeholder,
        .stDateInput input::placeholder {
            color: var(--text-light) !important;
        }
    }
    
    /* Make sure all text elements use CSS variables */
    p, span, div, li {
        color: var(--text-primary);
    }
    
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
        border-left: 4px solid var(--danger-color);
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
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
    }
    
    /* Hide Streamlit branding */
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
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .password-field {
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
        font-weight: 600;
        color: var(--primary-color);
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
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
    }
    
    .glass-effect {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .gradient-text {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
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
        background: var(--bg-tertiary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5e35b1 0%, #8e24aa 100%);
    }
    
    .confetti {
        position: fixed;
        width: 10px;
        height: 10px;
        background: var(--primary-color);
        opacity: 0;
    }
    
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: var(--bg-secondary);
        color: var(--text-primary);
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
        border: 1px solid var(--border-color);
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
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
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid var(--border-color);
        margin: 1rem 0;
    }
    
    .test-email-input {
        width: 100%;
        padding: 10px;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        margin: 10px 0;
        background: var(--input-bg);
        color: var(--text-primary);
    }
    
    .test-email-btn {
        background: linear-gradient(135deg, var(--accent-color) 0%, #03a9f4 100%);
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
        border-left: 4px solid var(--success-color);
    }
    
    .test-result-error {
        background: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 6px;
        margin: 10px 0;
        border-left: 4px solid var(--danger-color);
    }
    
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
    
    /* Ensure text in all containers is visible */
    div[data-testid="stText"],
    div[data-testid="stMarkdown"] {
        color: var(--text-primary) !important;
    }
    
    /* Sidebar specific styles for dark mode */
    @media (prefers-color-scheme: dark) {
        section[data-testid="stSidebar"] {
            background-color: var(--bg-secondary) !important;
        }
        
        section[data-testid="stSidebar"] * {
            color: var(--text-primary) !important;
        }
        
        section[data-testid="stSidebar"] .stTextInput input,
        section[data-testid="stSidebar"] .stButton button {
            color: var(--text-primary) !important;
            background-color: var(--input-bg) !important;
        }
    }
    
    /* Form reset animation */
    .form-reset {
        animation: fadeOut 0.5s ease forwards;
    }
    
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-20px); }
    }
    
    /* Holidays Table Styles */
    .holidays-table-container {
        background: var(--card-bg);
        border-radius: 24px;
        padding: 2.5rem;
        box-shadow: 0 20px 60px var(--shadow-color);
        border: 1px solid rgba(103, 58, 183, 0.1);
        margin: 2rem auto;
        max-width: 1000px;
    }
    
    .holidays-table-container:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #673ab7, #2196f3);
        border-radius: 24px 24px 0 0;
    }
    
    .holiday-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--bg-tertiary) 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid;
        border-color: var(--primary-color);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .holiday-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(103, 58, 183, 0.15);
    }
    
    .holiday-card:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 100%;
        background: linear-gradient(135deg, rgba(103, 58, 183, 0.05) 0%, rgba(33, 150, 243, 0.05) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .holiday-card:hover:before {
        opacity: 1;
    }
    
    .holiday-date {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
    }
    
    .holiday-date:before {
        content: '📅';
        margin-right: 10px;
        font-size: 1.2rem;
    }
    
    .holiday-name {
        font-size: 1.6rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .holiday-day {
        font-size: 1rem;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.3rem 1rem;
        background: linear-gradient(135deg, var(--accent-color) 0%, #03a9f4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .calendar-icon {
        width: 50px;
        height: 50px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        margin-right: 1.5rem;
        flex-shrink: 0;
    }
    
    .holiday-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .holiday-badge {
        background: linear-gradient(135deg, #673ab7 0%, #2196f3 100%);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    .holiday-count {
        text-align: center;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        margin: 2rem 0;
    }
    
    .holiday-legend {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        color: var(--text-secondary);
    }
    
    .legend-color {
        width: 15px;
        height: 15px;
        border-radius: 4px;
    }
    
    .public-holiday {
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
    }
    
    .religious-holiday {
        background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);
    }
    
    .national-holiday {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
    }
    
    .seasonal-holiday {
        background: linear-gradient(135deg, #ff9800 0%, #ff5722 100%);
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .holiday-grid {
            grid-template-columns: 1fr;
        }
        
        .holiday-card {
            padding: 1.2rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Superior details dictionary
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
    
}

# Department options
DEPARTMENTS = [
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

# Holidays data
HOLIDAYS_2025 = [
    {"date": "01-Jan", "day": "Thursday", "holiday": "New Year", "type": "national"},
    {"date": "26-Jan", "day": "Monday", "holiday": "Republic Day", "type": "national"},
    {"date": "04-Mar", "day": "Wednesday", "holiday": "Holi", "type": "religious"},
    {"date": "20-Mar", "day": "Friday", "holiday": "Ramzan Eid", "type": "religious"},
    {"date": "01-May", "day": "Friday", "holiday": "Maharashtra Day", "type": "regional"},
    {"date": "15-Aug", "day": "Saturday", "holiday": "Independence Day", "type": "national"},
    {"date": "14-Sep", "day": "Monday", "holiday": "Ganesh Chaturthi", "type": "religious"},
    {"date": "02-Oct", "day": "Friday", "holiday": "Gandhi Jayanti", "type": "national"},
    {"date": "21-Oct", "day": "Wednesday", "holiday": "Vijaydashmi", "type": "religious"},
    {"date": "08-Nov", "day": "Sunday", "holiday": "Diwali", "type": "religious"},
    {"date": "11-Nov", "day": "Wednesday", "holiday": "Bhai Dooj", "type": "religious"},
    {"date": "25-Dec", "day": "Friday", "holiday": "Christmas", "type": "religious"}
]

# Initialize session state for form reset
if 'reset_form_tab1' not in st.session_state:
    st.session_state.reset_form_tab1 = False
if 'reset_form_tab2' not in st.session_state:
    st.session_state.reset_form_tab2 = False
if 'form_data_tab1' not in st.session_state:
    st.session_state.form_data_tab1 = {
        'employee_name': '',
        'employee_code': '',
        'department': 'Select Department',
        'leave_type': 'Select Type',
        'from_date': datetime.now().date(),
        'till_date': datetime.now().date(),
        'purpose': '',
        'superior_name': 'Select Manager'
    }
if 'form_data_tab2' not in st.session_state:
    st.session_state.form_data_tab2 = {
        'approval_password': '',
        'action': 'Select Decision'
    }
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
    # Print to console for debugging
    print(f"[{level}] {message}")

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
        # Check if secrets exist - try both lowercase and uppercase
        if 'google_credentials' in st.secrets:
            log_debug("Found google_credentials (lowercase) in secrets")
            secrets_key = "google_credentials"
        elif 'GOOGLE_CREDENTIALS' in st.secrets:
            log_debug("Found GOOGLE_CREDENTIALS (uppercase) in secrets")
            secrets_key = "GOOGLE_CREDENTIALS"
        else:
            log_debug("Google credentials not found in secrets")
            st.error("❌ Google credentials not found in Streamlit secrets")
            return None
        
        log_debug(f"Loading Google credentials from {secrets_key}")
        
        # Access each field individually (more reliable in Streamlit Cloud)
        try:
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
        except KeyError as e:
            log_debug(f"Missing key in {secrets_key}: {str(e)}")
            st.error(f"❌ Missing credential field: {str(e)}")
            return None
        
        # Fix private key formatting if needed
        private_key = creds_dict.get("private_key", "")
        if private_key:
            # Check if private key has escaped newlines
            if "\\n" in private_key:
                creds_dict["private_key"] = private_key.replace("\\n", "\n")
                log_debug("Fixed escaped newlines in private key")
            
            # Ensure it has proper BEGIN/END headers
            if not private_key.startswith("-----BEGIN PRIVATE KEY-----"):
                # Try to add headers if missing
                if "MII" in private_key[:50]:  # Looks like base64 encoded key
                    creds_dict["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----"
                    log_debug("Added BEGIN/END headers to private key")
        
        log_debug(f"Credentials loaded for: {creds_dict['client_email']}")
        
        return creds_dict
            
    except Exception as e:
        log_debug(f"Error getting Google credentials: {traceback.format_exc()}")
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
        
        try:
            # Create credentials
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
            log_debug("Successfully created ServiceAccountCredentials")
        except Exception as cred_error:
            log_debug(f"Error creating credentials: {str(cred_error)}")
            raise cred_error
        
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
        log_debug(f"setup_google_sheets error: {traceback.format_exc()}")
        return None

def get_email_credentials():
    """Get email credentials from Streamlit secrets with better error handling"""
    try:
        log_debug("Getting email credentials from secrets...")
        
        # Try different possible secret names
        possible_sections = ['EMAIL', 'email', 'gmail', 'GMAIL']
        sender_email = None
        sender_password = None
        source = ""
        
        for section in possible_sections:
            if section in st.secrets:
                log_debug(f"Found email section: {section}")
                try:
                    sender_email = st.secrets[section].get("sender_email")
                    sender_password = st.secrets[section].get("sender_password")
                    if sender_email and sender_password:
                        source = section
                        break
                except Exception as e:
                    log_debug(f"Error reading {section} section: {str(e)}")
        
        if not sender_email or not sender_password:
            # Check environment variables as fallback
            log_debug("Trying environment variables...")
            sender_email = os.environ.get("EMAIL_SENDER", os.environ.get("SENDER_EMAIL"))
            sender_password = os.environ.get("EMAIL_PASSWORD", os.environ.get("SENDER_PASSWORD"))
            if sender_email and sender_password:
                source = "Environment Variables"
        
        if sender_email and sender_password:
            log_debug(f"Email credentials loaded for: {sender_email}")
            log_debug(f"Password length: {len(sender_password)} characters")
            
            # Log password type for debugging
            if len(sender_password) == 16:
                log_debug("Password appears to be a Gmail App Password (16 chars)")
            elif " " in sender_password:
                log_debug("WARNING: Password contains spaces")
            
            return sender_email, sender_password, source
        else:
            log_debug("Email credentials not found in secrets or environment")
            return "", "", "Not Found"
            
    except Exception as e:
        log_debug(f"Error getting email credentials: {str(e)}")
        return "", "", f"Error: {str(e)}"

def check_email_configuration():
    """Check if email is configured properly"""
    sender_email, sender_password, source = get_email_credentials()
    
    if not sender_email or not sender_password:
        return {
            "configured": False,
            "message": "❌ Email credentials not found",
            "details": f"Please check your Streamlit secrets or environment variables",
            "source": source
        }
    
    # Check if email looks valid
    if "@" not in sender_email or "." not in sender_email:
        return {
            "configured": False,
            "message": "❌ Invalid email format",
            "details": f"Email '{sender_email}' doesn't look valid",
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
        "password_length": len(sender_password),
        "message": f"✅ Email credentials found ({password_type})"
    }
    
def create_smtp_connection(sender_email, sender_password):
    """Create and return SMTP connection with multiple fallback methods"""
    server = None
    connection_method = ""
    error_messages = []
    
    # Method 1: SMTP_SSL (Port 465) - Primary method
    try:
        log_debug("Trying SMTP_SSL on port 465...")
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10, context=context)
        server.login(sender_email, sender_password)
        connection_method = "SMTP_SSL (Port 465)"
        log_debug(f"✓ {connection_method} successful")
        return server, connection_method
    except Exception as e1:
        error_messages.append(f"Port 465 failed: {str(e1)}")
        log_debug(f"Port 465 failed: {str(e1)}")
        if server:
            server.quit()
    
    # Method 2: STARTTLS (Port 587) - Secondary method
    try:
        log_debug("Trying STARTTLS on port 587...")
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(sender_email, sender_password)
        connection_method = "STARTTLS (Port 587)"
        log_debug(f"✓ {connection_method} successful")
        return server, connection_method
    except Exception as e2:
        error_messages.append(f"Port 587 failed: {str(e2)}")
        log_debug(f"Port 587 failed: {str(e2)}")
        if server:
            try:
                server.quit()
            except:
                pass
    
    # Method 3: Alternative ports
    alternative_ports = [25, 2525]
    for port in alternative_ports:
        try:
            log_debug(f"Trying port {port}...")
            if port in [465]:
                server = smtplib.SMTP_SSL('smtp.gmail.com', port, timeout=10)
            else:
                server = smtplib.SMTP('smtp.gmail.com', port, timeout=10)
                server.starttls(context=ssl.create_default_context())
            server.login(sender_email, sender_password)
            connection_method = f"Port {port}"
            log_debug(f"✓ {connection_method} successful")
            return server, connection_method
        except Exception as e:
            error_messages.append(f"Port {port} failed: {str(e)}")
            log_debug(f"Port {port} failed: {str(e)}")
            if server:
                try:
                    server.quit()
                except:
                    pass
    
    log_debug("All SMTP connection methods failed")
    return None, f"All methods failed: {' | '.join(error_messages)}"

def test_email_connection(test_recipient=None):
    """Test email connection by sending a test email"""
    try:
        log_debug("Starting email connection test...")
        sender_email, sender_password, source = get_email_credentials()
        
        if not sender_email or not sender_password:
            result = {
                "success": False,
                "message": "❌ Email credentials not configured",
                "details": "Please check your secrets.toml or environment variables",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            log_debug("Email test failed: No credentials")
            return result
        
        log_debug(f"Sender: {sender_email}")
        log_debug(f"Password source: {source}")
        
        # Use test recipient or sender's email for testing
        recipient = test_recipient or sender_email
        log_debug(f"Recipient: {recipient}")
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
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
        log_debug("Attempting to establish SMTP connection...")
        server, method = create_smtp_connection(sender_email, sender_password)
        
        if server:
            try:
                log_debug(f"Sending test email via {method}...")
                server.sendmail(sender_email, recipient, msg.as_string())
                server.quit()
                result = {
                    "success": True,
                    "message": f"✅ Email sent successfully via {method}",
                    "details": f"Test email sent to {recipient} at {test_time}",
                    "method": method,
                    "sender": sender_email,
                    "timestamp": test_time
                }
                log_debug(f"Test email sent successfully to {recipient}")
                return result
            except Exception as e:
                server.quit()
                error_msg = str(e)
                log_debug(f"Error sending test email: {error_msg}")
                
                # Provide specific guidance based on error
                if "535" in error_msg or "534" in error_msg:
                    troubleshooting = """
                    **Solution for Authentication Error:**
                    1. Go to: https://myaccount.google.com/security
                    2. Enable 2-Step Verification (if not already enabled)
                    3. Go to: https://myaccount.google.com/apppasswords
                    4. Generate an App Password for "Mail"
                    5. Select "Other (Custom name)" and name it "Streamlit App"
                    6. Copy the 16-character App Password
                    7. Update your secrets.toml with this password
                    """
                else:
                    troubleshooting = f"Error details: {error_msg}"
                
                result = {
                    "success": False,
                    "message": "❌ Failed to send email",
                    "details": troubleshooting,
                    "sender": sender_email,
                    "timestamp": test_time
                }
                return result
        else:
            error_details = f"SMTP Connection Failed: {method}"
            log_debug(error_details)
            
            troubleshooting = """
            **Common Solutions:**
            1. Ensure you're using an App Password (not your regular Gmail password)
            2. Enable 2-Step Verification on your Google account
            3. Check if your account has "Less Secure Apps" access enabled
            4. Try generating a new App Password
            5. Check your internet connection
            
            **App Password Creation Steps:**
            1. Visit: https://myaccount.google.com/security
            2. Enable 2-Step Verification
            3. Visit: https://myaccount.google.com/apppasswords
            4. Select "Mail" and "Other (Custom name)"
            5. Name it "VOLAR Streamlit App"
            6. Generate and copy the 16-character password
            """
            
            result = {
                "success": False,
                "message": "❌ SMTP Connection Failed",
                "details": f"{troubleshooting}\n\nError: {method}",
                "sender": sender_email,
                "timestamp": test_time
            }
            return result
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = str(e)
        log_debug(f"SMTP Authentication Error: {error_msg}")
        result = {
            "success": False,
            "message": "❌ SMTP Authentication Failed",
            "details": f"Error: {error_msg}\n\n**Solution:** Use an App Password (16 chars), not your regular password. Enable 2-Step Verification first.",
            "sender": sender_email,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return result
    except socket.timeout as e:
        error_msg = "Connection timeout - check your internet connection"
        log_debug(f"Connection timeout: {str(e)}")
        result = {
            "success": False,
            "message": "❌ Connection Timeout",
            "details": error_msg,
            "sender": sender_email,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return result
    except Exception as e:
        error_msg = str(e)
        log_debug(f"Unexpected error in test_email_connection: {traceback.format_exc()}")
        result = {
            "success": False,
            "message": "❌ Unexpected Error",
            "details": f"Error: {error_msg}",
            "sender": sender_email,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
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
        log_debug(f"Preparing to send approval email to {superior_email}")
        
        # Get email credentials
        sender_email, sender_password, source = get_email_credentials()
        
        if not sender_email or not sender_password:
            st.warning("⚠️ Email credentials not configured")
            log_debug("Email credentials missing")
            return False
            
        # Check if it's a valid email
        if "@" not in superior_email or "." not in superior_email:
            st.warning(f"⚠️ Invalid email format: {superior_email}")
            log_debug(f"Invalid email format: {superior_email}")
            return False
        
        # Get app URL
        try:
            app_url = st.secrets["APP_URL"]
        except:
            app_url = "https://9yq6u8fklhfba8uggnjr7h.streamlit.app/"
        
        log_debug(f"Using app URL: {app_url}")
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = superior_email
        msg['Subject'] = f"Leave Approval Required: {employee_name}"
        
        # Simple HTML email body - USING YOUR PREFERRED EMAIL UI
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
        log_debug(f"Creating SMTP connection for approval email to {superior_email}")
        server, method = create_smtp_connection(sender_email, sender_password)
        
        if server:
            try:
                log_debug(f"Sending approval email via {method}...")
                server.sendmail(sender_email, superior_email, msg.as_string())
                server.quit()
                log_debug(f"✓ Approval email sent to {superior_email} via {method}")
                return True
            except Exception as e:
                server.quit()
                error_msg = str(e)
                log_debug(f"Failed to send approval email: {error_msg}")
                st.error(f"❌ Failed to send email: {error_msg}")
                return False
        else:
            error_msg = f"Could not establish SMTP connection: {method}"
            log_debug(error_msg)
            st.error(f"❌ {error_msg}")
            return False
            
    except Exception as e:
        error_msg = str(e)
        log_debug(f"Error in send_approval_email: {traceback.format_exc()}")
        st.error(f"❌ Email sending error: {error_msg}")
        return False

def update_leave_status(sheet, approval_password, status):
    """Update leave status in Google Sheet using only approval password"""
    try:
        all_records = sheet.get_all_values()
        
        for idx, row in enumerate(all_records):
            if idx == 0:  # Skip header
                continue
            
            if len(row) > 13 and row[13] == approval_password:
                sheet.update_cell(idx + 1, 12, status)  # Status column
                sheet.update_cell(idx + 1, 13, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Approval date
                sheet.update_cell(idx + 1, 14, "USED")  # Mark password as used
                log_debug(f"Updated row {idx + 1} to status: {status}")
                return True
        
        log_debug("No matching record found for approval")
        return False
        
    except Exception as e:
        st.error(f"❌ Error updating status: {str(e)}")
        log_debug(f"Update error: {traceback.format_exc()}")
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
    if 'password_length' in email_config:
        st.sidebar.info(f"**Password Length:** {email_config['password_length']} chars")
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
                st.sidebar.success("✅ Test email sent successfully!")
            else:
                st.session_state.email_config_status = "Failed"
                st.sidebar.error("❌ Test email failed")

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

# Create beautiful tabs - ADDED NEW HOLIDAYS TAB
tab1, tab2, tab3 = st.tabs(["📝 Submit Leave Application", "✅ Approval Portal", "🎉 Company Holidays"])

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
    
    # Reset form if flag is set
    if st.session_state.reset_form_tab1:
        st.session_state.form_data_tab1 = {
            'employee_name': '',
            'employee_code': '',
            'department': 'Select Department',
            'leave_type': 'Select Type',
            'from_date': datetime.now().date(),
            'till_date': datetime.now().date(),
            'purpose': '',
            'superior_name': 'Select Manager'
        }
        st.session_state.reset_form_tab1 = False
    
    # Two-column layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        employee_name = st.text_input(
            "👤 Full Name",
            value=st.session_state.form_data_tab1['employee_name'],
            placeholder="Enter your full name",
            help="Please enter your complete name as per company records",
            key="employee_name_input"
        )
        employee_code = st.text_input(
            "🔢 Employee ID",
            value=st.session_state.form_data_tab1['employee_code'],
            placeholder="e.g., VF-EMP-001",
            help="Your unique employee identification code",
            key="employee_code_input"
        )
        department = st.selectbox(
            "🏛️ Department",
            ["Select Department"] + DEPARTMENTS,
            index=0 if st.session_state.form_data_tab1['department'] == 'Select Department' else DEPARTMENTS.index(st.session_state.form_data_tab1['department']) + 1,
            help="Select your department from the list",
            key="department_select"
        )
    
    with col2:
        leave_type = st.selectbox(
            "📋 Leave Type",
            ["Select Type", "Full Day", "Half Day", "Early Exit"],
            index=0 if st.session_state.form_data_tab1['leave_type'] == 'Select Type' else ["Select Type", "Full Day", "Half Day", "Early Exit"].index(st.session_state.form_data_tab1['leave_type']),
            help="Select the type of leave you are requesting",
            key="leave_type_select"
        )
        
        # Get date values with fallback
        from_date_value = st.session_state.form_data_tab1['from_date']
        if isinstance(from_date_value, str):
            try:
                from_date_value = datetime.strptime(from_date_value, "%Y-%m-%d").date()
            except:
                from_date_value = datetime.now().date()
        
        from_date = st.date_input(
            "📅 Start Date",
            value=from_date_value,
            min_value=datetime.now().date(),
            help="Select the first day of your leave",
            key="from_date_input"
        )
        
        till_date_value = st.session_state.form_data_tab1['till_date']
        if isinstance(till_date_value, str):
            try:
                till_date_value = datetime.strptime(till_date_value, "%Y-%m-%d").date()
            except:
                till_date_value = datetime.now().date()
        
        till_date = st.date_input(
            "📅 End Date",
            value=till_date_value,
            min_value=datetime.now().date(),
            help="Select the last day of your leave",
            key="till_date_input"
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
        value=st.session_state.form_data_tab1['purpose'],
        placeholder="Please provide a clear and detailed explanation for your leave request...",
        height=120,
        help="Be specific about the reason for your leave",
        key="purpose_textarea"
    )
    
    # Manager Selection
    superior_name = st.selectbox(
        "👔 Reporting Manager or Team Leader",
        ["Select Manager"] + list(SUPERIORS.keys()),
        index=0 if st.session_state.form_data_tab1['superior_name'] == 'Select Manager' else list(["Select Manager"] + list(SUPERIORS.keys())).index(st.session_state.form_data_tab1['superior_name']),
        help="Select your direct reporting manager",
        key="superior_select"
    )
    
    # Submit Button with Beautiful Design
    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        submit_button = st.button("🚀 Submit Leave Request", type="primary", use_container_width=True, key="submit_leave_request")
        
        if submit_button:
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
                            log_debug(f"Data written to Google Sheets for {employee_name}")
                            
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
                                    log_debug(f"Email exception: {traceback.format_exc()}")
                            
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
                                # Set flag to reset form on next render
                                st.session_state.reset_form_tab1 = True
                                time.sleep(2)
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
                                            <li>Enter approval code: <strong>{}</strong></li>
                                            <li>Select Approve or Reject</li>
                                            <li>Click Submit Decision</li>
                                        </ol>
                                    </div>
                                """.format(approval_password), unsafe_allow_html=True)
                                
                                st.balloons()
                                # Set flag to reset form on next render
                                st.session_state.reset_form_tab1 = True
                                time.sleep(2)
                                st.rerun()
                                
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
                            log_debug(f"Submission error: {traceback.format_exc()}")
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
                <h3 style="margin: 0;">Manager or Team Leader Approval Portal</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    Securely approve or reject leave requests using the approval code
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
                        Use the unique 5-character approval code sent via email for authentication
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Reset form if flag is set
    if st.session_state.reset_form_tab2:
        st.session_state.form_data_tab2 = {
            'approval_password': '',
            'action': 'Select Decision'
        }
        st.session_state.reset_form_tab2 = False
    
    # Form Fields - ONLY APPROVAL CODE REQUIRED
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        approval_password_input = st.text_input(
            "🔑 Approval Code",
            value=st.session_state.form_data_tab2['approval_password'],
            type="password",
            placeholder="Enter 5-character code",
            help="Enter the unique code from the approval email",
            key="approval_code_input"
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
    
    action_options = ["Select Decision", "✅ Approve", "❌ Reject"]
    action_index = action_options.index(st.session_state.form_data_tab2['action'])
    
    action = st.selectbox(
        "Select Action",
        action_options,
        index=action_index,
        label_visibility="collapsed",
        key="action_select"
    )
    
    # Submit Decision Button
    submit_decision_button = st.button("Submit Decision", type="primary", use_container_width=True, key="submit_decision_button")
    
    if submit_decision_button:
        if not all([approval_password_input, action != "Select Decision"]):
            st.markdown('''
                <div class="error-message">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <div style="font-size: 1.5rem; margin-right: 10px;">⚠️</div>
                        <div>
                            <strong>Missing Information</strong><br>
                            Please enter approval code and select a decision
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
                            Please enter the exact 5-character code from the approval email
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            with st.spinner("Processing your decision..."):
                sheet = setup_google_sheets()
                if sheet:
                    status = "Approved" if action == "✅ Approve" else "Rejected"
                    success = update_leave_status(sheet, approval_password_input, status)
                    
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
                        # Set flag to reset form on next render
                        st.session_state.reset_form_tab2 = True
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
                                        Please check your approval code or contact HR for assistance.
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

with tab3:
    # Holidays Tab - Beautiful Design
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #ff9800 0%, #ff5722 100%);">🎉</div>
            <div>
                <h3 style="margin: 0;">Company Holidays Calendar 2025</h3>
                <p style="margin: 5px 0 0 0; color: #718096; font-size: 0.95rem;">
                    Plan your leaves and vacations with our complete holiday schedule
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Stats Counter
    st.markdown(f"""
        <div style="text-align: center; margin: 3rem 0;">
            <div class="holiday-count">{len(HOLIDAYS_2025)}</div>
            <div style="font-size: 1.2rem; color: #718096; font-weight: 500;">
                Official Holidays in 2025
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Holiday Legend
    st.markdown("""
        <div class="holiday-legend">
            <div class="legend-item">
                <div class="legend-color national-holiday"></div>
                <span>National Holiday</span>
            </div>
            <div class="legend-item">
                <div class="legend-color religious-holiday"></div>
                <span>Religious Holiday</span>
            </div>
            <div class="legend-item">
                <div class="legend-color regional-holiday"></div>
                <span>Regional Holiday</span>
            </div>
            <div class="legend-item">
                <div class="legend-color seasonal-holiday"></div>
                <span>Seasonal Holiday</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Holiday Cards Grid
    st.markdown('<div class="holiday-grid">', unsafe_allow_html=True)
    
    # Get holiday type color mapping
    type_colors = {
        "national": "national-holiday",
        "religious": "religious-holiday", 
        "regional": "regional-holiday",
        "seasonal": "seasonal-holiday"
    }
    
    for holiday in HOLIDAYS_2025:
        # Determine color based on type
        badge_color = type_colors.get(holiday["type"], "national-holiday")
        
        st.markdown(f"""
            <div class="holiday-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div class="calendar-icon">📅</div>
                    <div>
                        <div class="holiday-date">{holiday["date"]}</div>
                        <div class="holiday-day">{holiday["day"]}</div>
                    </div>
                </div>
                <div class="holiday-name">{holiday["holiday"]}</div>
                <div class="holiday-badge {badge_color}">
                    {holiday["type"].title()} Holiday
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Important Notes
    st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                    padding: 2rem; border-radius: 20px; margin-top: 3rem; 
                    border-left: 5px solid #2196f3;">
            <div style="display: flex; align-items: flex-start;">
                <div style="font-size: 2rem; margin-right: 15px; color: #2196f3;">📌</div>
                <div>
                    <h4 style="margin: 0 0 1rem 0; color: #0d47a1;">Important Holiday Guidelines</h4>
                    <ul style="color: #1565c0; margin: 0; padding-left: 20px;">
                        <li>All employees are entitled to paid leave on company holidays</li>
                        <li>Holidays falling on weekends may be compensated as per company policy</li>
                        <li>Emergency services and essential staff schedules may vary</li>
                        <li>Additional regional holidays may be applicable based on location</li>
                        <li>Please plan your personal leave requests accordingly</li>
                    </ul>
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
            📧 hrvolarfashion@gmail.com<br>
            © 2024 VOLAR FASHION.
        </div>
    </div>
""", unsafe_allow_html=True)
