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
    
    /* Holidays Table Styles - SIMPLIFIED */
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
        border-left: 5px solid #673ab7;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
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
        font-size: 1.2rem;
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
    
    .holiday-day {
        font-size: 1rem;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.3rem 1rem;
        background: rgba(103, 58, 183, 0.1);
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .holiday-name {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .holiday-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
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
    
    /* Simple table layout for compact view */
    .simple-holiday-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #673ab7;
        display: flex;
        align-items: center;
        transition: all 0.3s ease;
    }
    
    .simple-holiday-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(103, 58, 183, 0.1);
    }
    
    .date-badge {
        background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        min-width: 80px;
        text-align: center;
        margin-right: 1rem;
    }
    
    .day-badge {
        background: rgba(33, 150, 243, 0.1);
        color: var(--accent-color);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin-right: 1rem;
    }
    
    .holiday-info {
        flex-grow: 1;
    }
    
    .holiday-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.2rem;
    }
    
    .holiday-subtitle {
        font-size: 0.9rem;
        color: var(--text-secondary);
    }
    
    .cluster-section {
    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    border: 2px solid #3b82f6;
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
}

/* Light mode override */
@media (prefers-color-scheme: light) {
    .cluster-section {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    }
}

.cluster-header h3 {
    color: #ffffff !important;
    margin: 0;
}

.cluster-header p {
    color: #dbeafe !important;
    margin: 5px 0 0 0;
    font-size: 0.95rem;
}

.cluster-badge {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    color: #78350f;
    padding: 0.3rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    margin-left: 10px;
}
    .add-cluster-btn {
        background: linear-gradient(135deg, #38d9a9 0%, #20c997 100%);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        margin: 10px 0;
        transition: all 0.3s;
    }
    
    .add-cluster-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 217, 169, 0.3);
    }
    
    .remove-cluster-btn {
        background: linear-gradient(135deg, #ff6b6b 0%, #fa5252 100%);
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 12px;
        margin-top: 10px;
    }
    
    /* Code badge styles */
    .code-badge {
        background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%);
        color: #856404;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 0.9rem;
        margin: 5px;
        display: inline-block;
        border: 1px solid #ffc107;
    }
    
    .code-display {
        background: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        text-align: center;
        font-size: 1.2rem;
        letter-spacing: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# Superior details dictionary
SUPERIORS = {
    "Jaya Tahilramani":"admin1@volarfashion.in",
    "Sandip Gawankar": "admin1@volarfashion.in",
    "Tariq Patel": "dn1@volarfashion.in",
    "Sarath Kumar": "Sarath@vfemails.com",
    "Rajeev Thakur": "Rajeev@vfemails.com",
    
    "Ayushi Jain": "ayushi@volarfashion.in",
    "Akshaya Shinde": "Akshaya@vfemails.com",
    "Vitika Mehta": "vitika@volarfashion.in",
    
    "Mohammed Tahir": "tahir@vfemails.com",
    
    
    "Hr":"admin1@volarfashion.in",
    
    "Krishna Yadav": "Krishna@vfemails.com",
    "Sarath Kumar": "Sarath@vfemails.com",
    "Manish Gupta": "Manish@vfemails.com",
    "Shantanu Shinde": "s37@vfemails.com"
    
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

# Holidays data - SIMPLIFIED
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
        'cluster_number': 1,
        'leave_type': 'Select Type',
        'from_date': datetime.now().date(),
        'till_date': datetime.now().date(),
        'approval_code': ''
    }]
if 'reset_form_tab1' not in st.session_state:
    st.session_state.reset_form_tab1 = False
if 'reset_form_tab2' not in st.session_state:
    st.session_state.reset_form_tab2 = False
if 'form_data_tab1' not in st.session_state:
    st.session_state.form_data_tab1 = {
        'employee_name': '',
        'employee_email': '',
        'employee_code': '',
        'department': 'Select Department',
        'purpose': '',
        'superior_name': 'Select Manager',
        'is_cluster': False
    }
if 'form_data_tab2' not in st.session_state:
    st.session_state.form_data_tab2 = {
        'approval_password': '',
        'action': 'Select Decision'
    }
if 'cluster_codes' not in st.session_state:
    st.session_state.cluster_codes = {}
if 'show_copy_section' not in st.session_state:
    st.session_state.show_copy_section = False
if 'test_email_result' not in st.session_state:
    st.session_state.test_email_result = None
if 'email_config_status' not in st.session_state:
    st.session_state.email_config_status = "Not Tested"
if 'debug_logs' not in st.session_state:
    st.session_state.debug_logs = []
if 'generated_codes' not in st.session_state:
    st.session_state.generated_codes = set()

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

def get_existing_codes_from_sheet(sheet):
    """Get all existing approval codes from Google Sheets"""
    try:
        if not sheet:
            log_debug("No sheet provided to get existing codes")
            return set()
        
        all_records = sheet.get_all_values()
        existing_codes = set()
        
        for idx, row in enumerate(all_records):
            if idx == 0:  # Skip header
                continue
            if len(row) > 14 and row[14]:  # Column 15 is approval code (0-indexed)
                code = row[14].strip()
                if code and code != "USED":
                    existing_codes.add(code)
        
        log_debug(f"Found {len(existing_codes)} existing codes in sheet")
        return existing_codes
        
    except Exception as e:
        log_debug(f"Error getting existing codes: {str(e)}")
        return set()

def generate_approval_password():
    """Generate a UNIQUE 5-digit alphanumeric password"""
    try:
        # Simple alphabet without confusing characters
        alphabet = string.ascii_uppercase.replace('O', '').replace('I', '').replace('L', '') + '23456789'
        
        # Generate random code
        password = ''.join(secrets.choice(alphabet) for _ in range(5))
        
        log_debug(f"Generated approval password: {password}")
        return password
        
    except Exception as e:
        log_debug(f"Error generating password: {str(e)}")
        # Fallback simple method
        import random
        return str(random.randint(10000, 99999))

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
        
        try:
            # Get the credentials JSON string
            creds_json = st.secrets[secrets_key]
            
            # If it's a string, parse it as JSON
            if isinstance(creds_json, str):
                import json
                creds_dict = json.loads(creds_json)
            else:
                # If it's already a dict
                creds_dict = creds_json
                
        except Exception as e:
            log_debug(f"Error parsing credentials: {str(e)}")
            # Try to access each field individually
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
        
        log_debug(f"Credentials loaded for: {creds_dict.get('client_email', 'Unknown')}")
        return creds_dict
            
    except Exception as e:
        log_debug(f"Error getting Google credentials: {traceback.format_exc()}")
        st.error(f"❌ Error loading credentials: {str(e)}")
        return None

def setup_google_sheets():
    """Setup Google Sheets connection"""
    try:
        log_debug("Setting up Google Sheets connection...")
        
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
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
            st.error(f"❌ Error creating credentials: {str(cred_error)}")
            return None
        
        # Authorize client
        client = gspread.authorize(creds)
        
        # Try to open the sheet
        SHEET_NAME = "Leave_Applications"
        try:
            spreadsheet = client.open(SHEET_NAME)
            sheet = spreadsheet.sheet1
            log_debug(f"Successfully connected to sheet: {SHEET_NAME}")
            
            # Check if sheet has data
            try:
                data = sheet.get_all_values()
                log_debug(f"Sheet has {len(data)} rows")
                
                # If sheet is empty or missing headers, add them
                if len(data) == 0 or not data[0]:
                    headers = [
                        "Submission Date", "Employee Name", "Employee Email", "Employee Code", "Department",
                        "Type of Leave", "No of Days", "Purpose of Leave", "From Date",
                        "Till Date", "Superior Name", "Superior Email", "Status", 
                        "Approval Date", "Approval Password", "Is Cluster Holiday", "Cluster Number"
                    ]
                    sheet.append_row(headers)
                    log_debug("Added headers to empty sheet")
                else:
                    log_debug(f"Headers found: {data[0]}")
                    
            except Exception as e:
                log_debug(f"Error checking sheet data: {str(e)}")
            
            return sheet
            
        except gspread.SpreadsheetNotFound:
            st.error(f"❌ Google Sheet '{SHEET_NAME}' not found!")
            st.info(f"Please create a sheet named '{SHEET_NAME}' in Google Sheets and share it with: {creds_dict.get('client_email', 'service account email')}")
            return None
        except Exception as e:
            st.error(f"❌ Error accessing sheet: {str(e)}")
            log_debug(f"Sheet access error: {traceback.format_exc()}")
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
            "timestamp": datetime.now().strftime("%Y-%m-d %H:%M:%S")
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

def calculate_working_days(from_date, till_date):
    """Calculate total number of days including Sundays"""
    total_days = (till_date - from_date).days + 1
    return total_days

def calculate_days(from_date, till_date, leave_type):
    """Calculate number of days with proper logic"""
    if leave_type == "Half Day":
        return 0.5
    elif leave_type == "Early Exit":
        return ""
    else:
        # For Full Day leave, calculate total days including Sundays
        return calculate_working_days(from_date, till_date)

def send_employee_submission_confirmation(employee_name, employee_email, superior_name, clusters_data):
    """Send confirmation email to employee when they submit leave application"""
    try:
        log_debug(f"Sending submission confirmation to employee: {employee_email}")
        
        # Get email credentials
        sender_email, sender_password, source = get_email_credentials()
        
        if not sender_email or not sender_password:
            log_debug("Email credentials missing for employee confirmation")
            return False
            
        # Check if it's a valid email
        if "@" not in employee_email or "." not in employee_email:
            log_debug(f"Invalid employee email format: {employee_email}")
            return False
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = employee_email
        
        if len(clusters_data) > 1:
            msg['Subject'] = f"Leave Application Submitted: {len(clusters_data)} periods - Reference Submitted"
        else:
            msg['Subject'] = f"Leave Application Submitted - Reference Submitted"
        
        # Build clusters details HTML
        clusters_html = ""
        for i, cluster in enumerate(clusters_data):
            days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
            days_display = "N/A" if cluster['leave_type'] == "Early Exit" else (f"{days} days" if cluster['leave_type'] == "Full Day" else "0.5 day")
            
            clusters_html += f"""
            <div style="background: {'#f8f9ff' if i % 2 == 0 else '#f0f2ff'}; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4dabf7;">
                <h4 style="margin-top: 0; color: #339af0;">Period {i+1}</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px; width: 40%;"><strong>Leave Type:</strong></td>
                        <td style="padding: 5px;">{cluster['leave_type']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>From Date:</strong></td>
                        <td style="padding: 5px;">{cluster['from_date'].strftime('%Y-%m-%d')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Till Date:</strong></td>
                        <td style="padding: 5px;">{cluster['till_date'].strftime('%Y-%m-%d')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Duration:</strong></td>
                        <td style="padding: 5px;">{days_display}</td>
                    </tr>
                </table>
            </div>
            """
        
        # HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
                .status-box {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2196f3; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">Leave Application Submitted</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p>
                </div>
                
                <p>Dear {employee_name},</p>
                
                <div class="info-box">
                    <h3 style="margin-top: 0; color: #673ab7;">Application Received</h3>
                    <p>Your leave application has been successfully submitted and is now pending approval.</p>
                    <p><strong>Submitted To:</strong> {superior_name}</p>
                    <p><strong>Submission Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <h3 style="color: #339af0;">Leave Periods Details</h3>
                {clusters_html}
                
                <div class="status-box">
                    <h4 style="margin-top: 0; color: #1976d2;">📋 Application Status</h4>
                    <p>Your application is currently <strong>Pending</strong>.</p>
                    <p>Your manager <strong>{superior_name}</strong> will review your request and you will receive another email once a decision is made.</p>
                </div>
                
                <div class="footer">
                    VOLAR FASHION PVT LTD - HR Department<br>
                    📧 hrvolarfashion@gmail.com<br>
                    This is an automated message.
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Create SMTP connection
        log_debug(f"Creating SMTP connection for employee confirmation to {employee_email}")
        server, method = create_smtp_connection(sender_email, sender_password)
        
        if server:
            try:
                log_debug(f"Sending employee confirmation via {method}...")
                server.sendmail(sender_email, employee_email, msg.as_string())
                server.quit()
                log_debug(f"✓ Employee confirmation sent to {employee_email}")
                return True
            except Exception as e:
                server.quit()
                error_msg = str(e)
                log_debug(f"Failed to send employee confirmation: {error_msg}")
                return False
        else:
            log_debug(f"Could not establish SMTP connection for employee confirmation")
            return False
            
    except Exception as e:
        error_msg = str(e)
        log_debug(f"Error in send_employee_submission_confirmation: {traceback.format_exc()}")
        return False

def send_approval_email(employee_name, superior_name, superior_email, clusters_data, cluster_codes):
    """Send approval request email to superior with separate codes for each cluster"""
    try:
        log_debug(f"Preparing to send approval email to {superior_email}")
        
        # Get email credentials
        sender_email, sender_password, source = get_email_credentials()
        
        if not sender_email or not sender_password:
            log_debug("Email credentials missing for approval email")
            return False
            
        # Check if it's a valid email
        if "@" not in superior_email or "." not in superior_email:
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
        
        if len(clusters_data) > 1:
            msg['Subject'] = f"CLUSTER LEAVE: {employee_name} - {len(clusters_data)} periods"
        else:
            msg['Subject'] = f"Leave Approval Required: {employee_name}"
        
        # Build clusters details HTML
        clusters_html = ""
        for i, cluster in enumerate(clusters_data):
            days = calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type'])
            days_display = "N/A" if cluster['leave_type'] == "Early Exit" else (f"{days} days" if cluster['leave_type'] == "Full Day" else "0.5 day")
            
            clusters_html += f"""
            <div style="background: {'#f8f9ff' if i % 2 == 0 else '#f0f2ff'}; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4dabf7;">
                <h4 style="margin-top: 0; color: #339af0;">Period {i+1}</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px; width: 40%;"><strong>Leave Type:</strong></td>
                        <td style="padding: 5px;">{cluster['leave_type']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>From Date:</strong></td>
                        <td style="padding: 5px;">{cluster['from_date'].strftime('%Y-%m-%d')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Till Date:</strong></td>
                        <td style="padding: 5px;">{cluster['till_date'].strftime('%Y-%m-%d')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Duration:</strong></td>
                        <td style="padding: 5px;">{days_display}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Approval Code:</strong></td>
                        <td style="padding: 5px;">
                            <span style="background: #fff3cd; padding: 5px 10px; border-radius: 4px; font-family: 'Courier New', monospace; font-weight: bold; letter-spacing: 2px;">
                                {cluster_codes.get(i, 'CODE MISSING')}
                            </span>
                        </td>
                    </tr>
                </table>
            </div>
            """
        
        # Simple HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
                .cluster-box {{ background: #e6f0ff; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4dabf7; }}
                .code {{ background: #fff3cd; padding: 10px 15px; border-radius: 6px; font-family: 'Courier New', monospace; font-weight: bold; letter-spacing: 2px; display: inline-block; margin: 5px; border: 1px solid #ffc107; }}
                .instructions {{ background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">Leave Approval Required</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p>
                </div>
                
                <p>Dear {superior_name},</p>
                
                <div class="info-box">
                    <h3 style="margin-top: 0; color: #673ab7;">Employee Information</h3>
                    <p><strong>Employee Name:</strong> {employee_name}</p>
                    <p><strong>Employee Code:</strong> {clusters_data[0].get('employee_code', 'N/A')}</p>
                    <p><strong>Department:</strong> {clusters_data[0].get('department', 'N/A')}</p>
                    <p><strong>Total Periods:</strong> {len(clusters_data)}</p>
                    <p><strong>Purpose:</strong> {clusters_data[0].get('purpose', 'N/A')}</p>
                </div>
                
                <h3 style="color: #339af0;">Leave Periods Details</h3>
                {clusters_html}
                
                <div class="instructions">
                    <h4 style="margin-top: 0; color: #2e7d32;">📋 How to Approve/Reject:</h4>
                    <ol>
                        <li>Visit: <a href="{app_url}">{app_url}</a></li>
                        <li>Click on "✅ Approval Portal" tab</li>
                        <li><strong>For each period:</strong> Enter the specific approval code mentioned above</li>
                        <li>Select Approve or Reject for that period</li>
                        <li>Click Submit Decision</li>
                        <li><strong>Repeat</strong> for each period with its specific code</li>
                    </ol>
                    <p><strong>Note:</strong> Each code can only be used once for its specific period.</p>
                </div>
                
                <div class="footer">
                    VOLAR FASHION PVT LTD - HR Department<br>
                    📧 hrvolarfashion@gmail.com<br>
                    This is an automated message.
                </div>
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
                return False
        else:
            log_debug(f"Could not establish SMTP connection for approval email")
            return False
            
    except Exception as e:
        error_msg = str(e)
        log_debug(f"Error in send_approval_email: {traceback.format_exc()}")
        return False

def send_superior_decision_confirmation(superior_name, superior_email, employee_name, cluster_index, status, approval_code):
    """Send confirmation email to superior when they approve/reject leave"""
    try:
        log_debug(f"Sending decision confirmation to superior: {superior_email}")
        
        # Get email credentials
        sender_email, sender_password, source = get_email_credentials()
        
        if not sender_email or not sender_password:
            log_debug("Email credentials missing for superior confirmation")
            return False
            
        # Check if it's a valid email
        if "@" not in superior_email or "." not in superior_email:
            log_debug(f"Invalid superior email format: {superior_email}")
            return False
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = superior_email
        
        status_text = "Approved" if status == "Approved" else "Rejected"
        status_color = "#28a745" if status == "Approved" else "#dc3545"
        status_bg = "#d4edda" if status == "Approved" else "#f8d7da"
        
        msg['Subject'] = f"Leave {status_text}: {employee_name} - Period {cluster_index}"
        
        # HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .status-box {{ background: {status_bg}; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid {status_color}; }}
                .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">Leave Decision Recorded</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p>
                </div>
                
                <p>Dear {superior_name},</p>
                
                <div class="status-box">
                    <h3 style="margin-top: 0; color: {status_color};">
                        {'✅ Approved' if status == 'Approved' else '❌ Rejected'}
                    </h3>
                    <p>You have successfully <strong>{status_text.lower()}</strong> the leave request.</p>
                </div>
                
                <div class="info-box">
                    <h4 style="margin-top: 0; color: #673ab7;">Decision Details</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; width: 40%;"><strong>Employee:</strong></td>
                            <td style="padding: 8px;">{employee_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Period:</strong></td>
                            <td style="padding: 8px;">{cluster_index}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Approval Code:</strong></td>
                            <td style="padding: 8px;">
                                <span style="background: #fff3cd; padding: 5px 10px; border-radius: 4px; font-family: 'Courier New', monospace; font-weight: bold;">
                                    {approval_code}
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Decision Time:</strong></td>
                            <td style="padding: 8px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Status:</strong></td>
                            <td style="padding: 8px;">
                                <span style="background: {status_bg}; color: {status_color}; padding: 4px 12px; border-radius: 20px; font-weight: bold;">
                                    {status_text.upper()}
                                </span>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <p><strong>Note:</strong> The employee has been notified of your decision via email.</p>
                
                <div class="footer">
                    VOLAR FASHION PVT LTD - HR Department<br>
                    📧 hrvolarfashion@gmail.com<br>
                    This is an automated message.
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Create SMTP connection
        log_debug(f"Creating SMTP connection for superior confirmation to {superior_email}")
        server, method = create_smtp_connection(sender_email, sender_password)
        
        if server:
            try:
                log_debug(f"Sending superior confirmation via {method}...")
                server.sendmail(sender_email, superior_email, msg.as_string())
                server.quit()
                log_debug(f"✓ Superior confirmation sent to {superior_email}")
                return True
            except Exception as e:
                server.quit()
                error_msg = str(e)
                log_debug(f"Failed to send superior confirmation: {error_msg}")
                return False
        else:
            log_debug(f"Could not establish SMTP connection for superior confirmation")
            return False
            
    except Exception as e:
        error_msg = str(e)
        log_debug(f"Error in send_superior_decision_confirmation: {traceback.format_exc()}")
        return False

def send_employee_decision_notification(employee_name, employee_email, superior_name, cluster_index, status, cluster_data):
    """Send notification email to employee when their leave is approved/rejected"""
    try:
        log_debug(f"Sending decision notification to employee: {employee_email}")
        
        # Get email credentials
        sender_email, sender_password, source = get_email_credentials()
        
        if not sender_email or not sender_password:
            log_debug("Email credentials missing for employee notification")
            return False
            
        # Check if it's a valid email
        if "@" not in employee_email or "." not in employee_email:
            log_debug(f"Invalid employee email format: {employee_email}")
            return False
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr(("VOLAR FASHION HR", sender_email))
        msg['To'] = employee_email
        
        status_text = "Approved" if status == "Approved" else "Rejected"
        status_color = "#28a745" if status == "Approved" else "#dc3545"
        status_bg = "#d4edda" if status == "Approved" else "#f8d7da"
        status_icon = "✅" if status == "Approved" else "❌"
        
        if 'is_cluster' in cluster_data and cluster_data['is_cluster']:
            msg['Subject'] = f"Leave {status_text}: Period {cluster_index} - {status_text}"
        else:
            msg['Subject'] = f"Leave {status_text}: Your request has been {status_text}"
        
        days = calculate_days(cluster_data['from_date'], cluster_data['till_date'], cluster_data['leave_type'])
        days_display = "N/A" if cluster_data['leave_type'] == "Early Exit" else (f"{days} days" if cluster_data['leave_type'] == "Full Day" else "0.5 day")
        
        # HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .status-box {{ background: {status_bg}; padding: 30px; border-radius: 10px; margin: 20px 0; border-left: 4px solid {status_color}; text-align: center; }}
                .info-box {{ background: #f8f9ff; padding: 20px; border-radius: 10px; margin: 20px 0; border: 1px solid #e2e8f0; }}
                .details-box {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #2196f3; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">Leave Request Update</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">VOLAR FASHION HR System</p>
                </div>
                
                <p>Dear {employee_name},</p>
                
                <div class="status-box">
                    <div style="font-size: 48px; margin-bottom: 15px;">{status_icon}</div>
                    <h2 style="margin: 0; color: {status_color};">{status_text.upper()}</h2>
                    <p style="font-size: 18px; margin-top: 10px;">
                        Your leave request has been <strong>{status_text.lower()}</strong> by {superior_name}.
                    </p>
                </div>
                
                <div class="info-box">
                    <h4 style="margin-top: 0; color: #673ab7;">Decision Summary</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; width: 40%;"><strong>Approved By:</strong></td>
                            <td style="padding: 8px;">{superior_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Decision Time:</strong></td>
                            <td style="padding: 8px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Status:</strong></td>
                            <td style="padding: 8px;">
                                <span style="background: {status_bg}; color: {status_color}; padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 14px;">
                                    {status_text.upper()}
                                </span>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <div class="details-box">
                    <h4 style="margin-top: 0; color: #1976d2;">Leave Details</h4>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; width: 40%;"><strong>Period:</strong></td>
                            <td style="padding: 8px;">{cluster_index}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Leave Type:</strong></td>
                            <td style="padding: 8px;">{cluster_data['leave_type']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>From Date:</strong></td>
                            <td style="padding: 8px;">{cluster_data['from_date']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Till Date:</strong></td>
                            <td style="padding: 8px;">{cluster_data['till_date']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Duration:</strong></td>
                            <td style="padding: 8px;">{days_display}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Purpose:</strong></td>
                            <td style="padding: 8px;">{cluster_data.get('purpose', 'N/A')}</td>
                        </tr>
                    </table>
                </div>
                
                <p>{"You can now proceed with your leave plans as approved." if status == "Approved" else "Please contact your manager if you need to discuss alternative arrangements."}</p>
                
                <div class="footer">
                    VOLAR FASHION PVT LTD - HR Department<br>
                    📧 hrvolarfashion@gmail.com<br>
                    This is an automated message.
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Create SMTP connection
        log_debug(f"Creating SMTP connection for employee notification to {employee_email}")
        server, method = create_smtp_connection(sender_email, sender_password)
        
        if server:
            try:
                log_debug(f"Sending employee notification via {method}...")
                server.sendmail(sender_email, employee_email, msg.as_string())
                server.quit()
                log_debug(f"✓ Employee notification sent to {employee_email}")
                return True
            except Exception as e:
                server.quit()
                error_msg = str(e)
                log_debug(f"Failed to send employee notification: {error_msg}")
                return False
        else:
            log_debug(f"Could not establish SMTP connection for employee notification")
            return False
            
    except Exception as e:
        error_msg = str(e)
        log_debug(f"Error in send_employee_decision_notification: {traceback.format_exc()}")
        return False

def save_to_google_sheets(sheet, row_data):
    """Save data to Google Sheets with error handling"""
    try:
        log_debug(f"Attempting to save row to Google Sheets: {row_data[:5]}...")
        
        # Append the row to the sheet
        sheet.append_row(row_data)
        log_debug(f"Successfully saved row to Google Sheets")
        return True
        
    except Exception as e:
        log_debug(f"Error saving to Google Sheets: {str(e)}")
        log_debug(f"Row data that failed: {row_data}")
        return False

def update_leave_status(sheet, approval_password, status):
    """Update leave status in Google Sheet using only approval password"""
    try:
        log_debug(f"Looking for approval code: {approval_password}")
        
        all_records = sheet.get_all_values()
        log_debug(f"Total records in sheet: {len(all_records)}")
        
        for idx, row in enumerate(all_records):
            if idx == 0:  # Skip header
                continue
            
            if len(row) > 14 and row[14].strip() == approval_password.strip():
                log_debug(f"Found matching code at row {idx + 1}")
                
                # Get employee details for email notification
                employee_name = row[1] if len(row) > 1 else ""  # Column B
                employee_email = row[2] if len(row) > 2 else ""  # Column C - NEW EMAIL FIELD
                superior_name = row[10] if len(row) > 10 else ""  # Column K
                superior_email = row[11] if len(row) > 11 else ""  # Column L
                
                # Get cluster details
                is_cluster = row[15] if len(row) > 15 else "No"  # Column P
                cluster_number = row[16] if len(row) > 16 else "1"  # Column Q
                
                # Get leave details for the email
                leave_details = {
                    'leave_type': row[5] if len(row) > 5 else "",  # Column F
                    'from_date': row[7] if len(row) > 7 else "",  # Column H
                    'till_date': row[8] if len(row) > 8 else "",  # Column I
                    'purpose': row[6] if len(row) > 6 else "",  # Column G
                    'is_cluster': is_cluster
                }
                
                # Update status in sheet
                sheet.update_cell(idx + 1, 13, status)  # Status column (Column M - index 13)
                sheet.update_cell(idx + 1, 14, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Approval date (Column N - index 14)
                sheet.update_cell(idx + 1, 15, "USED")  # Mark password as used (Column O - index 15)
                
                log_debug(f"Updated row {idx + 1} to status: {status}")
                
                # Send email notifications
                if email_config["configured"]:
                    # 1. Send confirmation to superior
                    send_superior_decision_confirmation(
                        superior_name, superior_email, 
                        employee_name, cluster_number, status, approval_password
                    )
                    
                    # 2. Send notification to employee
                    send_employee_decision_notification(
                        employee_name, employee_email,
                        superior_name, cluster_number, status, leave_details
                    )
                
                return True
        
        log_debug("No matching record found for approval code")
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
                try:
                    data = sheet.get_all_values()
                    st.info(f"Rows: {len(data)}")
                    if len(data) > 0:
                        st.info(f"Headers: {data[0]}")
                except:
                    st.info("Could not read sheet data")
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
tab1, tab2, tab3 = st.tabs(["📝 Submit Leave Application", "✅ Approval Portal", "📅 Company Holidays"])

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
                            Email notifications will be sent automatically to managers and employees.
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
            'employee_email': '',
            'employee_code': '',
            'department': 'Select Department',
            'purpose': '',
            'superior_name': 'Select Manager',
            'is_cluster': False
        }
        st.session_state.clusters = [{
            'cluster_number': 1,
            'leave_type': 'Select Type',
            'from_date': datetime.now().date(),
            'till_date': datetime.now().date(),
            'approval_code': ''
        }]
        st.session_state.cluster_codes = {}
        st.session_state.reset_form_tab1 = False
    
    # Two-column layout for basic info
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        employee_name = st.text_input(
            "👤 Full Name",
            value=st.session_state.form_data_tab1['employee_name'],
            placeholder="Enter your full name",
            help="Please enter your complete name as per company records",
            key="employee_name_input"
        )
        employee_email = st.text_input(
            "📧 Email Address",
            value=st.session_state.form_data_tab1['employee_email'],
            placeholder="your.email@company.com",
            help="Your email address for notifications",
            key="employee_email_input"
        )
    
    with col2:
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
    
    # Cluster Holiday Option
    is_cluster = st.checkbox(
        "Is this a Cluster Holiday? (Multiple leave periods)",
        value=st.session_state.form_data_tab1['is_cluster'],
        help="Check this if you need to apply for multiple separate leave periods in one application",
        key="is_cluster_checkbox"
    )
    
    # CLUSTER HOLIDAY SECTION
    if is_cluster:
        st.markdown("""
            <div class="cluster-section">
                <div class="cluster-header">
                    <div class="icon-badge" style="background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%);">📅</div>
                    <div>
                        <h3 style="margin: 0;">Cluster Holiday Periods</h3>
                        <p style="margin: 5px 0 0 0; color: #4dabf7; font-size: 0.95rem;">
                            Add multiple leave periods below (each will have separate approval code)
                        </p>
               
            </div>
        """, unsafe_allow_html=True)
        
        # Display all clusters
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
                
                # Update cluster data
                st.session_state.clusters[i]['leave_type'] = leave_type
            
            with col2:
                # For Half Day and Early Exit, dates must be same
                if leave_type in ["Half Day", "Early Exit"]:
                    date_value = cluster['from_date']
                    selected_date = st.date_input(
                        f"Date - Period {i+1}",
                        value=date_value,
                        min_value=datetime.now().date(),
                        key=f"date_cluster_{i}"
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
                            key=f"from_date_cluster_{i}"
                        )
                        st.session_state.clusters[i]['from_date'] = from_date
                    
                    with col_b:
                        till_date = st.date_input(
                            f"To - Period {i+1}",
                            value=cluster['till_date'],
                            min_value=datetime.now().date(),
                            key=f"till_date_cluster_{i}"
                        )
                        st.session_state.clusters[i]['till_date'] = till_date
            
            with col3:
                # Calculate days for this cluster
                if leave_type != "Select Type":
                    no_of_days = calculate_days(
                        st.session_state.clusters[i]['from_date'],
                        st.session_state.clusters[i]['till_date'],
                        leave_type
                    )
                    
                    if leave_type == "Early Exit":
                        days_display = "N/A"
                    elif leave_type == "Half Day":
                        days_display = "0.5"
                    else:
                        days_display = str(no_of_days)
                    
                    st.markdown(f"""
                        <div style="background: #e3f2fd; padding: 10px; border-radius: 8px; text-align: center;">
                            <div style="font-size: 0.8rem; color: #1976d2;">Days</div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: #0d47a1;">{days_display}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            with col4:
                if total_clusters > 1:
                    if st.button("❌ Remove", key=f"remove_cluster_{i}"):
                        st.session_state.clusters.pop(i)
                        st.rerun()
        
        # Add new cluster button
        if st.button("➕ Add Another Period", key="add_cluster"):
            new_cluster_number = len(st.session_state.clusters) + 1
            st.session_state.clusters.append({
                'cluster_number': new_cluster_number,
                'leave_type': 'Select Type',
                'from_date': datetime.now().date(),
                'till_date': datetime.now().date(),
                'approval_code': ''
            })
            st.rerun()
        
        # Calculate total days for all clusters
        total_days = 0
        for cluster in st.session_state.clusters:
            if cluster['leave_type'] == "Full Day":
                days = calculate_working_days(cluster['from_date'], cluster['till_date'])
                total_days += days
            elif cluster['leave_type'] == "Half Day":
                total_days += 0.5
        
        # Display total days
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4dabf7 0%, #339af0 100%); 
                        color: white; padding: 1rem; border-radius: 12px; text-align: center; margin: 1rem 0;">
                <div style="font-size: 0.9rem;">Total Working Days</div>
                <div style="font-size: 2rem; font-weight: bold;">{total_days}</div>
                <div style="font-size: 0.8rem;">across {len(st.session_state.clusters)} period(s)</div>
            </div>
        """, unsafe_allow_html=True)
    
    else:
        # SINGLE HOLIDAY SECTION (Non-cluster)
        st.markdown("""
            <div style="margin-top: 2rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">📅</div>
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
                "📋 Leave Type",
                ["Select Type", "Full Day", "Half Day", "Early Exit"],
                index=0,
                help="Select the type of leave you are requesting",
                key="leave_type_single"
            )
        
        with col2:
            if leave_type in ["Half Day", "Early Exit"]:
                # For Half Day and Early Exit, only one date
                date_value = st.session_state.clusters[0]['from_date']
                selected_date = st.date_input(
                    "📅 Date",
                    value=date_value,
                    min_value=datetime.now().date(),
                    help="Select the date for your leave",
                    key="date_single"
                )
                from_date = selected_date
                till_date = selected_date
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    from_date_value = st.session_state.clusters[0]['from_date']
                    from_date = st.date_input(
                        "📅 Start Date",
                        value=from_date_value,
                        min_value=datetime.now().date(),
                        help="Select the first day of your leave",
                        key="from_date_single"
                    )
                
                with col_b:
                    till_date_value = st.session_state.clusters[0]['till_date']
                    till_date = st.date_input(
                        "📅 End Date",
                        value=till_date_value,
                        min_value=datetime.now().date(),
                        help="Select the last day of your leave",
                        key="till_date_single"
                    )
        
        # Update session state for single holiday
        st.session_state.clusters[0]['leave_type'] = leave_type
        st.session_state.clusters[0]['from_date'] = from_date
        st.session_state.clusters[0]['till_date'] = till_date
        
        # Calculate and display days
        if leave_type != "Select Type":
            no_of_days = calculate_days(from_date, till_date, leave_type)
            
            if leave_type == "Early Exit":
                st.markdown(f"""
                    <div class="thumbsup-box floating-element">
                        <div class="thumbsup-emoji">👍</div>
                        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">Early Exit Request</div>
                        <div style="font-size: 0.95rem;">
                            You're requesting to leave early from work today. Only 2 Early Leaves are Permitted per month.
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            elif leave_type == "Half Day":
                st.markdown(f"""
                    <div class="metric-card floating-element">
                        <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500;">Leave Duration</div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a; margin: 10px 0;">
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
                        <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500;">Leave Duration</div>
                        <div style="font-size: 2.5rem; font-weight: 700; color: #553c9a; margin: 10px 0;">
                            {no_of_days}
                        </div>
                        <div style="font-size: 0.9rem; color: #805ad5;">
                            working days
                        </div>
                     
                    </div>
                """, unsafe_allow_html=True)
    
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
            # VALIDATION CHECKS
            validation_passed = True
            error_messages = []
            
            # Check basic required fields including email
            if not all([employee_name, employee_email, employee_code, department != "Select Department", 
                        purpose, superior_name != "Select Manager"]):
                validation_passed = False
                error_messages.append("Please complete all required fields")
            
            # Validate email format
            if employee_email and "@" not in employee_email:
                validation_passed = False
                error_messages.append("Please enter a valid email address")
            
            # Validate clusters
            for i, cluster in enumerate(st.session_state.clusters):
                if cluster['leave_type'] == "Select Type":
                    validation_passed = False
                    error_messages.append(f"Please select leave type for Period {i+1}")
                    break
                
                # Check date validity for Full Day
                if cluster['leave_type'] == "Full Day":
                    if cluster['from_date'] > cluster['till_date']:
                        validation_passed = False
                        error_messages.append(f"End date must be after or equal to start date for Period {i+1}")
                        break
            
            if not validation_passed:
                error_html = "<div class='error-message'><div style='display: flex; align-items: center; justify-content: center;'><div style='font-size: 1.5rem; margin-right: 10px;'>⚠️</div><div><strong>Validation Error</strong><br>"
                for error in error_messages:
                    error_html += f"{error}<br>"
                error_html += "</div></div></div>"
                st.markdown(error_html, unsafe_allow_html=True)
            else:
                with st.spinner('Submitting your application...'):
                    # Prepare data
                    submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    superior_email = SUPERIORS[superior_name]
                    
                    # Connect to Google Sheets
                    sheet = setup_google_sheets()
                    
                    if sheet:
                        try:
                            # Generate unique codes for each cluster
                            cluster_codes = {}
                            submission_success = True
                            submission_errors = []
                            
                            # Submit each cluster as separate row
                            for i, cluster in enumerate(st.session_state.clusters):
                                # Generate code
                                code = generate_approval_password()
                                cluster_codes[i] = code
                                log_debug(f"Generated code for period {i+1}: {code}")
                                
                                # Prepare leave details
                                leave_details = {
                                    "employee_name": employee_name,
                                    "employee_email": employee_email,
                                    "employee_code": employee_code,
                                    "department": department,
                                    "leave_type": cluster['leave_type'],
                                    "no_of_days": calculate_days(cluster['from_date'], cluster['till_date'], cluster['leave_type']),
                                    "purpose": purpose,
                                    "from_date": cluster['from_date'].strftime("%Y-%m-%d"),
                                    "till_date": cluster['till_date'].strftime("%Y-%m-%d")
                                }
                                
                                # Prepare row data
                                row_data = [
                                    submission_date,
                                    employee_name,
                                    employee_email,  # NEW: Employee email
                                    employee_code,
                                    department,
                                    cluster['leave_type'],
                                    str(leave_details['no_of_days']),
                                    purpose,
                                    leave_details['from_date'],
                                    leave_details['till_date'],
                                    superior_name,
                                    superior_email,
                                    "Pending",  # Status
                                    "",  # Approval Date (empty initially)
                                    code,  # Approval code
                                    "Yes" if is_cluster else "No",  # Is Cluster
                                    str(i+1) if is_cluster else "1"  # Cluster number
                                ]
                                
                                # Write to Google Sheets
                                success = save_to_google_sheets(sheet, row_data)
                                if not success:
                                    submission_success = False
                                    submission_errors.append(f"Failed to save period {i+1}")
                                else:
                                    log_debug(f"Successfully saved period {i+1} with code: {code}")
                            
                            if not submission_success:
                                st.markdown(f'''
                                    <div class="error-message">
                                        <div style="display: flex; align-items: center; justify-content: center;">
                                            <div style="font-size: 1.5rem; margin-right: 10px;">❌</div>
                                            <div>
                                                <strong>Submission Error</strong><br>
                                                Failed to save some periods to database.<br>
                                                Errors: {', '.join(submission_errors)}
                                            </div>
                                        </div>
                                    </div>
                                ''', unsafe_allow_html=True)
                                return
                            
                            # Send email notifications if configuration is working
                            email_operations = []
                            
                            if email_config["configured"]:
                                # 1. Send confirmation to employee
                                try:
                                    # Prepare clusters data for email
                                    clusters_for_email = []
                                    for cluster in st.session_state.clusters:
                                        cluster_copy = cluster.copy()
                                        cluster_copy['employee_code'] = employee_code
                                        cluster_copy['department'] = department
                                        cluster_copy['purpose'] = purpose
                                        clusters_for_email.append(cluster_copy)
                                    
                                    employee_confirmation_sent = send_employee_submission_confirmation(
                                        employee_name,
                                        employee_email,
                                        superior_name,
                                        clusters_for_email
                                    )
                                    email_operations.append(("Employee Confirmation", employee_confirmation_sent))
                                except Exception as e:
                                    log_debug(f"Error sending employee confirmation: {str(e)}")
                                    email_operations.append(("Employee Confirmation", False))
                                
                                # 2. Send approval request to superior
                                try:
                                    superior_email_sent = send_approval_email(
                                        employee_name,
                                        superior_name,
                                        superior_email,
                                        clusters_for_email,
                                        cluster_codes
                                    )
                                    email_operations.append(("Superior Notification", superior_email_sent))
                                except Exception as e:
                                    log_debug(f"Error sending superior notification: {str(e)}")
                                    email_operations.append(("Superior Notification", False))
                            
                            # Check if any email was sent successfully
                            any_email_sent = any(success for _, success in email_operations) if email_operations else False
                            
                            if any_email_sent:
                                # Show success message
                                success_html = '''
                                    <div class="success-message">
                                        <div style="font-size: 3rem; margin-bottom: 1rem;">✨</div>
                                        <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 10px; color: #166534;">
                                            Application Submitted Successfully!
                                        </div>
                                        <div style="color: #155724; margin-bottom: 15px;">
                                            Your leave request has been submitted and notifications have been sent.
                                        </div>
                                '''
                                
                                # Add email status details
                                if email_operations:
                                    success_html += '<div style="background: rgba(255,255,255,0.5); padding: 10px; border-radius: 8px; margin: 10px 0;">'
                                    success_html += '<div style="font-size: 0.9rem; color: #0f5132;"><strong>Email Notifications:</strong></div>'
                                    for operation, success in email_operations:
                                        status_icon = "✅" if success else "⚠️"
                                        status_text = "Sent" if success else "Not Sent"
                                        success_html += f'<div style="font-size: 0.85rem; margin: 5px 0;">{status_icon} {operation}: {status_text}</div>'
                                    success_html += '</div>'
                                
                                success_html += '''
                                        <div style="font-size: 0.95rem; color: #0f5132; opacity: 0.9;">
                                            You will receive another email once your manager makes a decision.
                                        </div>
                                    </div>
                                '''
                                
                                st.markdown(success_html, unsafe_allow_html=True)
                                
                                st.balloons()
                                # Clear generated codes for this session
                                st.session_state.generated_codes.clear()
                                # Set flag to reset form on next render
                                st.session_state.reset_form_tab1 = True
                                time.sleep(2)
                                st.rerun()
                            else:
                                # Show manual approval codes section
                                st.session_state.cluster_codes = cluster_codes
                                st.session_state.show_copy_section = True
                                
                                st.markdown(f'''
                                    <div class="info-box">
                                        <div style="display: flex; align-items: flex-start;">
                                            <div style="font-size: 1.5rem; margin-right: 15px; color: #ff9800;">📧</div>
                                            <div>
                                                <strong style="display: block; margin-bottom: 8px; color: #ff9800;">Email Notification Issue</strong>
                                                Your application was saved to the database successfully!<br>
                                                However, we couldn't send the email notifications automatically.<br>
                                                <small>Check your email configuration in the sidebar.</small>
                                            </div>
                                        </div>
                                    </div>
                                ''', unsafe_allow_html=True)
                                
                                # Manual approval codes section
                                st.markdown("---")
                                st.markdown("""
                                    <div style="text-align: center; margin: 2rem 0;">
                                        <div style="font-size: 1.3rem; font-weight: 600; color: #673ab7; margin-bottom: 1rem;">
                                            📋 Manual Approval Process
                                        </div>
                                        <p style="color: #718096; margin-bottom: 1.5rem;">
                                            Please share these approval codes with your manager <strong>{}</strong>:
                                        </p>
                                    </div>
                                """.format(superior_name), unsafe_allow_html=True)
                                
                                # Display all cluster codes
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
                                                        {cluster['from_date'].strftime('%Y-%m-%d')} to {cluster['till_date'].strftime('%Y-%m-%d')} • {cluster['leave_type']} • {days_display}
                                                    </div>
                                                </div>
                                                <div style="text-align: center;">
                                                    <div style="font-size: 0.9rem; color: #6b46c1; font-weight: 500; margin-bottom: 5px;">
                                                        Approval Code
                                                    </div>
                                                    <div style="font-size: 2rem; font-weight: 700; color: #553c9a; 
                                                                letter-spacing: 4px; font-family: 'Courier New', monospace;">
                                                        {code}
                                                    </div>
                                                    <button class="copy-code-btn" onclick="copyToClipboard('{code}')" style="margin-top: 10px;">
                                                        📋 Copy Code
                                                    </button>
                                                </div>
                                            </div>
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
                                            <li><strong>For each period:</strong> Enter the specific approval code mentioned above</li>
                                            <li>Select Approve or Reject for that period</li>
                                            <li>Click Submit Decision</li>
                                            <li><strong>Repeat</strong> for each period with its specific code</li>
                                        </ol>
                                        <p style="color: #2e7d32; font-size: 0.9rem; margin-top: 10px;">
                                            <strong>Note:</strong> Each code can only be used once for its specific period.
                                        </p>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                st.balloons()
                                # Clear generated codes for this session
                                st.session_state.generated_codes.clear()
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
                                    Both you and the employee have been notified via email.
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
    # CLEAN HOLIDAYS TAB WITH PROPER ALIGNMENT
    st.markdown("""
        <div class="section-header">
            <div class="icon-badge" style="background: linear-gradient(135deg, #2196f3 0%, #03a9f4 100%);">📅</div>
            <div>
                <h3 style="margin: 0;">Company Holidays 2026</h3>
              
            
        </div>
    """, unsafe_allow_html=True)
    
    # Holiday count card
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
    
    # Create a DataFrame for the holidays
    holidays_data = []
    for holiday in HOLIDAYS_2026:
        day_month = holiday["date"].split("-")
        date_str = f"{day_month[0]} {day_month[1]} 2026"
        holidays_data.append({
            "📅 Date": date_str,
            "📆 Day": holiday["day"],
            "🎉 Holiday": holiday["holiday"]
        })
    
    # Add CSS for table styling and centering
    st.markdown("""
        <style>
        /* Center the table */
        .holidays-table-wrapper {
            display: flex;
            justify-content: center;
            width: 100%;
            margin: 2rem 0;
        }
        
        /* Style for the day badges */
        .day-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .day-saturday {
            background: rgba(33, 150, 243, 0.1);
            color: #2196f3;
            border: 1px solid rgba(33, 150, 243, 0.2);
        }
        
        .day-sunday {
            background: rgba(244, 67, 54, 0.1);
            color: #f44336;
            border: 1px solid rgba(244, 67, 54, 0.2);
        }
        
        .day-weekday {
            background: rgba(76, 175, 80, 0.1);
            color: #4caf50;
            border: 1px solid rgba(76, 175, 80, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create the dataframe
    df = pd.DataFrame(holidays_data)
    
    # Function to apply day badge styling
    def style_day(val):
        if val == "Saturday":
            return f'<span class="day-badge day-saturday">{val}</span>'
        elif val == "Sunday":
            return f'<span class="day-badge day-sunday">{val}</span>'
        else:
            return f'<span class="day-badge day-weekday">{val}</span>'
    
    # Apply styling to the Day column
    df["📆 Day"] = df["📆 Day"].apply(style_day)
    
    # Convert dataframe to HTML with styling
    html_table = df.to_html(escape=False, index=False)
    
    # Wrap the table in a centered container
    centered_table = f"""
    <div class="holidays-table-wrapper">
        {html_table}
    </div>
    """
    
    # Apply additional CSS to the table
    st.markdown("""
        <style>
        /* Style the actual table */
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
        
        .holidays-table-wrapper tr:last-child td {
            border-bottom: none;
        }
        
        .holidays-table-wrapper tr:nth-child(even) {
            background-color: rgba(103, 58, 183, 0.05);
        }
        
        .holidays-table-wrapper tr:hover {
            background-color: rgba(103, 58, 183, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display the centered table
    st.markdown(centered_table, unsafe_allow_html=True)
    

# Footer
st.markdown("""
    <div class="footer">
        <div style="margin-bottom: 1rem;">
            <strong style="color: #673ab7;">VOLAR FASHION PVT LTD</strong><br>
            Human Resources Management System
        </div>
        <div style="font-size: 0.9rem;">
            📧 hrvolarfashion@gmail.com<br>
            © 2026 VOLAR FASHION.
        </div>
    </div>
""", unsafe_allow_html=True)
