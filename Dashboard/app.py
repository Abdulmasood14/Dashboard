import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime, date, timedelta
import re 
import requests
from io import StringIO
import time

# Page configuration
st.set_page_config(
    page_title="News Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Global styling */
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
        background-attachment: fixed;
    }
    
    /* Main container styling */
    .main .block-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .css-1d391kg .stSelectbox label {
        color: #ffffff !important;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }
    
    /* Enhanced company cards with neon effects */
    .company-card {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.9) 0%, 
            rgba(118, 75, 162, 0.9) 25%,
            rgba(255, 107, 157, 0.9) 50%,
            rgba(64, 224, 208, 0.9) 75%,
            rgba(138, 43, 226, 0.9) 100%);
        border-radius: 25px;
        color: white;
        text-align: center;
        box-shadow: 
            0 20px 40px rgba(102, 126, 234, 0.4),
            0 0 30px rgba(255, 107, 157, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 220px;
        font-size: 28px;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
        position: relative;
        overflow: hidden;
        padding: 60px 20px;
        cursor: pointer;
        border: 2px solid rgba(255, 255, 255, 0.1);
        margin: 15px 0;
        backdrop-filter: blur(10px);
    }
    
    .company-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #ff6b9d, #c471ed, #12c2e9, #c471ed, #ff6b9d);
        border-radius: 25px;
        z-index: -1;
        animation: borderGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes borderGlow {
        0% { opacity: 0.5; transform: scale(1); }
        100% { opacity: 1; transform: scale(1.02); }
    }
    
    .company-card:hover {
        transform: translateY(-20px) scale(1.05) rotateX(5deg);
        box-shadow: 
            0 35px 70px rgba(102, 126, 234, 0.6),
            0 0 50px rgba(255, 107, 157, 0.4),
            0 0 100px rgba(64, 224, 208, 0.2);
        background: linear-gradient(135deg, 
            rgba(118, 75, 162, 1) 0%, 
            rgba(255, 107, 157, 1) 25%,
            rgba(64, 224, 208, 1) 50%,
            rgba(138, 43, 226, 1) 75%,
            rgba(102, 126, 234, 1) 100%);
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.8);
    }
    
    /* Animated header */
    .main-header {
        text-align: center;
        background: linear-gradient(45deg, #667eea, #764ba2, #ff6b9d, #40e0d0);
        background-size: 300% 300%;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s ease-in-out infinite;
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 30px;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        letter-spacing: 2px;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Enhanced section headers */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #ff6b9d 100%);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #667eea, #764ba2, #ff6b9d) 1;
        padding-bottom: 10px;
        margin-top: 30px;
        margin-bottom: 20px;
        font-weight: 700;
        font-size: 1.8rem;
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #ff6b9d);
        border-radius: 2px;
        animation: pulseGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes pulseGlow {
        0% { opacity: 0.6; box-shadow: 0 0 5px rgba(102, 126, 234, 0.3); }
        100% { opacity: 1; box-shadow: 0 0 20px rgba(255, 107, 157, 0.6); }
    }
    
    /* Enhanced status indicators */
    .status-success {
        color: #00ff88;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    .status-warning {
        color: #ffaa00;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 170, 0, 0.5);
    }
    
    .status-error {
        color: #ff4757;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
    }
    
    /* Enhanced calendar section */
    .calendar-section {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.1) 0%, 
            rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .calendar-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(255, 255, 255, 0.1) 50%, 
            transparent 100%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .date-info {
        font-size: 22px;
        background: linear-gradient(45deg, #667eea, #764ba2, #ff6b9d);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        text-align: center;
        margin-bottom: 15px;
        text-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
        letter-spacing: 1px;
    }
    
    /* Enhanced Streamlit buttons */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.9) 0%, 
            rgba(118, 75, 162, 0.9) 25%,
            rgba(255, 107, 157, 0.9) 50%,
            rgba(64, 224, 208, 0.9) 75%,
            rgba(138, 43, 226, 0.9) 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 25px !important;
        color: white !important;
        text-align: center !important;
        box-shadow: 
            0 20px 40px rgba(102, 126, 234, 0.4),
            0 0 30px rgba(255, 107, 157, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-height: 220px !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5) !important;
        width: 100% !important;
        margin: 15px 0 !important;
        backdrop-filter: blur(10px) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]::before {
        content: '' !important;
        position: absolute !important;
        top: -2px !important;
        left: -2px !important;
        right: -2px !important;
        bottom: -2px !important;
        background: linear-gradient(45deg, #ff6b9d, #c471ed, #12c2e9, #c471ed, #ff6b9d) !important;
        border-radius: 25px !important;
        z-index: -1 !important;
        animation: borderGlow 3s ease-in-out infinite alternate !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-20px) scale(1.05) rotateX(5deg) !important;
        box-shadow: 
            0 35px 70px rgba(102, 126, 234, 0.6),
            0 0 50px rgba(255, 107, 157, 0.4),
            0 0 100px rgba(64, 224, 208, 0.2) !important;
        background: linear-gradient(135deg, 
            rgba(118, 75, 162, 1) 0%, 
            rgba(255, 107, 157, 1) 25%,
            rgba(64, 224, 208, 1) 50%,
            rgba(138, 43, 226, 1) 75%,
            rgba(102, 126, 234, 1) 100%) !important;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.8) !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:active {
        transform: translateY(-10px) scale(1.02) !important;
    }
    
    /* Enhanced metrics */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.1) 0%, 
            rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 25px;
        margin: 10px;
        box-shadow: 
            0 15px 35px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.3),
            0 0 30px rgba(102, 126, 234, 0.2);
    }
    
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        color: #00ff88 !important;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.5) !important;
        background: linear-gradient(45deg, #00ff88, #40e0d0, #667eea);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    div[data-testid="metric-container"] [data-testid="metric-label"] {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
        font-size: 1.1rem !important;
    }
    
    /* Enhanced selectbox styling */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.1) 0%, 
            rgba(255, 255, 255, 0.05) 100%) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: white !important;
    }
    
    .stSelectbox label {
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
        font-size: 1.1rem !important;
    }
    
    /* Enhanced date input */
    .stDateInput > div > div > input {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.1) 0%, 
            rgba(255, 255, 255, 0.05) 100%) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: white !important;
    }
    
    .stDateInput label {
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Enhanced text input */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.1) 0%, 
            rgba(255, 255, 255, 0.05) 100%) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 500 !important;
    }
    
    .stTextInput label {
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Enhanced text area */
    .stTextArea textarea {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.1) 0%, 
            rgba(255, 255, 255, 0.05) 100%) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 500 !important;
    }
    
    .stTextArea label {
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Enhanced expandable sections */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.2) 0%, 
            rgba(255, 107, 157, 0.2) 100%) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
    }
    
    .streamlit-expanderContent {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.05) 0%, 
            rgba(255, 255, 255, 0.02) 100%) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 20px !important;
        margin-top: 10px !important;
    }
    
    /* Enhanced warning and info messages */
    .stAlert {
        backdrop-filter: blur(15px) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, 
            rgba(255, 170, 0, 0.2) 0%, 
            rgba(255, 170, 0, 0.1) 100%) !important;
        color: #ffaa00 !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.2) 0%, 
            rgba(102, 126, 234, 0.1) 100%) !important;
        color: #667eea !important;
    }
    
    .stError {
        background: linear-gradient(135deg, 
            rgba(255, 71, 87, 0.2) 0%, 
            rgba(255, 71, 87, 0.1) 100%) !important;
        color: #ff4757 !important;
    }
    
    /* Enhanced download buttons */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #00ff88 0%, #40e0d0 50%, #667eea 100%) !important;
        border: none !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 25px !important;
        box-shadow: 0 10px 25px rgba(0, 255, 136, 0.3) !important;
        transition: all 0.3s ease !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
    }
    
    div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(0, 255, 136, 0.4) !important;
        background: linear-gradient(135deg, #40e0d0 0%, #667eea 50%, #00ff88 100%) !important;
    }
    
    /* Enhanced regular buttons */
    div[data-testid="stButton"] > button:not([kind="primary"]) {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.1) 0%, 
            rgba(255, 255, 255, 0.05) 100%) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 25px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
    }
    
    div[data-testid="stButton"] > button:not([kind="primary"]):hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3) !important;
        background: linear-gradient(135deg, 
            rgba(102, 126, 234, 0.2) 0%, 
            rgba(255, 107, 157, 0.2) 100%) !important;
    }
    
    /* Enhanced markdown content */
    .stMarkdown {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: white !important;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Enhanced JSON display */
    .stJson {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.05) 0%, 
            rgba(255, 255, 255, 0.02) 100%) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 20px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Floating particles effect */
    .particle {
        position: fixed;
        border-radius: 50%;
        pointer-events: none;
        animation: float 6s ease-in-out infinite;
        z-index: -1;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.7; }
        50% { transform: translateY(-20px) rotate(180deg); opacity: 1; }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #ff6b9d 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #ff6b9d 50%, #667eea 100%);
    }
    
    /* Enhanced divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            rgba(102, 126, 234, 0.5) 25%, 
            rgba(255, 107, 157, 0.8) 50%, 
            rgba(64, 224, 208, 0.5) 75%, 
            transparent 100%);
        margin: 30px 0;
        border-radius: 1px;
    }
    
    /* Floating icons effect */
    .floating-icon {
        position: fixed;
        font-size: 20px;
        opacity: 0.1;
        animation: floatIcon 8s linear infinite;
        z-index: -1;
        color: #667eea;
    }
    
    @keyframes floatIcon {
        0% { transform: translateY(100vh) rotate(0deg); }
        100% { transform: translateY(-100px) rotate(360deg); }
    }
</style>

<!-- Add floating particles -->
<div class="particle" style="top: 10%; left: 10%; width: 4px; height: 4px; background: #667eea; animation-delay: 0s;"></div>
<div class="particle" style="top: 20%; left: 80%; width: 6px; height: 6px; background: #ff6b9d; animation-delay: 2s;"></div>
<div class="particle" style="top: 60%; left: 20%; width: 3px; height: 3px; background: #40e0d0; animation-delay: 4s;"></div>
<div class="particle" style="top: 80%; left: 70%; width: 5px; height: 5px; background: #764ba2; animation-delay: 1s;"></div>
<div class="particle" style="top: 40%; left: 90%; width: 4px; height: 4px; background: #c471ed; animation-delay: 3s;"></div>

<!-- Add floating icons -->
<div class="floating-icon" style="left: 5%; animation-delay: 0s;">📊</div>
<div class="floating-icon" style="left: 15%; animation-delay: 2s;">📈</div>
<div class="floating-icon" style="left: 85%; animation-delay: 4s;">📰</div>
<div class="floating-icon" style="left: 95%; animation-delay: 6s;">💼</div>
<div class="floating-icon" style="left: 25%; animation-delay: 1s;">🚀</div>
<div class="floating-icon" style="left: 75%; animation-delay: 5s;">💡</div>

""", unsafe_allow_html=True)

class CompanyDataProcessor:
    def __init__(self, github_repo="Abdulmasood14/news", csv_directory="scraper_csv_outputs"):
        self.github_repo = github_repo
        self.csv_directory = csv_directory
        self.companies_data = {}
        self.available_dates = []
        self.load_available_dates()
    
    def load_available_dates(self):
        """Load available dates by checking local CSV files or predefined list"""
        try:
            # Check if running locally with CSV files
            if os.path.exists(self.csv_directory):
                # Local directory exists, scan for CSV files
                csv_files = glob.glob(os.path.join(self.csv_directory, "*.csv"))
                dates = []
                
                for file_path in csv_files:
                    filename = os.path.basename(file_path)
                    date_from_file = self.extract_date_from_filename(filename)
                    if date_from_file:
                        dates.append(date_from_file)
                
                self.available_dates = sorted(list(set(dates)), reverse=True)
            else:
                # Use predefined recent dates when files are known to exist
                # This should be manually updated with actual available dates
                predefined_dates = [
                    date(2025, 8, 25),  # Today's example
                    date(2025, 8, 24),
                    date(2025, 8, 23),
                    date(2025, 8, 22),
                    date(2025, 8, 21),
                    # Add more dates as files become available
                ]
                self.available_dates = predefined_dates
            
            # Silently load dates without showing status messages
            pass
                
        except Exception as e:
            st.error(f"Error loading dates: {str(e)}")
            self.available_dates = []
    
    def extract_date_from_filename(self, filename):
        """Extract date from CSV filename (format: DD.MM.YYYY.csv)"""
        # Match pattern: DD.MM.YYYY.csv
        date_pattern = r'(\d{2})\.(\d{2})\.(\d{4})\.csv$'
        match = re.search(date_pattern, filename)
        
        if match:
            day, month, year = match.groups()
            try:
                return date(int(year), int(month), int(day))
            except ValueError:
                return None
        
        return None
    
    def load_company_data_for_date(self, selected_date):
        """Load company data for specific date from GitHub using direct URL"""
        if not selected_date:
            return
        
        # Try multiple URL patterns to find the file
        date_str = selected_date.strftime("%d.%m.%Y")
        csv_filename = f"{date_str}.csv"
        
        possible_urls = [
            f"https://raw.githubusercontent.com/{self.github_repo}/main/{self.csv_directory}/{csv_filename}",
            f"https://raw.githubusercontent.com/{self.github_repo}/master/{self.csv_directory}/{csv_filename}",
            f"https://raw.githubusercontent.com/{self.github_repo}/main/{csv_filename}",
            f"https://raw.githubusercontent.com/{self.github_repo}/master/{csv_filename}"
        ]
        
        for github_raw_url in possible_urls:
            try:
                # Download CSV from GitHub
                response = requests.get(github_raw_url, timeout=15)
                if response.status_code == 200 and len(response.content) > 0:
                    # Read CSV content
                    csv_content = StringIO(response.text)
                    df = pd.read_csv(csv_content)
                    
                    # Validate columns
                    required_columns = ['Company_Name', 'Extracted_Links', 'Extracted_Text']
                    if not all(col in df.columns for col in required_columns):
                        continue
                    
                    # Process the data
                    companies_data = {}
                    
                    for index, row in df.iterrows():
                        company_name = str(row['Company_Name']).strip().upper()
                        
                        if company_name and company_name != 'NAN':
                            companies_data[company_name] = {
                                'company_name': company_name,
                                'extracted_links': str(row['Extracted_Links']) if pd.notna(row['Extracted_Links']) else '',
                                'extracted_text': str(row['Extracted_Text']) if pd.notna(row['Extracted_Text']) else '',
                                'file_path': github_raw_url,
                                'extraction_date': selected_date,
                                'row_number': index + 1
                            }
                    
                    self.companies_data = companies_data
                    return
                    
            except Exception as e:
                continue
        
        # If we reach here, none of the URLs worked
        self.companies_data = {}
    
    def get_companies_list(self):
        """Get list of all companies for selected date"""
        return list(self.companies_data.keys())
    
    def get_company_data(self, company_name):
        """Get data for specific company"""
        return self.companies_data.get(company_name)
    
    def get_available_dates(self):
        """Get list of available dates"""
        return self.available_dates
    
    def get_summary_stats(self):
        """Get summary statistics for current data"""
        total_companies = len(self.companies_data)
        
        total_links = 0
        total_text_length = 0
        
        for data in self.companies_data.values():
            # Count links (assuming they're separated by some delimiter)
            links_text = data.get('extracted_links', '')
            if links_text:
                # Count URLs or lines
                total_links += len([line for line in links_text.split('\n') if line.strip()])
            
            # Count text length
            text_content = data.get('extracted_text', '')
            total_text_length += len(text_content)
        
        return {
            'total_companies': total_companies,
            'total_links': total_links,
            'total_text_length': total_text_length
        }

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    
    # Initialize data processor
    processor = CompanyDataProcessor()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Handle button clicks from dashboard
    if st.session_state.get('selected_company'):
        st.session_state.page = "Company Details"
    
    page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Company Details"], 
                               index=0 if st.session_state.page == "Dashboard" else 1)
    
    if page == "Dashboard":
        st.session_state.page = "Dashboard"
        show_dashboard(processor)
    elif page == "Company Details":
        st.session_state.page = "Company Details"
        show_company_details(processor)

def show_dashboard(processor):
    """Display main dashboard with company cards"""
    st.markdown("<h1 class='main-header'>News Dashboard</h1>", unsafe_allow_html=True)
    

    
    # Calendar Section
    st.markdown("<div class='calendar-section'>", unsafe_allow_html=True)
    st.markdown("### Select Date")
    
    available_dates = processor.get_available_dates()
    
    if not available_dates:
        st.warning("No CSV files found in the GitHub repository.")
        st.info("**Troubleshooting Steps:**")
        st.info("1. Make sure your CSV files are uploaded to GitHub")
        st.info("2. Check that files follow naming pattern: DD.MM.YYYY.csv (e.g., 25.08.2025.csv)")
        st.info(f"3. Verify files are in '{processor.csv_directory}' directory or root directory")
        st.info("4. Wait a few minutes after uploading before refreshing")
        
        if st.button("Try Again"):
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Date selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show available dates for selection
        if available_dates:
            # Add a default "Select a date" option
            date_options = ["Select a date..."] + available_dates
            
            # Find current selection index
            if st.session_state.selected_date and st.session_state.selected_date in available_dates:
                current_index = available_dates.index(st.session_state.selected_date) + 1
            else:
                current_index = 0
            
            selected_option = st.selectbox(
                "Available dates:",
                date_options,
                index=current_index,
                format_func=lambda x: x.strftime("%d %B %Y (%A)") if x != "Select a date..." else x,
                key="date_dropdown"
            )
            
            # Update session state only if a real date is selected
            if selected_option != "Select a date...":
                if st.session_state.selected_date != selected_option:
                    st.session_state.selected_date = selected_option
                    st.rerun()
            else:
                if st.session_state.selected_date is not None:
                    st.session_state.selected_date = None
                    st.rerun()
    
    with col2:
        # Calendar picker (alternative selection)
        if available_dates:
            calendar_date = st.date_input(
                "Or pick a date:",
                value=st.session_state.selected_date if st.session_state.selected_date else available_dates[0],
                min_value=min(available_dates) if available_dates else date.today(),
                max_value=max(available_dates) if available_dates else date.today(),
                key="date_picker"
            )
            
            if calendar_date in available_dates:
                if st.session_state.selected_date != calendar_date:
                    st.session_state.selected_date = calendar_date
                    st.rerun()
            elif calendar_date not in available_dates:
                st.warning(f"No data available for {calendar_date.strftime('%d.%m.%Y')}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Load data for selected date and show company cards
    if st.session_state.selected_date:
        processor.load_company_data_for_date(st.session_state.selected_date)
        
        # Show current date info
        st.markdown(f"<div class='date-info'>Showing data for: {st.session_state.selected_date.strftime('%d %B %Y (%A)')}</div>", 
                   unsafe_allow_html=True)
        
        # Get companies data
        companies = processor.get_companies_list()
        
        if not companies:
            st.info(f"No company data found for {st.session_state.selected_date.strftime('%d.%m.%Y')}")
            return
        
        # Show only total companies metric
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.metric("Total Companies", len(companies))
        
        st.markdown("---")
        
        # Company cards
        st.markdown("<h2 class='section-header'>Company Data Cards</h2>", unsafe_allow_html=True)
        
        # Create cards in grid layout (2 columns)
        cols_per_row = 2
        for i in range(0, len(companies), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, company in enumerate(companies[i:i+cols_per_row]):
                with cols[j]:
                    # Create a button with the company name
                    if st.button(
                        company,
                        key=f"card_{company}_{i}_{j}",
                        help=f"Click to view details for {company}",
                        use_container_width=True
                    ):
                        st.session_state.selected_company = company
                        st.rerun()

def show_company_details(processor):
    """Display detailed view for selected company"""
    
    if not st.session_state.selected_date:
        st.error("Please select a date first from the Dashboard")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return
    
    # Load data for current date
    processor.load_company_data_for_date(st.session_state.selected_date)
    
    companies = processor.get_companies_list()
    if not companies:
        st.error("No company data available for selected date")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return
    
    # Company selector
    default_company = st.session_state.get('selected_company', companies[0] if companies else None)
    if default_company not in companies:
        default_company = companies[0]
    
    selected_company = st.selectbox("Select Company", companies, 
                                   index=companies.index(default_company))
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "Dashboard"
        if 'selected_company' in st.session_state:
            del st.session_state.selected_company
        st.rerun()
    
    data = processor.get_company_data(selected_company)
    
    if not data:
        st.error(f"No data found for {selected_company}")
        return
    
    # Company header
    st.markdown(f"<h1 class='main-header'>{selected_company} - Detailed View</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='date-info'>Data from: {st.session_state.selected_date.strftime('%d %B %Y')}</div>", 
               unsafe_allow_html=True)
    
    # Summary information
    st.markdown("<h3 class='section-header'>Summary Information</h3>", unsafe_allow_html=True)
    
    # Center the single metric
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.metric("Company Name", data['company_name'])
    
    # Extracted Links Section
    st.markdown("<h3 class='section-header'>Extracted Links</h3>", unsafe_allow_html=True)
    
    links_text = data.get('extracted_links', '')
    if links_text and links_text.strip() and links_text.lower() != 'nan':
        # Split links by newlines or other separators
        links_list = [link.strip() for link in links_text.split('\n') if link.strip()]
        
        if links_list:
            st.write(f"Found {len(links_list)} links:")
            
            # Show links in expandable section
            with st.expander("View All Links", expanded=True):
                for i, link in enumerate(links_list, 1):
                    if link.startswith('http'):
                        st.markdown(f"[{link}]({link})")
                    else:
                        st.write(f"{link}")
            
            # Download links
            if st.button("Download Links as Text"):
                st.download_button(
                    label="Download Links",
                    data='\n'.join(links_list),
                    file_name=f"{selected_company}_links_{st.session_state.selected_date.strftime('%d%m%Y')}.txt",
                    mime="text/plain"
                )
        else:
            st.info("No valid links found")
    else:
        st.info("No links available for this company")
    
    # Extracted Text Content Section
    st.markdown("<h3 class='section-header'>Extracted Text Content</h3>", unsafe_allow_html=True)
    
    text_content = data.get('extracted_text', '')
    if text_content and text_content.strip() and text_content.lower() != 'nan':
        # Text search
        text_search = st.text_input("Search in text content", placeholder="Enter keyword to search...")
        
        display_text = text_content
        if text_search and text_search in text_content.lower():
            # Simple highlighting
            display_text = text_content.replace(text_search, f"**{text_search}**")
        
        # Show preview
        st.text_area("Content Preview", text_content[:500] + "..." if len(text_content) > 500 else text_content, height=100)
        
        # Full content in expandable section
        with st.expander("View Full Content", expanded=False):
            st.markdown(display_text)
        
        # Download text content
        if st.button("Download Text Content"):
            st.download_button(
                label="Download Text",
                data=text_content,
                file_name=f"{selected_company}_content_{st.session_state.selected_date.strftime('%d%m%Y')}.txt",
                mime="text/plain"
            )
    else:
        st.info("No text content available for this company")
    
    # Raw data section
    st.markdown("<h3 class='section-header'>Raw Data</h3>", unsafe_allow_html=True)
    
    if st.button("Show Raw Data"):
        st.json({
            'company_name': data['company_name'],
            'row_number': data['row_number'],
            'extraction_date': str(data['extraction_date']),
            'extracted_links': data['extracted_links'][:200] + "..." if len(data['extracted_links']) > 200 else data['extracted_links'],
            'extracted_text': data['extracted_text'][:200] + "..." if len(data['extracted_text']) > 200 else data['extracted_text']
        })

if __name__ == "__main__":
    main()
