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
    page_title="Nifty 50 News Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for glacier dark theme
st.markdown("""
<style>
    .company-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #475569 75%, #64748b 100%);
        border: 2px solid rgba(148, 163, 184, 0.3);
        border-radius: 20px;
        color: #e2e8f0;
        text-align: center;
        box-shadow: 
            0 0 20px rgba(148, 163, 184, 0.2),
            inset 0 0 20px rgba(148, 163, 184, 0.1),
            0 10px 25px rgba(15, 23, 42, 0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 200px;
        font-size: 26px;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.7);
        position: relative;
        overflow: hidden;
        padding: 60px 20px;
        cursor: pointer;
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }
    
    .company-card:before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(148, 163, 184, 0.1) 0%, transparent 70%);
        transform: rotate(45deg);
        transition: all 0.6s ease;
        opacity: 0;
    }
    
    .company-card:hover {
        transform: translateY(-15px) scale(1.03);
        box-shadow: 
            0 0 30px rgba(148, 163, 184, 0.4),
            inset 0 0 30px rgba(148, 163, 184, 0.2),
            0 20px 40px rgba(15, 23, 42, 0.7);
        background: linear-gradient(135deg, #1e293b 0%, #334155 25%, #475569 50%, #64748b 75%, #94a3b8 100%);
        border-color: rgba(148, 163, 184, 0.6);
        color: #f1f5f9;
    }
    
    .company-card:hover:before {
        opacity: 1;
        animation: glacierShimmer 2s infinite;
    }
    
    @keyframes glacierShimmer {
        0% { transform: rotate(45deg) translateX(-100%); }
        100% { transform: rotate(45deg) translateX(100%); }
    }
    
    .main-header {
        text-align: center;
        color: #94a3b8;
        margin-bottom: 30px;
        text-shadow: 0 0 10px rgba(148, 163, 184, 0.5);
    }
    
    .section-header {
        color: #cbd5e1;
        border-bottom: 2px solid rgba(148, 163, 184, 0.5);
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 15px;
        text-shadow: 0 0 5px rgba(148, 163, 184, 0.3);
    }
    
    .status-success {
        color: #10b981;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }
    
    .status-warning {
        color: #f59e0b;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
    }
    
    .status-error {
        color: #ef4444;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
    }
    
    .calendar-section {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 2px solid rgba(148, 163, 184, 0.2);
        box-shadow: 
            0 0 15px rgba(148, 163, 184, 0.1),
            inset 0 0 15px rgba(148, 163, 184, 0.05);
        backdrop-filter: blur(5px);
    }
    
    .date-info {
        font-size: 18px;
        color: #cbd5e1;
        font-weight: 600;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 0 0 8px rgba(203, 213, 225, 0.4);
    }
    
    .search-section {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 2px solid rgba(148, 163, 184, 0.2);
        box-shadow: 
            0 0 15px rgba(148, 163, 184, 0.1),
            inset 0 0 15px rgba(148, 163, 184, 0.05);
        backdrop-filter: blur(5px);
    }
    
    /* Dark glacier theme for Streamlit elements */
    .stApp {
        background: linear-gradient(135deg, #020617 0%, #0f172a 50%, #1e293b 100%);
        color: #e2e8f0;
    }
    
    /* Style all Streamlit buttons to look like glacier cards */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #475569 75%, #64748b 100%) !important;
        border: 2px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 20px !important;
        color: #e2e8f0 !important;
        text-align: center !important;
        box-shadow: 
            0 0 20px rgba(148, 163, 184, 0.2),
            inset 0 0 20px rgba(148, 163, 184, 0.1),
            0 10px 25px rgba(15, 23, 42, 0.5) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-height: 200px !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.7) !important;
        width: 100% !important;
        margin: 10px 0 !important;
        backdrop-filter: blur(10px) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-15px) scale(1.03) !important;
        box-shadow: 
            0 0 30px rgba(148, 163, 184, 0.4),
            inset 0 0 30px rgba(148, 163, 184, 0.2),
            0 20px 40px rgba(15, 23, 42, 0.7) !important;
        background: linear-gradient(135deg, #1e293b 0%, #334155 25%, #475569 50%, #64748b 75%, #94a3b8 100%) !important;
        border-color: rgba(148, 163, 184, 0.6) !important;
        color: #f1f5f9 !important;
    }
    
    div[data-testid="stButton"] > button[kind="primary"]:active {
        transform: translateY(-8px) scale(1.01) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Metrics styling */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 0 10px rgba(148, 163, 184, 0.1);
    }
    
    /* Text inputs and selects glacier theme */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 8px;
        color: #e2e8f0;
    }
    
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 8px;
        color: #e2e8f0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 8px;
        color: #cbd5e1;
    }
    
    /* Info/warning/error boxes glacier theme */
    .stAlert {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 8px;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Nifty 50 companies list
NIFTY_50_COMPANIES = [
    "RELIANCE", "TCS", "HDFCBANK", "BHARTIARTL", "INFY", "ICICIBANK", "SBIN", "LICI",
    "HINDUNILVR", "ITC", "KOTAKBANK", "LT", "HCLTECH", "ASIANPAINT", "AXISBANK",
    "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "ADANIENT", "WIPRO", "ONGC",
    "NTPC", "JSWSTEEL", "M&M", "POWERGRID", "BAJFINANCE", "TATAMOTORS", "TECHM",
    "ADANIPORTS", "COALINDIA", "NESTLEIND", "TATACONSUM", "BAJAJFINSV", "HDFCLIFE",
    "HINDALCO", "INDUSINDBK", "SBILIFE", "BPCL", "GRASIM", "CIPLA", "TATASTEEL",
    "APOLLOHOSP", "DRREDDY", "EICHERMOT", "BRITANNIA", "DIVISLAB", "HEROMOTOCO",
    "BAJAJ-AUTO", "UPL"
]

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
                    
                    # Process the data - filter for Nifty 50 companies
                    companies_data = {}
                    
                    for index, row in df.iterrows():
                        company_name = str(row['Company_Name']).strip().upper()
                        
                        # Check if company is in Nifty 50 list
                        if company_name and company_name != 'NAN' and company_name in NIFTY_50_COMPANIES:
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
    
    def get_nifty50_companies_list(self):
        """Get list of Nifty 50 companies available for selected date"""
        return list(self.companies_data.keys())
    
    def get_all_nifty50_companies(self):
        """Get all Nifty 50 companies"""
        return NIFTY_50_COMPANIES
    
    def get_company_data(self, company_name):
        """Get data for specific company"""
        return self.companies_data.get(company_name.upper())
    
    def get_available_dates(self):
        """Get list of available dates"""
        return self.available_dates
    
    def search_companies(self, search_term):
        """Search companies by name"""
        if not search_term:
            return NIFTY_50_COMPANIES
        
        search_term = search_term.upper()
        return [company for company in NIFTY_50_COMPANIES if search_term in company]

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    
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
    """Display main dashboard with Nifty 50 company cards"""
    st.markdown("<h1 class='main-header'>Nifty 50 News Dashboard</h1>", unsafe_allow_html=True)
    
    # Date Selection Section
    st.markdown("<div class='calendar-section'>", unsafe_allow_html=True)
    st.markdown("### Select Date for News Data")
    
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
        # Still show Nifty 50 companies even if no data files
        show_nifty50_cards(processor, None)
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
    
    # Company Search Section
    st.markdown("<div class='search-section'>", unsafe_allow_html=True)
    st.markdown("### Search Nifty 50 Companies")
    
    search_term = st.text_input(
        "Search for companies:",
        placeholder="Type company name (e.g., RELIANCE, TCS, INFY...)",
        key="company_search"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Show Nifty 50 company cards
    show_nifty50_cards(processor, search_term)

def show_nifty50_cards(processor, search_term):
    """Display Nifty 50 company cards"""
    
    # Get filtered companies based on search
    if search_term:
        companies = processor.search_companies(search_term)
        st.markdown(f"<div class='date-info'>Found {len(companies)} companies matching '{search_term}'</div>", 
                   unsafe_allow_html=True)
    else:
        companies = processor.get_all_nifty50_companies()
        st.markdown(f"<div class='date-info'>Showing all {len(companies)} Nifty 50 companies</div>", 
                   unsafe_allow_html=True)
    
    if not companies:
        st.info("No companies found matching your search.")
        return
    
    # Load data for selected date if available
    if st.session_state.selected_date:
        processor.load_company_data_for_date(st.session_state.selected_date)
        available_companies = processor.get_nifty50_companies_list()
        st.markdown(f"<div class='date-info'>Data available for {len(available_companies)} companies on {st.session_state.selected_date.strftime('%d %B %Y')}</div>", 
                   unsafe_allow_html=True)
    else:
        available_companies = []
        st.markdown("<div class='date-info'>Select a date above to view news data</div>", 
                   unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Company cards
    st.markdown("<h2 class='section-header'>Nifty 50 Company Cards</h2>", unsafe_allow_html=True)
    
    # Create cards in grid layout (3 columns for better fit)
    cols_per_row = 3
    for i in range(0, len(companies), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, company in enumerate(companies[i:i+cols_per_row]):
            with cols[j]:
                # Check if data is available for this company on selected date
                has_data = company in available_companies if st.session_state.selected_date else False
                
                # Add indicator if data is available
                card_text = company
                if has_data:
                    card_text += " 📊"  # Data available indicator
                
                # Create a button with the company name
                if st.button(
                    card_text,
                    key=f"card_{company}_{i}_{j}",
                    help=f"Click to view details for {company}" + (" (Data available)" if has_data else " (No data for selected date)"),
                    use_container_width=True
                ):
                    st.session_state.selected_company = company
                    if has_data:
                        st.rerun()
                    else:
                        if st.session_state.selected_date:
                            st.warning(f"No news data available for {company} on {st.session_state.selected_date.strftime('%d %B %Y')}. Please select a different date or company.")
                        else:
                            st.info("Please select a date first to view news data.")

def show_company_details(processor):
    """Display detailed view for selected company"""
    
    if not st.session_state.selected_company:
        st.error("Please select a company first from the Dashboard")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return
    
    if not st.session_state.selected_date:
        st.error("Please select a date first from the Dashboard")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return
    
    # Load data for current date
    processor.load_company_data_for_date(st.session_state.selected_date)
    
    # Get data for selected company
    data = processor.get_company_data(st.session_state.selected_company)
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.page = "Dashboard"
        if 'selected_company' in st.session_state:
            del st.session_state.selected_company
        st.rerun()
    
    if not data:
        st.error(f"No news data found for {st.session_state.selected_company} on {st.session_state.selected_date.strftime('%d %B %Y')}")
        st.info("Try selecting a different date or company from the dashboard.")
        return
    
    # Company header
    st.markdown(f"<h1 class='main-header'>{st.session_state.selected_company} - News Details</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='date-info'>News data from: {st.session_state.selected_date.strftime('%d %B %Y')}</div>", 
               unsafe_allow_html=True)
    
    # Summary information
    st.markdown("<h3 class='section-header'>Company Information</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric("Company", data['company_name'])
    with col2:
        st.metric("Date", st.session_state.selected_date.strftime('%d %B %Y'))
    with col3:
        st.metric("Nifty 50", "✓ Listed")
    
    # Extracted Links Section
    st.markdown("<h3 class='section-header'>News Links</h3>", unsafe_allow_html=True)
    
    links_text = data.get('extracted_links', '')
    if links_text and links_text.strip() and links_text.lower() != 'nan':
        # Split links by newlines or other separators
        links_list = [link.strip() for link in links_text.split('\n') if link.strip()]
        
        if links_list:
            st.write(f"Found {len(links_list)} news links:")
            
            # Show links in expandable section
            with st.expander("View All News Links", expanded=True):
                for i, link in enumerate(links_list, 1):
                    if link.startswith('http'):
                        st.markdown(f"**Link {i}:** [{link}]({link})")
                    else:
                        st.write(f"**Link {i}:** {link}")
            
            # Download links
            if st.button("Download Links as Text"):
                st.download_button(
                    label="Download Links",
                    data='\n'.join(links_list),
                    file_name=f"{st.session_state.selected_company}_links_{st.session_state.selected_date.strftime('%d%m%Y')}.txt",
                    mime="text/plain"
                )
        else:
            st.info("No valid links found")
    else:
        st.info("No news links available for this company on selected date")
    
    # Extracted Text Content Section
    st.markdown("<h3 class='section-header'>News Content</h3>", unsafe_allow_html=True)
    
    text_content = data.get('extracted_text', '')
    if text_content and text_content.strip() and text_content.lower() != 'nan':
        # Text search
        text_search = st.text_input("Search in news content", placeholder="Enter keyword to search...")
        
        display_text = text_content
        if text_search and text_search.lower() in text_content.lower():
            # Simple highlighting
            display_text = text_content.replace(text_search, f"**{text_search}**")
            display_text = display_text.replace(text_search.lower(), f"**{text_search.lower()}**")
            display_text = display_text.replace(text_search.upper(), f"**{text_search.upper()}**")
        
        # Show preview
        st.text_area("Content Preview", text_content[:1000] + "..." if len(text_content) > 1000 else text_content, height=150)
        
        # Full content in expandable section
        with st.expander("View Full News Content", expanded=False):
            st.markdown(display_text)
        
        # Download text content
        if st.button("Download News Content"):
            st.download_button(
                label="Download Content",
                data=text_content,
                file_name=f"{st.session_state.selected_company}_news_{st.session_state.selected_date.strftime('%d%m%Y')}.txt",
                mime="text/plain"
            )
    else:
        st.info("No news content available for this company on selected date")

if __name__ == "__main__":
    main()
