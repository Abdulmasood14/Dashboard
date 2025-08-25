import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime, date, timedelta
import re 
import requests
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="News Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Glacier UI effects
st.markdown("""
<style>
    /* Dark theme base */
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #1a1a2e 100%);
        color: #e8f4f8;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #1a1a2e 100%);
    }
    
    /* Sidebar dark glacier theme */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    .company-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 25%, #4a90b8 50%, #87ceeb 75%, #b0e0e6 100%);
        border-radius: 25px;
        color: #0f0f23;
        text-align: center;
        box-shadow: 0 15px 35px rgba(135, 206, 235, 0.3), 0 0 25px rgba(176, 224, 230, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 200px;
        font-size: 26px;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(15, 15, 35, 0.3);
        position: relative;
        overflow: hidden;
        padding: 60px 20px;
        cursor: pointer;
        border: 2px solid rgba(135, 206, 235, 0.4);
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }
    
    .company-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .company-card:hover::before {
        left: 100%;
    }
    
    .company-card:hover {
        transform: translateY(-15px) scale(1.03);
        box-shadow: 0 25px 50px rgba(135, 206, 235, 0.4), 0 0 40px rgba(176, 224, 230, 0.3);
        background: linear-gradient(135deg, #2d5a87 0%, #4a90b8 25%, #87ceeb 50%, #b0e0e6 75%, #e0f6ff 100%);
        border: 2px solid rgba(135, 206, 235, 0.8);
    }
    
    .main-header {
        text-align: center;
        color: #87ceeb;
        margin-bottom: 30px;
        text-shadow: 0 0 20px rgba(135, 206, 235, 0.5);
        font-weight: 700;
    }
    
    .section-header {
        color: #b0e0e6;
        border-bottom: 2px solid #4a90b8;
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 15px;
        text-shadow: 0 0 10px rgba(176, 224, 230, 0.3);
        background: linear-gradient(90deg, #1e3a5f, transparent);
        padding-left: 10px;
        border-radius: 5px;
    }
    
    .status-success {
        color: #4ade80;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
    }
    
    .status-warning {
        color: #fbbf24;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(251, 191, 36, 0.3);
    }
    
    .status-error {
        color: #f87171;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(248, 113, 113, 0.3);
    }
    
    .calendar-section {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.8), rgba(45, 90, 135, 0.6));
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(135, 206, 235, 0.3);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(135, 206, 235, 0.1);
    }
    
    .date-info {
        font-size: 18px;
        color: #b0e0e6;
        font-weight: 600;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 0 0 15px rgba(176, 224, 230, 0.4);
    }
    
    /* Streamlit widgets dark glacier styling */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.9), rgba(45, 90, 135, 0.7));
        border: 1px solid rgba(135, 206, 235, 0.4);
        border-radius: 10px;
        color: #e8f4f8;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.9), rgba(45, 90, 135, 0.7));
        border: 1px solid rgba(135, 206, 235, 0.4);
        border-radius: 10px;
        color: #e8f4f8;
        backdrop-filter: blur(10px);
    }
    
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.9), rgba(45, 90, 135, 0.7));
        border: 1px solid rgba(135, 206, 235, 0.4);
        border-radius: 10px;
        color: #e8f4f8;
        backdrop-filter: blur(10px);
    }
    
    /* Style all Streamlit buttons to look like glacier cards */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 25%, #4a90b8 50%, #87ceeb 75%, #b0e0e6 100%) !important;
        border: 2px solid rgba(135, 206, 235, 0.4) !important;
        border-radius: 25px !important;
        color: #0f0f23 !important;
        text-align: center !important;
        box-shadow: 0 15px 35px rgba(135, 206, 235, 0.3), 0 0 25px rgba(176, 224, 230, 0.2) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-height: 200px !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 10px rgba(15, 15, 35, 0.3) !important;
        width: 100% !important;
        margin: 10px 0 !important;
        backdrop-filter: blur(10px) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-15px) scale(1.03) !important;
        box-shadow: 0 25px 50px rgba(135, 206, 235, 0.4), 0 0 40px rgba(176, 224, 230, 0.3) !important;
        background: linear-gradient(135deg, #2d5a87 0%, #4a90b8 25%, #87ceeb 50%, #b0e0e6 75%, #e0f6ff 100%) !important;
        border: 2px solid rgba(135, 206, 235, 0.8) !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:active {
        transform: translateY(-8px) scale(1.01) !important;
    }
    
    /* Regular buttons styling */
    div[data-testid="stButton"] > button:not([kind="primary"]) {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.9), rgba(45, 90, 135, 0.7)) !important;
        border: 1px solid rgba(135, 206, 235, 0.4) !important;
        border-radius: 10px !important;
        color: #b0e0e6 !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stButton"] > button:not([kind="primary"]):hover {
        background: linear-gradient(135deg, rgba(45, 90, 135, 0.9), rgba(74, 144, 184, 0.7)) !important;
        border: 1px solid rgba(135, 206, 235, 0.8) !important;
        color: #e0f6ff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(135, 206, 235, 0.2) !important;
    }
    
    /* Metrics styling */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.8), rgba(45, 90, 135, 0.6));
        border: 1px solid rgba(135, 206, 235, 0.3);
        border-radius: 15px;
        padding: 15px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(135, 206, 235, 0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.8), rgba(45, 90, 135, 0.6)) !important;
        border: 1px solid rgba(135, 206, 235, 0.3) !important;
        border-radius: 10px !important;
        color: #b0e0e6 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .streamlit-expanderContent {
        background: linear-gradient(135deg, rgba(15, 15, 35, 0.9), rgba(26, 26, 46, 0.8)) !important;
        border: 1px solid rgba(135, 206, 235, 0.2) !important;
        border-radius: 0 0 10px 10px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%) !important;
    }
    
    /* Info/warning/error messages */
    .stInfo {
        background: linear-gradient(135deg, rgba(74, 144, 184, 0.2), rgba(135, 206, 235, 0.1)) !important;
        border: 1px solid rgba(135, 206, 235, 0.4) !important;
        border-radius: 10px !important;
        color: #b0e0e6 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(255, 215, 0, 0.1)) !important;
        border: 1px solid rgba(251, 191, 36, 0.4) !important;
        border-radius: 10px !important;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(248, 113, 113, 0.2), rgba(255, 0, 0, 0.1)) !important;
        border: 1px solid rgba(248, 113, 113, 0.4) !important;
        border-radius: 10px !important;
    }
    
    /* Add glacial particle effect */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: radial-gradient(2px 2px at 20px 30px, rgba(176, 224, 230, 0.3), transparent),
                         radial-gradient(2px 2px at 40px 70px, rgba(135, 206, 235, 0.2), transparent),
                         radial-gradient(1px 1px at 90px 40px, rgba(176, 224, 230, 0.4), transparent),
                         radial-gradient(1px 1px at 130px 80px, rgba(135, 206, 235, 0.3), transparent),
                         radial-gradient(2px 2px at 160px 30px, rgba(176, 224, 230, 0.2), transparent);
        background-repeat: repeat;
        background-size: 200px 200px;
        pointer-events: none;
        z-index: -1;
        animation: glacialFloat 20s infinite linear;
    }
    
    @keyframes glacialFloat {
        0% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-20px) translateX(10px); }
        50% { transform: translateY(-40px) translateX(-5px); }
        75% { transform: translateY(-20px) translateX(15px); }
        100% { transform: translateY(0px) translateX(0px); }
    }
    
    /* Text color adjustments */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #b0e0e6 !important;
    }
    
    .stMarkdown p, .stMarkdown div {
        color: #e8f4f8 !important;
    }
    
    /* JSON display styling */
    .stJson {
        background: linear-gradient(135deg, rgba(15, 15, 35, 0.9), rgba(26, 26, 46, 0.8)) !important;
        border: 1px solid rgba(135, 206, 235, 0.3) !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
    }
</style>
""", unsafe_allow_html=True)

class CompanyDataProcessor:
    def __init__(self, github_repo="Abdulmasood14/news", csv_directory="scraper_csv_outputs"):
        self.github_repo = github_repo
        self.csv_directory = csv_directory
        self.companies_data = {}
        self.available_dates = []
        self.load_available_dates()
    
    def load_available_dates(self):
        """Load available dates by checking file existence directly (bypasses GitHub API)"""
        try:
            # Generate date range to check (last 60 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=60)
            
            available_dates = []
            current_date = start_date
            
            while current_date <= end_date:
                date_str = current_date.strftime("%d.%m.%Y")
                csv_filename = f"{date_str}.csv"
                github_raw_url = f"https://raw.githubusercontent.com/{self.github_repo}/master/{self.csv_directory}/{csv_filename}"
                
                try:
                    # Quick HEAD request to check if file exists
                    response = requests.head(github_raw_url, timeout=3)
                    if response.status_code == 200:
                        available_dates.append(current_date)
                except:
                    pass  # File doesn't exist or request failed
                
                current_date += timedelta(days=1)
            
            self.available_dates = sorted(available_dates, reverse=True)
            
            # If no dates found, try some fallback dates
            if not self.available_dates:
                fallback_dates = [
                    date(2025, 1, 15),
                    date(2025, 1, 14),
                    date(2025, 1, 13),
                    date(2024, 12, 31),
                    date(2024, 12, 30),
                ]
                
                for check_date in fallback_dates:
                    date_str = check_date.strftime("%d.%m.%Y")
                    csv_filename = f"{date_str}.csv"
                    github_raw_url = f"https://raw.githubusercontent.com/{self.github_repo}/master/{self.csv_directory}/{csv_filename}"
                    
                    try:
                        response = requests.head(github_raw_url, timeout=3)
                        if response.status_code == 200:
                            available_dates.append(check_date)
                    except:
                        pass
                
                self.available_dates = sorted(available_dates, reverse=True)
                
        except Exception as e:
            st.error(f"Error discovering dates: {str(e)}")
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
        
        # Construct GitHub raw URL for the CSV file
        date_str = selected_date.strftime("%d.%m.%Y")
        csv_filename = f"{date_str}.csv"
        github_raw_url = f"https://raw.githubusercontent.com/{self.github_repo}/master/{self.csv_directory}/{csv_filename}"
        
        try:
            # Download CSV from GitHub
            response = requests.get(github_raw_url, timeout=10)
            if response.status_code == 200:
                # Read CSV content
                csv_content = StringIO(response.text)
                df = pd.read_csv(csv_content)
                
                # Validate columns
                required_columns = ['Company_Name', 'Extracted_Links', 'Extracted_Text']
                if not all(col in df.columns for col in required_columns):
                    st.error(f"CSV file must contain columns: {required_columns}")
                    return
                
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
            else:
                st.error(f"Failed to download CSV file for {date_str} from GitHub (Status: {response.status_code})")
                self.companies_data = {}
                
        except Exception as e:
            st.error(f"Error loading data for {date_str}: {str(e)}")
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
