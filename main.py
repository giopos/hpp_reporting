#python3 -m streamlit run "/Users/postiglioneg/Desktop/12x25 streamlit/main.py"

# Streamlit app for Swimmer Dashboard
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.integrate import quad
import json
import base64
from io import BytesIO
import zipfile
import matplotlib as mpl
import matplotlib.pyplot as plt  # Keep for PDF export
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch
from matplotlib.patches import Rectangle, Circle
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from pathlib import Path
import tracker

# Set page configuration to wide layout and hide all default menus and buttons
st.set_page_config(
    layout="wide", 
    page_title="Swimmer Dashboard",
    page_icon="🏊‍♂️",
    menu_items={},
    initial_sidebar_state="collapsed"
)

# Track app start (once per session)
tracker.track_app_start()

# Hide Streamlit elements including the deploy menu
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stDecoration"] {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

# Define a consistent color palette - updated for better visual harmony
COLOR_BLUE = "#3B82F6"  # Primary blue
COLOR_NAVY = "#1E40AF"  # Darker blue
COLOR_RED = "#EF4444"   # Accent red
COLOR_LIGHT_BLUE = "#93C5FD"  # Light blue for highlights
COLOR_GRAY = "#F3F4F6"  # Background gray
COLOR_TEXT = "#1F2937"  # Primary text
COLOR_SECONDARY_TEXT = "#6B7280"  # Secondary text
COLOR_GREEN = "#10B981"  # Success green
COLOR_YELLOW = "#F59E0B"  # Warning yellow
COLOR_PURPLE = "#8B5CF6"  # Accent purple
COLOR_GREEN_LIGHT = "#ECFDF3"
COLOR_RED_LIGHT = "#FEE2E2"
COLOR_BLUE_LIGHT = "#EFF6FF"

# Custom CSS to improve layout with a more modern design and compact view
st.markdown("""
<style>
    /* Global layout adjustments */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }
    .main .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* Header styling to match report layout */
    .dashboard-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        padding: 0.4rem 0.25rem 0.2rem 0.25rem;
        margin-bottom: 0.2rem;
        background-color: white;
        border-radius: 4px;
    }
    .header-left {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
    }
    .header-title {
        font-size: 2.6rem;
        font-weight: 800;
        line-height: 1.05;
        margin: 0;
        color: #1E40AF;
    }
    .header-subtitle {
        font-size: 1.5rem;
        font-style: italic;
        margin: 0;
        color: #1E40AF;
    }
    .header-controls {
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
        align-items: flex-end;
    }
    .header-controls [data-baseweb="select"] > div {
        background-color: #f3f4f6;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        min-height: 2.2rem;
        padding: 2px 8px;
    }
    .header-controls [data-baseweb="select"] input {
        font-size: 0.9rem;
        color: #111827;
    }
    
    /* Card styling - reduced padding */
    .card {
        background-color: white;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border: 1px solid #f0f0f0;
    }
    
    /* Dashboard grid layout */
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 8px;
    }
    
    /* Metric cards - more compact */
    .metrics-container {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin-bottom: 5px;
    }
    .metric-card {
        background-color: white;
        border-radius: 4px;
        padding: 5px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        flex: 1;
        min-width: 80px;
        text-align: center;
        border: 1px solid #f0f0f0;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1E40AF;
        margin: 2px 0;
    }
    .metric-label {
        font-size: 14px;
        color: #6B7280;
        margin-bottom: 0;
    }
    
    /* Chart containers - reduced height */
    .chart-container {
        background-color: white;
        border-radius: 4px;
        padding: 5px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 4px;
        /* height: 160px; */
        /* overflow: hidden; */
        border: 1px solid #f0f0f0;
        display: flex;
        flex-direction: column;
    }
    .chart-title {
        font-size: 14px;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 2px;
        color: #1E40AF;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 2px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 30px;
        white-space: pre-wrap;
        background-color: #f3f4f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding: 5px 10px;
        font-size: 0.8rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3B82F6;
        color: white;
    }
    
    /* Export button */
    .export-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: white;
        color: #1E40AF;
        padding: 5px 10px;
        border-radius: 4px;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.8rem;
        margin: 5px 0;
        cursor: pointer;
        border: 1px solid #e5e7eb;
        transition: all 0.2s;
    }
    .export-button:hover {
        background-color: #f9fafb;
        border-color: #3B82F6;
    }
    .stButton button {
        background-color: white !important;
        color: #1E40AF !important;
        font-weight: 500 !important;
        border-radius: 4px !important;
        padding: 4px 10px !important;
        font-size: 0.8rem !important;
        height: auto !important;
        border: 1px solid #e5e7eb !important;
        transition: all 0.2s !important;
    }
    .stButton button:hover {
        background-color: #f9fafb !important;
        border-color: #3B82F6 !important;
    }
    
    /* Hide headers completely */
    header {display: none !important;}
    
    /* Reduce header margins further */
    h1, h2, h3, h4 {
        margin-top: 0 !important;
        margin-bottom: 0.1rem !important;
        color: #1F2937;
    }
    
    /* Hide fullscreen button on charts */
    button[title="View fullscreen"] {
        display: none;
    }
    
    /* Footer */
    footer {
        font-size: 0.6rem;
        color: #6B7280;
        margin-top: 5px;
        text-align: right;
        padding: 3px;
        border-top: 1px solid #f0f0f0;
    }
    
    /* Make sure plots don't overflow and use space efficiently */
    .stPlotlyChart, .stPlot {
        /* height: calc(100% - 15px) !important; */
        /* min-height: 0 !important; */
    }
    
    /* Fix for Plotly charts to stay within containers */
    .chart-container [data-testid="stPlotlyChart"] {
        width: 100% !important;
        flex: 1 !important;
    }
    
    /* Ensure the SVG elements inside Plotly charts are properly sized */
    .chart-container [data-testid="stPlotlyChart"] svg {
        max-height: 100% !important;
    }
    
    /* Reduce padding in dataframe further */
    .dataframe-container {
        padding: 0 !important;
    }
    .dataframe th, .dataframe td {
        padding: 2px 4px !important;
        font-size: 0.75rem !important;
    }
    
    /* Info messages */
    .info-message {
        background-color: #f3f4f6;
        border-radius: 3px;
        padding: 4px;
        font-size: 0.7rem;
        color: #6B7280;
        text-align: center;
    }
    
    /* Charts grid layout */
    .charts-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: auto auto;
        gap: 8px;
        margin-bottom: 8px;
    }
    /* Make selectbox more compact */
    .stSelectbox {
        margin-bottom: 0 !important;
    }
    .stSelectbox > div {
        margin-bottom: 0 !important;
    }
    .stSelectbox > div > div > div {
        min-height: 1.5rem !important;
    }
    
    /* Remove extra space around elements */
    div.element-container {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Adjust spacing for stacked elements */
    div.stMarkdown {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Configure matplotlib for consistent, modern charts with higher quality
plt.style.use('ggplot')
mpl.rcParams['font.size'] = 9
mpl.rcParams['figure.titlesize'] = 11
mpl.rcParams['axes.titlesize'] = 10
mpl.rcParams['axes.labelsize'] = 9
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['figure.figsize'] = (4, 3)
mpl.rcParams['figure.dpi'] = 150
mpl.rcParams['savefig.dpi'] = 200
mpl.rcParams['figure.autolayout'] = True
mpl.rcParams['axes.grid'] = True
mpl.rcParams['grid.alpha'] = 0.2
mpl.rcParams['axes.facecolor'] = '#f8f9fa'
mpl.rcParams['figure.facecolor'] = 'white'
mpl.rcParams['axes.edgecolor'] = '#e5e7eb'
mpl.rcParams['axes.linewidth'] = 0.5
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['lines.markersize'] = 5
mpl.rcParams['patch.linewidth'] = 0.5

# Load data
@st.cache_data
def load_data(uploaded_file=None):
    """Load data from uploaded file or return None"""
    if uploaded_file is None:
        return None
    df = pd.read_excel(uploaded_file)
    # Strip non-breaking spaces and trailing whitespace from key string columns
    for col in ['Gender', 'Stroke', 'Swimmer']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('\xa0', '', regex=False).str.strip()
            df[col] = df[col].replace('nan', pd.NA)
    return df

@st.cache_data
def load_percentile_data():
    with open("percentile_data.json", "r") as f:
        return json.load(f)

@st.cache_data
def load_template_file():
    """Load the template Excel file for downloads"""
    try:
        with open("12x25m Data Test.xlsx", "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None

def validate_uploaded_file(df):
    """Validate uploaded Excel file structure against expected template"""
    required_columns = ['Swimmer', 'Gender', 'Stroke', 'Date'] + [f'Time {i}' for i in range(1, 13)]
    optional_columns = (
        [f'Stroke Rate {i}' for i in range(1, 13)] +
        [f'Stroke Count {i}' for i in range(1, 13)] +
        [f'Stroke Efficiency Index {i}' for i in range(1, 13)] +
        ['CV', 'Dprime']
    )
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    extra_cols = [col for col in df.columns if col not in required_columns + optional_columns]
    
    return {
        'valid': len(missing_cols) == 0,
        'missing': missing_cols,
        'extra': extra_cols,
        'warnings': extra_cols
    }

def show_upload_interface():
    """Display the file upload interface with template download"""
    st.markdown("""
    <div style='text-align: center; padding: 2rem 1rem;'>
        <h1 style='color: #1E40AF; margin-bottom: 0.5rem;'>🏊‍♂️ Swimmer Performance Dashboard</h1>
        <p style='font-size: 1.2rem; color: #6B7280; margin-bottom: 2rem;'>
            Upload your 12x25m test data to generate comprehensive performance reports
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Template download section
        st.markdown("### Download Template")
        st.markdown("First time using this app? Download the Excel template to ensure your data is formatted correctly.")
        
        template_bytes = load_template_file()
        if template_bytes:
            if st.download_button(
                label="⬇ Download Excel Template",
                data=template_bytes,
                file_name="12x25m_Data_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            ):
                tracker.track_template_download()
        else:
            st.warning("Template file not found. Please ensure '12x25m Data Test.xlsx' is in the app directory.")
        
        st.markdown("---")
        
        # File upload section
        st.markdown("### Upload Your Data")
        st.markdown("Upload your completed Excel file with swimmer test data:")
        
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file (.xlsx or .xls) with your 12x25m test data",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            with st.spinner("Loading and validating data..."):
                try:
                    # Load the data
                    df = load_data(uploaded_file)
                    
                    if df is None:
                        st.error("Failed to load the Excel file. Please check the file format.")
                        return None
                    
                    # Validate the structure
                    validation = validate_uploaded_file(df)
                    
                    if validation['valid']:
                        st.success(f"File uploaded successfully! Found {len(df)} records.")
                        
                        # Show data summary
                        swimmers_count = df['Swimmer'].nunique()
                        strokes = df['Stroke'].dropna().unique().tolist()
                        dates = df['Date'].dropna().unique()
                        
                        st.markdown("**Data Summary:**")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Swimmers", swimmers_count)
                        with col_b:
                            st.metric("Strokes", len(strokes))
                        with col_c:
                            st.metric("Sessions", len(dates))
                        
                        if validation['warnings']:
                            with st.expander("Additional columns detected (not used in analysis)"):
                                st.write(", ".join(validation['warnings']))
                        
                        # Store in session state
                        st.session_state['data'] = df
                        st.session_state['uploaded_file_name'] = uploaded_file.name
                        st.session_state['upload_timestamp'] = pd.Timestamp.now()
                        tracker.track_file_upload(uploaded_file.name, len(df), swimmers_count)
                        
                        st.markdown("---")
                        st.info("Scroll down to view the dashboard")
                        
                        return df
                    else:
                        st.error("❌ File validation failed. The uploaded file is missing required columns.")
                        
                        # Show comparison
                        st.markdown("### 📋 Template Comparison")
                        st.markdown("**Missing Required Columns:**")
                        if validation['missing']:
                            for col in validation['missing']:
                                st.markdown(f"- ❌ `{col}`")
                        else:
                            st.markdown("- ✅ All required columns present")
                        
                        if validation['extra']:
                            st.markdown("**Extra Columns (will be ignored):**")
                            for col in validation['extra']:
                                st.markdown(f"- ⚠️ `{col}`")
                        
                        st.markdown("---")
                        st.info("💡 **Tip:** Download the template above and ensure your file has the same column structure.")
                        
                        return None
                        
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                    st.info("Please ensure the file is a valid Excel file (.xlsx or .xls) and not corrupted.")
                    return None
        
        # Instructions when no file uploaded
        st.markdown("""
        <div style='background-color: #F3F4F6; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
            <h4 style='margin-top: 0; color: #1F2937;'>Required Columns</h4>
            <ul style='color: #6B7280;'>
                <li><strong>Swimmer</strong> - Athlete name</li>
                <li><strong>Gender</strong> - M/F</li>
                <li><strong>Stroke</strong> - Freestyle, Backstroke, Breaststroke, or Butterfly</li>
                <li><strong>Date</strong> - Test date</li>
                <li><strong>Time 1</strong> through <strong>Time 12</strong> - Split times in seconds for each 25m rep</li>
            </ul>
            <h4 style='color: #1F2937;'>Optional Columns</h4>
            <ul style='color: #6B7280;'>
                <li>Stroke Rate, Stroke Count, Stroke Efficiency Index (1-12)</li>
                <li>CV (Critical Velocity), Dprime - will be calculated if not provided</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        return None

# Initialize session state
if 'data' not in st.session_state:
    st.session_state['data'] = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state['uploaded_file_name'] = None

# Load percentile reference data (always available)
percentile_reference_data = load_percentile_data()

# Show upload interface and get data
if st.session_state['data'] is None:
    tracker.track_page_view("upload_interface")
    data = show_upload_interface()
    if data is None:
        st.stop()  # Stop execution until file is uploaded
else:
    tracker.track_page_view("dashboard")
    data = st.session_state['data']
    
    # Show file info banner
    st.markdown(f"""
    <div style='background-color: #EFF6FF; padding: 0.5rem 1rem; border-radius: 4px; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <span style='color: #1E40AF; font-weight: 600;'>📊 Data Loaded:</span>
            <span style='color: #6B7280;'>{st.session_state.get('uploaded_file_name', 'Unknown file')}</span>
            <span style='color: #9CA3AF; margin-left: 1rem; font-size: 0.9rem;'>
                {len(data)} records | Uploaded: {st.session_state.get('upload_timestamp', pd.Timestamp.now()).strftime('%d/%m/%Y %H:%M')}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add button to upload different file
    if st.button("📤 Upload Different File", type="secondary"):
        st.session_state['data'] = None
        st.session_state['uploaded_file_name'] = None
        st.session_state['favorites'] = []
        st.rerun()

# Percentile calculation function (matching R implementation)
def calculate_percentile(reference_values, swimmer_value):
    """Calculate percentile rank - percentage of values less than swimmer's value"""
    values_below = sum(1 for v in reference_values if v < swimmer_value)
    return round(values_below / len(reference_values), 3) * 100

# Helper function to format pace
def format_pace(seconds):
    """Format pace as mm:ss or ss.s"""
    try:
        if seconds is None or (isinstance(seconds, float) and np.isnan(seconds)):
            return "N/A"
    except Exception:
        return "N/A"
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        m = int(seconds // 60)
        s = seconds - m * 60
        return f"{m}:{s:04.1f}"

def _format_date_display(value):
    date_val = pd.to_datetime(value, errors='coerce', dayfirst=True)
    if pd.notna(date_val):
        return date_val.strftime('%d/%m/%Y')
    return str(value) if value is not None else 'N/A'

def _format_date_file(value):
    date_val = pd.to_datetime(value, errors='coerce', dayfirst=True)
    if pd.notna(date_val):
        return date_val.strftime('%d-%m-%Y')
    return str(value).replace('/', '-').replace(' ', '_') if value is not None else 'N/A'

# PDF/export helpers
def _to_float(value):
    try:
        if pd.isna(value):
            return np.nan
        return float(value)
    except Exception:
        return np.nan

def _calc_cv_dprime(speeds_arr, splits_arr):
    speeds_late = speeds_arr[8:12]
    cv_val = np.mean(np.sort(speeds_late)[:2])
    dprime_val = (speeds_arr[0] - cv_val) * splits_arr[0]
    for idx in range(1, len(splits_arr)):
        dprime_val += ((speeds_arr[idx] - cv_val) * splits_arr[idx]) + 0.5 * (
            (speeds_arr[idx - 1] - speeds_arr[idx]) * splits_arr[idx]
        )
    return cv_val, dprime_val

def _metrics_for_row(r):
    if r is None:
        return None
    splits_arr = np.array([_to_float(r.get(col)) for col in split_cols], dtype=float)
    if np.isnan(splits_arr).any():
        return None
    speeds_arr = 25 / splits_arr
    cv_val = r.get('CV', np.nan)
    if pd.isna(cv_val):
        cv_val, dprime_val = _calc_cv_dprime(speeds_arr, splits_arr)
    else:
        dprime_val = r.get('Dprime', np.nan)
        if pd.isna(dprime_val):
            _, dprime_val = _calc_cv_dprime(speeds_arr, splits_arr)

    peak_speed_val = speeds_arr[0]
    drop_off_val = ((peak_speed_val - cv_val) / peak_speed_val) * 100

    cs_scm = 0.8518 * cv_val + 0.0925
    cs_lcm = cs_scm * 0.9554 - 0.0091
    pace_scm_sec = 100 / cs_scm
    pace_lcm_sec = 100 / cs_lcm

    sei_cols = [f"Stroke Efficiency Index {i}" for i in range(1, 13)]
    sei_vals = [
        _to_float(r.get(col))
        for col in sei_cols
        if not pd.isna(_to_float(r.get(col)))
    ]
    sei_avg = float(np.mean(sei_vals)) if sei_vals else np.nan

    return {
        "splits": splits_arr,
        "speeds": speeds_arr,
        "cum_time": np.cumsum(splits_arr),
        "cv": float(cv_val),
        "dprime": float(dprime_val),
        "peak_speed": float(peak_speed_val),
        "drop_off": float(drop_off_val),
        "pace_scm_sec": float(pace_scm_sec),
        "pace_lcm_sec": float(pace_lcm_sec),
        "pace_scm_str": format_pace(pace_scm_sec),
        "pace_lcm_str": format_pace(pace_lcm_sec),
        "sei_avg": sei_avg,
    }

def _delta_percent(curr_val, prev_val, higher_is_better=True):
    if curr_val is None or prev_val is None:
        return None
    if np.isnan(curr_val) or np.isnan(prev_val) or prev_val == 0:
        return None
    if higher_is_better:
        delta = (curr_val - prev_val) / abs(prev_val) * 100
    else:
        delta = (prev_val - curr_val) / abs(prev_val) * 100
    if abs(delta) < 0.05:
        return 0.0
    return delta

def _delta_absolute(curr_val, prev_val, higher_is_better=True):
    if curr_val is None or prev_val is None:
        return None
    if np.isnan(curr_val) or np.isnan(prev_val):
        return None
    delta = (curr_val - prev_val) if higher_is_better else (prev_val - curr_val)
    if abs(delta) < 0.005:
        return 0.0
    return delta

def _metric_color_styles(delta, mode="improve"):
    if delta is None or delta == 0:
        return COLOR_BLUE_LIGHT, None
    if mode == "dropoff":
        if delta < 0:
            return COLOR_BLUE_LIGHT, COLOR_BLUE
        return COLOR_GREEN_LIGHT, COLOR_GREEN
    return (COLOR_GREEN_LIGHT, COLOR_GREEN) if delta > 0 else (COLOR_RED_LIGHT, COLOR_RED)

# Get list of swimmers from loaded data
swimmers = sorted(data['Swimmer'].dropna().unique().tolist()) if data is not None else []

def _load_favorites():
    """Load favorites from session state only (no file persistence)"""
    return st.session_state.get("favorites", [])

def _save_favorites():
    """Save favorites to session state only (no file persistence)"""
    if 'data' in st.session_state and st.session_state['data'] is not None:
        swimmers_list = sorted(st.session_state['data']['Swimmer'].dropna().unique().tolist())
        favorites = st.session_state.get("favorites", [])
        favorites_sorted = sorted({name for name in favorites if name in swimmers_list})
        st.session_state["favorites"] = favorites_sorted

def _stroke_abbrev(stroke_name):
    mapping = {
        "butterfly": "BF",
        "backstroke": "BK",
        "breaststroke": "BR",
        "freestyle": "FS",
    }
    if stroke_name is None:
        return ""
    key = str(stroke_name).strip().lower()
    return mapping.get(key, key[:2].upper())

def _swimmer_strokes(swimmer_name):
    if not swimmer_name:
        return []
    strokes = data.loc[
        data['Swimmer'] == swimmer_name, 'Stroke'
    ].dropna().unique().tolist()
    return sorted(strokes)

def _on_swimmer_change():
    swimmer_name = st.session_state.get("select_swimmer")
    strokes = _swimmer_strokes(swimmer_name)
    if strokes:
        st.session_state["select_stroke"] = strokes[0]

def _select_favorite(name, stroke):
    st.session_state["select_swimmer"] = name
    if stroke:
        st.session_state["select_stroke"] = stroke

# Sidebar filters and export
if "favorites" not in st.session_state:
    st.session_state["favorites"] = _load_favorites()
if "select_swimmer" not in st.session_state:
    st.session_state["select_swimmer"] = swimmers[0] if swimmers else None
if "select_stroke" not in st.session_state:
    initial_strokes = _swimmer_strokes(st.session_state.get("select_swimmer"))
    st.session_state["select_stroke"] = initial_strokes[0] if initial_strokes else None

with st.sidebar:
    st.markdown("### Filters")
    with st.expander("Swimmer & Session", expanded=True):
        swimmer = st.selectbox(
            'Select Swimmer',
            swimmers,
            key="select_swimmer",
            on_change=_on_swimmer_change,
            label_visibility="collapsed"
        )

        # Filter data by selected swimmer
        swimmer_data = data[data['Swimmer'] == swimmer]

        # Get available strokes and dates for the selected swimmer
        available_strokes = swimmer_data['Stroke'].unique().tolist()
        available_strokes.sort()

        # Add stroke filter
        if len(available_strokes) > 1:
            selected_stroke = st.selectbox(
                'Select Stroke',
                available_strokes,
                key="select_stroke",
                label_visibility="collapsed"
            )
            swimmer_data = swimmer_data[swimmer_data['Stroke'] == selected_stroke]
        else:
            selected_stroke = available_strokes[0] if available_strokes else None

        # Get available dates for the selected swimmer and stroke
        available_dates = swimmer_data['Date'].unique().tolist()
        # Format dates for display
        date_options = []
        date_mapping = {}
        for date in available_dates:
            if isinstance(date, pd.Timestamp):
                formatted_date = date.strftime('%d/%m/%Y')
            elif isinstance(date, str):
                try:
                    date_obj = pd.to_datetime(date, dayfirst=True)
                    formatted_date = date_obj.strftime('%d/%m/%Y')
                except Exception:
                    formatted_date = str(date)
            else:
                formatted_date = str(date)
            date_options.append(formatted_date)
            date_mapping[formatted_date] = date

        # Add date filter if multiple dates available
        if len(date_options) > 1:
            selected_date_str = st.selectbox('Select Date', date_options, label_visibility="collapsed")
            selected_date = date_mapping[selected_date_str]
            swimmer_data = swimmer_data[swimmer_data['Date'] == selected_date]
        elif len(date_options) == 1:
            selected_date_str = date_options[0]
        else:
            selected_date_str = 'N/A'

    st.markdown("### Favorites")
    st.multiselect(
        "Select favorites",
        swimmers,
        key="favorites",
        on_change=_save_favorites
    )

    if st.session_state["favorites"]:
        st.markdown("**Quick Select**")
        quick_buttons = []
        for fav_name in st.session_state["favorites"]:
            for stroke_name in _swimmer_strokes(fav_name):
                abbr = _stroke_abbrev(stroke_name)
                label = f"{fav_name} ({abbr})"
                quick_buttons.append((label, fav_name, stroke_name))

        if quick_buttons:
            fav_cols = st.columns(min(3, len(quick_buttons)))
            for idx, (label, fav_name, stroke_name) in enumerate(quick_buttons):
                with fav_cols[idx % len(fav_cols)]:
                    st.button(
                        label,
                        key=f"favorite_{fav_name}_{stroke_name}",
                        on_click=_select_favorite,
                        args=(fav_name, stroke_name)
                    )

    st.markdown("### Export")
    if st.button("Export Report", help="Generate PDF report"):
        st.session_state["request_export"] = True
        st.session_state["show_bulk_export_dialog"] = False
    if st.button("Bulk Export", help="Export multiple athlete reports"):
        st.session_state["show_bulk_export_dialog"] = True
        st.session_state["show_pdf_dialog"] = False
        st.session_state["request_export"] = False
    
    # Logo settings for PDF export
    with st.expander("⚙️ PDF Logo Settings"):
        logo_option = st.radio(
            "Logo option",
            options=['default', 'upload', 'none'],
            format_func=lambda x: {'default': 'Use default logo', 'upload': 'Upload custom logo', 'none': 'No logo'}[x],
            key='logo_option',
            label_visibility="collapsed"
        )
        
        if logo_option == 'upload':
            uploaded_logo = st.file_uploader(
                "Upload logo image",
                type=['jpg', 'jpeg', 'png'],
                help="Upload a logo image for PDF reports",
                key='logo_uploader'
            )
            if uploaded_logo is not None:
                st.session_state['uploaded_logo'] = uploaded_logo.read()
                st.success("✅ Logo uploaded")
            elif 'uploaded_logo' in st.session_state:
                st.info("Using previously uploaded logo")
        elif logo_option == 'default':
            st.info("Will use default logo.jpg if available")
        else:
            st.info("PDFs will not include a logo")

    # Admin: Usage Logs (password-gated)
    with st.expander("📊 Usage Logs"):
        admin_pass = st.text_input("Admin password", type="password", key="admin_pass")
        try:
            expected_pass = st.secrets.get("admin", {}).get("password", "admin12x25")
        except Exception:
            expected_pass = "admin12x25"
        if admin_pass == expected_pass:
            logs = tracker.read_logs()
            summary = tracker.summarise_logs(logs)
            st.metric("Total events", summary["total_events"])
            st.metric("Unique sessions", summary["unique_sessions"])
            if summary["events_breakdown"]:
                st.markdown("**Events:**")
                for evt, count in sorted(summary["events_breakdown"].items(), key=lambda x: -x[1]):
                    st.text(f"  {evt}: {count}")
            log_bytes = tracker.get_log_file_bytes()
            if log_bytes:
                st.download_button(
                    "📥 Download Logs",
                    data=log_bytes,
                    file_name="usage_logs.jsonl",
                    mime="application/json",
                    key="download_logs_btn"
                )
            # Optional: push to GitHub
            if st.button("Push logs to GitHub", key="push_logs_btn"):
                ok, msg = tracker.push_logs_to_github()
                if ok:
                    st.success(msg)
                else:
                    st.warning(msg)
        elif admin_pass:
            st.error("Wrong password")

# Get date and stroke info
row = swimmer_data.iloc[0]
date_str = row.get('Date', '')
stroke_str = row.get('Stroke', '')

# Format date as dd/mm/yyyy if it's a datetime object
if isinstance(date_str, pd.Timestamp):
    date_str = date_str.strftime('%d/%m/%Y')
# Try to handle string date formats
elif isinstance(date_str, str) and len(date_str) > 10:
    try:
        # Try to parse the date string and reformat it
        date_obj = pd.to_datetime(date_str, dayfirst=True)
        date_str = date_obj.strftime('%d/%m/%Y')
    except:
        # If parsing fails, keep the original string
        pass

def _format_header_date(value):
    date_val = pd.to_datetime(value, errors='coerce', dayfirst=True)
    if pd.notna(date_val):
        return date_val.strftime('%B %Y')
    return str(value) if value else 'N/A'

header_date_str = _format_header_date(date_str)
header_subtitle = f"{header_date_str} - {stroke_str}" if stroke_str else header_date_str

# Track which swimmer/stroke/date is being viewed
tracker.track_swimmer_view(swimmer, str(stroke_str), str(date_str))

st.markdown(
    f"<div class='dashboard-header'>"
    f"<div class='header-left'>"
    f"<div class='header-title'>{swimmer}</div>"
    f"<div class='header-subtitle'>{header_subtitle}</div>"
    f"</div>"
    f"</div>",
    unsafe_allow_html=True
)
    
###############################################################################
# STEP 1: Check if Dprime & CV exist; if not, recalc using trapezoidal method.
###############################################################################
required_cols = ['Dprime', 'CV']
split_cols = [f"Time {i}" for i in range(1, 13)]
if not all(col in swimmer_data.columns for col in required_cols):
    # If the file does not have Dprime or CV
    if not all(col in swimmer_data.columns for col in split_cols):
        st.error("Required split time columns are missing.")
    else:
        # Recalculate from raw split times
        row = swimmer_data.iloc[0]
        splits = np.array([row[col] for col in split_cols], dtype=float)
        speeds = 25 / splits  # m/s
        cum_time = np.cumsum(splits)

        # CV: average of the two lowest speeds among splits 9-12
        speeds_late = speeds[8:12]
        CV = np.mean(np.sort(speeds_late)[:2])

        # Dprime via trapezoidal formula from your Excel approach
        # Dprime = (speeds[0] - CV)*splits[0] + sum(i=1..11)[(speeds[i] - CV)*splits[i] + 0.5*(speeds[i-1]-speeds[i])*splits[i]]
        Dprime = (speeds[0] - CV) * splits[0]
        for i in range(1, len(splits)):
            Dprime += ((speeds[i] - CV) * splits[i]) + 0.5 * ((speeds[i-1] - speeds[i]) * splits[i])

        # Peak Speed & Drop Off
        peak_speed = speeds[0]  # from first rep
        drop_off = ((peak_speed - CV) / peak_speed) * 100

        # LC & SC conversions for CV
        CS_SCM = 0.8518 * CV + 0.0925
        CS_LCM = CS_SCM * 0.9554 - 0.0091

        pace_SCM = format_pace(100 / CS_SCM)
        pace_LCM = format_pace(100 / CS_LCM)

        # Attach new columns to the subset
        swimmer_data = swimmer_data.copy()
        swimmer_data['Dprime'] = Dprime
        swimmer_data['CV'] = CV
        swimmer_data['Peak Speed'] = peak_speed
        swimmer_data['Drop off %'] = drop_off
        swimmer_data['CS_SCM Pace'] = pace_SCM
        swimmer_data['CS_LCM Pace'] = pace_LCM

else:
    # If Dprime & CV exist, but we still might need to compute other derived metrics
    row = swimmer_data.iloc[0]
    if all(col in swimmer_data.columns for col in split_cols):
        splits = np.array([row[col] for col in split_cols], dtype=float)
        speeds = 25 / splits
        peak_speed = speeds[0]
        CV = row['CV']
        drop_off = ((peak_speed - CV) / peak_speed) * 100
        CS_SCM = 0.8518 * CV + 0.0925
        CS_LCM = CS_SCM * 0.9554 - 0.0091

        pace_SCM = format_pace(100 / CS_SCM)
        pace_LCM = format_pace(100 / CS_LCM)

        swimmer_data = swimmer_data.copy()
        swimmer_data['Peak Speed'] = peak_speed
        swimmer_data['Drop off %'] = drop_off
        swimmer_data['CS_SCM Pace'] = pace_SCM
        swimmer_data['CS_LCM Pace'] = pace_LCM

###############################################################################
# STEP 2: Display Key Metrics and Export Function
###############################################################################
# Create a function to generate PDF export
def create_export_pdf(swimmer_name=None, swimmer_df=None):
    old_autolayout = mpl.rcParams.get('figure.autolayout', False)
    mpl.rcParams['figure.autolayout'] = False
    try:
        if swimmer_name is None:
            swimmer_name = swimmer
        if swimmer_df is None:
            swimmer_df = swimmer_data
        # Get logo from session state
        logo_img = None
        logo_option = st.session_state.get('logo_option', 'default')
        
        if logo_option == 'upload' and 'uploaded_logo' in st.session_state:
            try:
                logo_img = plt.imread(BytesIO(st.session_state['uploaded_logo']))
            except Exception:
                logo_img = None
        elif logo_option == 'default':
            try:
                logo_img = plt.imread("logo.jpg")
            except Exception:
                # If default logo doesn't exist, skip it
                logo_img = None
        # If logo_option == 'none', logo_img stays None

        def _add_logo_footer(fig):
            if logo_img is None:
                return
            logo_ax = fig.add_axes([0.4, 0.005, 0.2, 0.045])
            logo_ax.axis('off')
            logo_ax.add_patch(Rectangle(
                (0, 0), 1, 1, transform=logo_ax.transAxes,
                facecolor='white', edgecolor='none', zorder=0
            ))
            logo_ax.imshow(logo_img, zorder=1)

        def _format_date_compact(value):
            if isinstance(value, pd.Timestamp):
                return value.strftime('%d-%m-%y')
            if isinstance(value, str):
                try:
                    return pd.to_datetime(value, dayfirst=True).strftime('%d-%m-%y')
                except Exception:
                    return value
            return str(value) if value is not None else 'N/A'

        def _format_header_date(value):
            date_val = pd.to_datetime(value, errors='coerce', dayfirst=True)
            if pd.notna(date_val):
                return date_val.strftime('%B %Y')
            return str(value) if value else 'N/A'

        def _apply_date_locator(ax, date_values):
            if not date_values:
                return
            dates_clean = [d for d in date_values if pd.notna(d)]
            if not dates_clean:
                return
            min_date = min(dates_clean)
            max_date = max(dates_clean)
            span_days = (max_date - min_date).days if max_date and min_date else 0
            if span_days <= 180:
                locator = mdates.MonthLocator(interval=1)
                formatter = mdates.DateFormatter('%b-%y')
            elif span_days <= 730:
                locator = mdates.MonthLocator(interval=3)
                formatter = mdates.DateFormatter('%b-%y')
            else:
                locator = mdates.YearLocator()
                formatter = mdates.DateFormatter('%Y')
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)

        def _arrow(curr_val, prev_val, higher_is_better=True):
            if curr_val is None or prev_val is None:
                return "", COLOR_SECONDARY_TEXT
            if np.isnan(curr_val) or np.isnan(prev_val):
                return "", COLOR_SECONDARY_TEXT
            if curr_val == prev_val:
                return "→", COLOR_SECONDARY_TEXT
            improved = curr_val > prev_val if higher_is_better else curr_val < prev_val
            return ("↑", COLOR_GREEN) if improved else ("↓", COLOR_RED)

        row = swimmer_df.iloc[0]
        stroke_str = row.get('Stroke', 'N/A')
        date_str = _format_date_compact(row.get('Date', 'N/A'))
        header_date_str = _format_header_date(row.get('Date', 'N/A'))
        header_subtitle = f"{header_date_str} - {stroke_str}" if stroke_str else header_date_str

        current_metrics = _metrics_for_row(row)
        if current_metrics is None:
            st.error("Missing split time data for export.")
            return None

        # Historical data for same swimmer and stroke
        history = data[data['Swimmer'] == swimmer_name]
        if stroke_str:
            history = history[history['Stroke'] == stroke_str]
        history = history.copy()
        history['_date'] = pd.to_datetime(history['Date'], errors='coerce', dayfirst=True)
        history = history.sort_values('_date')

        current_date = pd.to_datetime(row.get('Date'), errors='coerce', dayfirst=True)
        prev_row = None
        if not history.empty and pd.notna(current_date):
            prev_rows = history[history['_date'] < current_date]
            if not prev_rows.empty:
                prev_row = prev_rows.iloc[-1]

        prev_metrics = _metrics_for_row(prev_row) if prev_row is not None else None

        # Build key metric cards with delta pills (higher is better except time-based pace)
        metric_cards = [
            {
                "label": "D'",
                "value": f"{current_metrics['dprime']:.2f}",
                "compare_curr": current_metrics['dprime'],
                "compare_prev": prev_metrics['dprime'] if prev_metrics else None,
                "higher_is_better": True,
            },
            {
                "label": "Peak Speed",
                "value": f"{current_metrics['peak_speed']:.2f} m/s",
                "compare_curr": current_metrics['peak_speed'],
                "compare_prev": prev_metrics['peak_speed'] if prev_metrics else None,
                "higher_is_better": True,
            },
            {
                "label": "Critical Velocity",
                "value": f"{current_metrics['cv']:.2f} m/s",
                "compare_curr": current_metrics['cv'],
                "compare_prev": prev_metrics['cv'] if prev_metrics else None,
                "higher_is_better": True,
            },
            {
                "label": "Drop off %",
                "value": f"{current_metrics['drop_off']:.2f}%",
                "compare_curr": current_metrics['drop_off'],
                "compare_prev": prev_metrics['drop_off'] if prev_metrics else None,
                "higher_is_better": True,
                "delta_mode": "dropoff",
            },
            {
                "label": "CS - SCM Pace",
                "value": current_metrics['pace_scm_str'],
                "compare_curr": current_metrics['pace_scm_sec'],
                "compare_prev": prev_metrics['pace_scm_sec'] if prev_metrics else None,
                "higher_is_better": False,
            },
            {
                "label": "CS - LCM Pace",
                "value": current_metrics['pace_lcm_str'],
                "compare_curr": current_metrics['pace_lcm_sec'],
                "compare_prev": prev_metrics['pace_lcm_sec'] if prev_metrics else None,
                "higher_is_better": False,
            },
        ]

        A4_SIZE = (8.27, 11.69)
        buf = BytesIO()
        with PdfPages(buf) as pdf:
            # ------------------------------------------------------------------
            # Page 1: Summary + Velocity Curve + Table
            # ------------------------------------------------------------------
            fig = plt.figure(figsize=A4_SIZE)
            fig.patch.set_facecolor('white')

            fig.text(0.06, 0.94, f"{swimmer_name}", ha='left', va='center',
                     fontsize=24, fontweight='bold', color=COLOR_NAVY)
            fig.text(0.06, 0.905, header_subtitle, ha='left', va='center',
                     fontsize=14, color=COLOR_NAVY, style='italic')

            # Metrics cards - positioned closer to header
            gs_metrics = fig.add_gridspec(
                1, 6,
                left=0.06,
                right=0.94,
                top=0.88,
                bottom=0.78,
                wspace=0.65
            )

            for idx, metric in enumerate(metric_cards):
                ax_metric = fig.add_subplot(gs_metrics[0, idx])
                ax_metric.set_xlim(0, 1)
                ax_metric.set_ylim(0, 1)
                ax_metric.set_box_aspect(1)
                ax_metric.axis('off')

                delta = _delta_percent(
                    metric["compare_curr"],
                    metric["compare_prev"],
                    metric["higher_is_better"]
                )
                circle_color, pill_color = _metric_color_styles(
                    delta,
                    metric.get("delta_mode", "improve")
                )

                circle_center = (0.5, 0.6)
                circle_radius = 0.42
                ax_metric.add_patch(Circle(circle_center, circle_radius,
                                           transform=ax_metric.transAxes,
                                           color=circle_color, ec='none'))

                ax_metric.text(circle_center[0], circle_center[1],
                               f"{metric['value']}",
                               ha='center', va='center', fontsize=9.5,
                               color=COLOR_TEXT, fontweight='bold')

                ax_metric.text(0.5, 0.08, metric["label"],
                               ha='center', va='center', fontsize=7.5,
                               color=COLOR_SECONDARY_TEXT)

                if pill_color and delta is not None:
                    arrow = "↑" if delta > 0 else "↓"
                    pill_text = f"{arrow} {delta:+.0f}%"
                    ax_metric.text(0.78, 0.82,
                                   pill_text,
                                   ha='center', va='center',
                                   fontsize=7, color='white',
                                   bbox=dict(boxstyle="round,pad=0.25",
                                             facecolor=pill_color, edgecolor='none'))

            # Velocity curve - reduced height and moved up
            ax_vel = fig.add_axes([0.08, 0.56, 0.84, 0.20])
            ax_vel.set_facecolor('white')
            ax_vel.plot(current_metrics['cum_time'], current_metrics['speeds'],
                        marker='o', color=COLOR_BLUE, label="Velocity")
            ax_vel.axhline(y=current_metrics['cv'], color=COLOR_RED, linestyle='--',
                           label="Critical Velocity")
            ax_vel.fill_between(
                current_metrics['cum_time'],
                current_metrics['cv'],
                current_metrics['speeds'],
                where=(current_metrics['speeds'] > current_metrics['cv']),
                color=COLOR_LIGHT_BLUE,
                alpha=0.3,
                label="D' Area"
            )
            ax_vel.set_title("Velocity Curve", fontsize=11, color=COLOR_NAVY)
            ax_vel.set_xlabel("Cumulative Time (s)")
            ax_vel.set_ylabel("Velocity (m/s)")
            ax_vel.legend(loc='upper right', fontsize=8)
            ax_vel.grid(True, color='#e5e7eb', linewidth=0.6)

            # Data table (Rep columns) - positioned with more space from plot, closer to title
            fig.text(0.06, 0.425, "Summary table", ha='left', va='center',
                     fontsize=10, fontweight='bold', color=COLOR_NAVY)
            ax_table = fig.add_axes([0.06, 0.28, 0.88, 0.15])
            ax_table.axis('off')

            rep_cols = [str(i) for i in range(1, 13)]
            stroke_rate_cols = [f"Stroke Rate {i}" for i in range(1, 13)]
            stroke_count_cols = [f"Stroke Count {i}" for i in range(1, 13)]
            #sei_cols = [f"Stroke Efficiency Index {i}" for i in range(1, 13)]

            splits = current_metrics['splits']
            #speeds = current_metrics['speeds']
            stroke_rates = [_to_float(row.get(col)) for col in stroke_rate_cols]
            stroke_counts = [_to_float(row.get(col)) for col in stroke_count_cols]
            #sei_vals = [_to_float(row.get(col)) for col in sei_cols]

            table_rows = [
                [f"{v:.2f}" if not np.isnan(v) else "N/A" for v in splits],
                [f"{v:.1f}" if not np.isnan(v) else "N/A" for v in stroke_rates],
                [f"{v:.1f}" if not np.isnan(v) else "N/A" for v in stroke_counts],
                #[f"{v:.2f}" if not np.isnan(v) else "N/A" for v in sei_vals],
                #[f"{v:.2f}" if not np.isnan(v) else "N/A" for v in speeds],
            ]
            row_labels = ["Time (s)", "SR", "SC"]
            #row_labels = ["Time (s)", "Stroke Rate", "Stroke Count", "SEI", "Velocity (m/s)"]
            table_data = [[label] + row for label, row in zip(row_labels, table_rows)]
            col_labels = ["Metric"] + rep_cols

            table = ax_table.table(
                cellText=table_data,
                colLabels=col_labels,
                cellLoc='center',
                loc='center'
            )
            table.auto_set_font_size(False)
            table.set_fontsize(7)
            table.scale(1, 1.4)

            for (r, c), cell in table.get_celld().items():
                cell.set_edgecolor('#e5e7eb')
                if r == 0:
                    cell.set_facecolor(COLOR_NAVY)
                    cell.set_text_props(color='white', weight='bold')
                elif c == 0:
                    cell.set_facecolor(COLOR_GRAY)
                    cell.set_text_props(color=COLOR_TEXT, weight='bold')
                else:
                    cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f9fafb')

            _add_logo_footer(fig)
            pdf.savefig(fig)
            plt.close(fig)

            # ------------------------------------------------------------------
            # Page 2: Percentiles + Density Charts
            # ------------------------------------------------------------------
            fig = plt.figure(figsize=A4_SIZE)
            fig.patch.set_facecolor('white')
            fig.text(0.5, 0.965, "Performance Ranking", ha='center', va='center',
                     fontsize=15, fontweight='bold', color=COLOR_NAVY)

            swimmer_gender = row.get('Gender', 'Male')
            pb_100m = _to_float(row.get('100 m PB', np.nan))
            filtered_percentile_data = [
                d for d in percentile_reference_data
                if d.get('Gender') == swimmer_gender and d.get('Stroke') == stroke_str
            ]

            gs = fig.add_gridspec(
                3, 3,
                height_ratios=[1.2, 1, 1],
                hspace=0.25,
                wspace=0.25,
                left=0.12,
                right=0.94,
                top=0.92,
                bottom=0.08
            )

            if filtered_percentile_data and pb_100m and not pd.isna(pb_100m):
                peak_speed_val = current_metrics['peak_speed']
                cv_val = current_metrics['cv']
                dprime_val = current_metrics['dprime']
                pb_velocity = 100 / pb_100m

                rel_peak_speed = (peak_speed_val / pb_velocity) * 100
                rel_cs = (cv_val / pb_velocity) * 100
                asr = ((peak_speed_val - cv_val) / peak_speed_val) * 100

                ref_ps = [d['PS'] for d in filtered_percentile_data]
                ref_cs = [d['CS'] for d in filtered_percentile_data]
                ref_d = [d['D'] for d in filtered_percentile_data]
                ref_rel_ps = [d['RelPS'] * 100 for d in filtered_percentile_data]
                ref_rel_cs = [d['RelCS'] * 100 for d in filtered_percentile_data]
                ref_asr = [d['ASR'] * 100 for d in filtered_percentile_data]

                percentiles = {
                    'Peak Speed': calculate_percentile(ref_ps, peak_speed_val),
                    'Critical Speed': calculate_percentile(ref_cs, cv_val),
                    "D'": calculate_percentile(ref_d, dprime_val),
                    'Relative Peak Speed': calculate_percentile(ref_rel_ps, rel_peak_speed),
                    'Relative Critical Speed': calculate_percentile(ref_rel_cs, rel_cs),
                    'Anaerobic Speed Reserve': calculate_percentile(ref_asr, asr),
                }

                metrics = list(percentiles.keys())[::-1]
                values = [percentiles[m] for m in metrics]

                def _gradient_color(value):
                    if value < 50:
                        r = 255
                        g = int(255 * (value / 50))
                        b = 0
                    else:
                        r = int(255 * (1 - (value - 50) / 50))
                        g = int(180 + 75 * ((value - 50) / 50))
                        b = int(80 * ((value - 50) / 50))
                    return (r / 255, g / 255, b / 255)

                colors = [_gradient_color(v) for v in values]
                ax_percentile = fig.add_subplot(gs[0, :])
                ax_percentile.barh(metrics, values, color=colors)
                ax_percentile.set_xlim(0, 100)
                ax_percentile.set_xlabel("Percentile")
                ax_percentile.set_title("Cohort Ranking", fontsize=11, color=COLOR_NAVY)
                for i, v in enumerate(values):
                    ax_percentile.text(v + 1, i, f"{v:.0f}", va='center', fontsize=8, color=COLOR_TEXT)
                ax_percentile.grid(True, axis='x', color='#e5e7eb', linewidth=0.6)
                ax_percentile.tick_params(axis='y', labelsize=5, pad=3)

                def _quantiles(values):
                    vals = np.array(values, dtype=float)
                    return np.quantile(vals, [0.1, 0.5, 0.9])

                def _density_chart(ax, ref_values, swimmer_value, quantiles, title, color):
                    ax.hist(ref_values, bins=30, density=True, color=color, alpha=0.3)
                    for q in quantiles:
                        ax.axvline(q, color='gray', linewidth=1, linestyle=':')
                    ax.axvline(swimmer_value, color='gold', linewidth=2.5, linestyle='--')
                    ax.set_title(title, fontsize=8, color=COLOR_NAVY)
                    ax.set_yticks([])
                    ax.grid(False)
                    ax.set_box_aspect(0.75)

                charts = [
                    (ref_ps, peak_speed_val, _quantiles(ref_ps), "Peak Speed (m/s)", '#3B82F6'),
                    (ref_cs, cv_val, _quantiles(ref_cs), "Critical Speed (m/s)", '#EF4444'),
                    (ref_d, dprime_val, _quantiles(ref_d), "D' (m)", '#10B981'),
                    (ref_rel_ps, rel_peak_speed, _quantiles(ref_rel_ps), "Relative Peak Speed (%)", '#3B82F6'),
                    (ref_rel_cs, rel_cs, _quantiles(ref_rel_cs), "Relative Critical Speed (%)", '#EF4444'),
                    (ref_asr, asr, _quantiles(ref_asr), "Anaerobic Speed Reserve (%)", '#10B981'),
                ]

                for idx, (ref_vals, swim_val, quant, title, color) in enumerate(charts):
                    r = 1 + (idx // 3)
                    c = idx % 3
                    ax = fig.add_subplot(gs[r, c])
                    _density_chart(ax, ref_vals, swim_val, quant, title, color)

            else:
                fig.text(0.5, 0.5,
                         "Percentile analysis requires Gender, Stroke, and 100m PB data.",
                         ha='center', va='center', fontsize=10, color=COLOR_SECONDARY_TEXT)

            _add_logo_footer(fig)
            pdf.savefig(fig)
            plt.close(fig)

            # ------------------------------------------------------------------
            # Page 3: Historical Trends (conditional)
            # ------------------------------------------------------------------
            if len(history) > 1:
                fig = plt.figure(figsize=A4_SIZE)
                fig.patch.set_facecolor('white')
                fig.text(0.5, 0.965, "Historical Analysis", ha='center', va='center',
                         fontsize=15, fontweight='bold', color=COLOR_NAVY)

                # Velocity curve overlay
                ax_hist_vel = fig.add_axes([0.08, 0.62, 0.84, 0.28])
                ax_hist_vel.set_facecolor('white')

                color_cycle = [COLOR_BLUE, COLOR_NAVY, COLOR_GREEN, COLOR_RED, COLOR_PURPLE, '#f97316']
                history_rows = []
                color_idx = 0
                for _, hist_row in history.iterrows():
                    hist_metrics = _metrics_for_row(hist_row)
                    if hist_metrics is None:
                        continue
                    hist_date = pd.to_datetime(hist_row.get('Date'), errors='coerce', dayfirst=True)
                    history_rows.append((hist_row, hist_metrics, hist_date))
                    label = _format_date_compact(hist_row.get('Date', ''))
                    ax_hist_vel.plot(
                        hist_metrics['cum_time'],
                        hist_metrics['speeds'],
                        marker='o',
                        linewidth=1.5,
                        color=color_cycle[color_idx % len(color_cycle)],
                        label=label
                    )
                    color_idx += 1

                ax_hist_vel.set_title("Historical Velocity Curves", fontsize=11, color=COLOR_NAVY)
                ax_hist_vel.set_xlabel("Cumulative Time (s)")
                ax_hist_vel.set_ylabel("Velocity (m/s)")
                ax_hist_vel.grid(True, color='#e5e7eb', linewidth=0.6)
                ax_hist_vel.legend(fontsize=7, ncol=2, loc='upper right')

                if len(history_rows) < 2:
                    plt.close(fig)
                else:
                    # Trend plots
                    ax_ps = fig.add_axes([0.08, 0.40, 0.26, 0.16])
                    ax_cs = fig.add_axes([0.38, 0.40, 0.26, 0.16])
                    ax_d = fig.add_axes([0.68, 0.40, 0.26, 0.16])

                    dates = []
                    ps_vals = []
                    cs_vals = []
                    d_vals = []
                    for _, metrics, hist_date in history_rows:
                        if pd.isna(hist_date):
                            continue
                        dates.append(hist_date)
                        ps_vals.append(metrics['peak_speed'])
                        cs_vals.append(metrics['cv'])
                        d_vals.append(metrics['dprime'])

                    for ax, vals, title, color in [
                        (ax_ps, ps_vals, "Peak Speed", COLOR_BLUE),
                        (ax_cs, cs_vals, "Critical Speed", COLOR_RED),
                        (ax_d, d_vals, "D'", COLOR_GREEN),
                    ]:
                        ax.plot(dates, vals, marker='o', color=color, linewidth=1.5)
                        ax.set_title(title, fontsize=9, color=COLOR_NAVY)
                        _apply_date_locator(ax, dates)
                        ax.tick_params(axis='x', rotation=45, labelsize=7)
                        ax.grid(True, color='#e5e7eb', linewidth=0.6)

                    # Historical table at bottom
                    fig.text(0.06, 0.25, "Summary table", ha='left', va='center',
                     fontsize=10, fontweight='bold', color=COLOR_NAVY)
                    ax_hist_table = fig.add_axes([0.06, 0.05, 0.88, 0.28])
                    ax_hist_table.axis('off')

                    history_table = []
                    for hist_row, _, _ in history_rows:
                        date_label = _format_date_compact(hist_row.get('Date', ''))
                        splits_row = [_to_float(hist_row.get(col)) for col in split_cols]
                        row_vals = [date_label] + [
                            f"{v:.2f}" if not np.isnan(v) else "N/A" for v in splits_row
                        ]
                        history_table.append(row_vals)

                    col_labels = ["Date"] + [str(i) for i in range(1, 13)]
                    table = ax_hist_table.table(
                        cellText=history_table,
                        colLabels=col_labels,
                        cellLoc='center',
                        loc='center'
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(7)
                    table.scale(1, 1.3)

                    for (r, c), cell in table.get_celld().items():
                        cell.set_edgecolor('#e5e7eb')
                        if r == 0:
                            cell.set_facecolor(COLOR_NAVY)
                            cell.set_text_props(color='white', weight='bold')
                        else:
                            cell.set_facecolor('#ffffff' if r % 2 == 0 else '#f9fafb')

                    _add_logo_footer(fig)
                    pdf.savefig(fig)
                    plt.close(fig)

        buf.seek(0)
        return buf
    except Exception as e:
        st.error(f"Error generating export: {e}")
        return None
    finally:
        mpl.rcParams['figure.autolayout'] = old_autolayout

# Function to create a download link
def get_download_link(buffer, filename, text):
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">{text}</a>'
    return href

@st.dialog("PDF Preview")
def _show_pdf_dialog():
    preview = st.session_state.get("pdf_preview", {})
    pdf_bytes = preview.get("bytes")
    if not pdf_bytes:
        st.write("No PDF preview available.")
        if st.button("Close"):
            st.session_state["show_pdf_dialog"] = False
        return

    st.markdown(
        f"<div style='margin:4px 0 8px 0; font-size:12px; color:#6B7280;'>"
        f"{preview.get('swimmer', '')} | {preview.get('stroke', '')} | {preview.get('date', '')}"
        f"</div>",
        unsafe_allow_html=True
    )
    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    st.markdown(
        f"<iframe src='data:application/pdf;base64,{b64_pdf}' "
        f"width='100%' height='700px' style='border:1px solid #e5e7eb; border-radius:4px;'></iframe>",
        unsafe_allow_html=True
    )
    if st.download_button(
        "Download PDF",
        data=pdf_bytes,
        file_name=preview.get("filename", "report.pdf"),
        mime="application/pdf"
    ):
        tracker.track_pdf_download(preview.get("swimmer", "unknown"))
    if st.button("Close"):
        st.session_state["show_pdf_dialog"] = False

if st.session_state.pop("request_export", False):
    st.session_state["show_bulk_export_dialog"] = False
    tracker.track_pdf_export(swimmer, stroke_str, date_str)
    pdf_buffer = create_export_pdf()
    if pdf_buffer:
        st.session_state["pdf_preview"] = {
            "bytes": pdf_buffer.getvalue(),
            "filename": f"{swimmer}_report.pdf",
            "swimmer": swimmer,
            "stroke": stroke_str,
            "date": date_str,
        }
        st.session_state["show_pdf_dialog"] = True
    else:
        st.session_state["show_pdf_dialog"] = False

if st.session_state.get("show_pdf_dialog"):
    _show_pdf_dialog()

@st.dialog("Bulk Export Reports")
def _show_bulk_export_dialog():
    st.markdown(
        """
        <style>
        div[data-testid="stDialog"] > div {
            width: 900px;
            max-width: 90vw;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if "bulk_selected" not in st.session_state:
        st.session_state["bulk_selected"] = []
    if "bulk_export_zip" not in st.session_state:
        st.session_state["bulk_export_zip"] = None

    date_series = pd.to_datetime(data['Date'], errors='coerce', dayfirst=True)
    available_dates = sorted(date_series.dropna().unique())
    if not available_dates:
        st.info("No test dates available for bulk export.")
        if st.button("Close"):
            st.session_state["show_bulk_export_dialog"] = False
        return

    date_display = [_format_date_display(date_val) for date_val in available_dates]
    date_map = dict(zip(date_display, available_dates))
    selected_date_label = st.selectbox("Date of test", date_display, key="bulk_export_date")
    selected_date = date_map[selected_date_label]

    swimmers_for_date = sorted(
        data.loc[date_series == selected_date, 'Swimmer'].dropna().unique().tolist()
    )

    search_text = st.text_input("Search", key="bulk_export_search")
    available_options = [
        name for name in swimmers_for_date
        if name not in st.session_state["bulk_selected"]
    ]
    if search_text:
        available_options = [
            name for name in available_options
            if search_text.lower() in name.lower()
        ]

    col_left, col_mid, col_right = st.columns([5, 2, 5])
    with col_left:
        st.markdown("**Available options**")
        available_pick = st.multiselect(
            " ",
            available_options,
            default=[],
            key="bulk_available_pick"
        )
    with col_mid:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        add_all = st.button("▶▶ Add All", key="bulk_add_all", use_container_width=True)
        add_one = st.button("▶ Add", key="bulk_add", use_container_width=True)
        remove_one = st.button("◀ Remove", key="bulk_remove", use_container_width=True)
        remove_all = st.button("◀◀ Remove All", key="bulk_remove_all", use_container_width=True)
    with col_right:
        st.markdown("**Selected options**")
        selected_pick = st.multiselect(
            " ",
            st.session_state["bulk_selected"],
            default=[],
            key="bulk_selected_pick"
        )

    rerun_needed = False
    if add_all:
        st.session_state["bulk_selected"] = swimmers_for_date
        rerun_needed = True
    if add_one and available_pick:
        st.session_state["bulk_selected"] = sorted(
            set(st.session_state["bulk_selected"]).union(available_pick)
        )
        rerun_needed = True
    if remove_one and selected_pick:
        st.session_state["bulk_selected"] = [
            name for name in st.session_state["bulk_selected"]
            if name not in selected_pick
        ]
        rerun_needed = True
    if remove_all:
        st.session_state["bulk_selected"] = []
        rerun_needed = True
    if rerun_needed:
        st.rerun()

    st.markdown("---")
    st.markdown(f"**Selected:** {len(st.session_state['bulk_selected'])}")

    export_disabled = len(st.session_state["bulk_selected"]) == 0
    if st.button("Export", type="primary", disabled=export_disabled, key="bulk_export_button"):
        total = len(st.session_state["bulk_selected"])
        tracker.track_bulk_export(total, str(selected_date))
        progress = st.progress(0)
        status = st.empty()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for idx, name in enumerate(st.session_state["bulk_selected"], start=1):
                status.write(f"Generating {name}...")
                swimmer_rows = data[(data['Swimmer'] == name) & (date_series == selected_date)]
                if swimmer_rows.empty:
                    progress.progress(idx / total)
                    continue
                pdf_buffer = create_export_pdf(swimmer_name=name, swimmer_df=swimmer_rows)
                if pdf_buffer:
                    file_date = _format_date_file(selected_date)
                    pdf_filename = f"{name} {file_date} 12x25 Report.pdf"
                    zf.writestr(pdf_filename, pdf_buffer.getvalue())
                progress.progress(idx / total)
        zip_buffer.seek(0)
        st.session_state["bulk_export_zip"] = zip_buffer.getvalue()
        st.session_state["bulk_export_zip_name"] = (
            f"Bulk_Export_{_format_date_file(selected_date)}_12x25_Reports.zip"
        )
        status.write("Export ready.")

    if st.session_state.get("bulk_export_zip"):
        if st.download_button(
            "Download ZIP",
            data=st.session_state["bulk_export_zip"],
            file_name=st.session_state.get("bulk_export_zip_name", "bulk_export.zip"),
            mime="application/zip",
            key="bulk_download_zip"
        ):
            tracker.track_bulk_download(len(st.session_state.get("bulk_selected", [])))

    if st.button("Close", key="bulk_close"):
        st.session_state["show_bulk_export_dialog"] = False

if st.session_state.get("show_bulk_export_dialog"):
    _show_bulk_export_dialog()

# Create a more compact, card-based layout for metrics
metrics_row1, metrics_row2 = st.columns([6, 1])

with metrics_row1:
    current_metrics = _metrics_for_row(row)
    history = data[data['Swimmer'] == swimmer]
    if selected_stroke:
        history = history[history['Stroke'] == selected_stroke]
    history = history.copy()
    history['_date'] = pd.to_datetime(history['Date'], errors='coerce', dayfirst=True)
    history = history.sort_values('_date')
    current_date = pd.to_datetime(row.get('Date'), errors='coerce', dayfirst=True)
    prev_metrics = None
    if not history.empty and pd.notna(current_date):
        prev_rows = history[history['_date'] < current_date]
        if not prev_rows.empty:
            prev_metrics = _metrics_for_row(prev_rows.iloc[-1])

    show_abs_change = st.session_state.get("metric_delta_absolute", False)

    metric_cards = [
        {
            "label": "D'",
            "value": f"{current_metrics['dprime']:.2f}",
            "curr": current_metrics['dprime'],
            "prev": prev_metrics['dprime'] if prev_metrics else None,
            "higher_is_better": True,
            "abs_unit": "m",
        },
        {
            "label": "Critical Velocity",
            "value": f"{current_metrics['cv']:.2f} m/s",
            "curr": current_metrics['cv'],
            "prev": prev_metrics['cv'] if prev_metrics else None,
            "higher_is_better": True,
            "abs_unit": "m/s",
        },
        {
            "label": "Peak Speed",
            "value": f"{current_metrics['peak_speed']:.2f} m/s",
            "curr": current_metrics['peak_speed'],
            "prev": prev_metrics['peak_speed'] if prev_metrics else None,
            "higher_is_better": True,
            "abs_unit": "m/s",
        },
        {
            "label": "Drop off %",
            "value": f"{current_metrics['drop_off']:.2f}%",
            "curr": current_metrics['drop_off'],
            "prev": prev_metrics['drop_off'] if prev_metrics else None,
            "higher_is_better": True,
            "abs_unit": "pp",
            "delta_mode": "dropoff",
        },
        {
            "label": "CS - SCM Pace",
            "value": current_metrics['pace_scm_str'],
            "curr": current_metrics['pace_scm_sec'],
            "prev": prev_metrics['pace_scm_sec'] if prev_metrics else None,
            "higher_is_better": False,
            "abs_unit": "s",
        },
        {
            "label": "CS - LCM Pace",
            "value": current_metrics['pace_lcm_str'],
            "curr": current_metrics['pace_lcm_sec'],
            "prev": prev_metrics['pace_lcm_sec'] if prev_metrics else None,
            "higher_is_better": False,
            "abs_unit": "s",
        },
    ]

    cards_html = "<div style='display:flex; flex-wrap:wrap; gap:12px; margin-bottom:8px;'>"
    for metric in metric_cards:
        if show_abs_change:
            delta = _delta_absolute(metric["curr"], metric["prev"], metric["higher_is_better"])
        else:
            delta = _delta_percent(metric["curr"], metric["prev"], metric["higher_is_better"])
        circle_bg, pill_color = _metric_color_styles(
            delta,
            metric.get("delta_mode", "improve")
        )
        if pill_color is None:
            pill_html = ""
        else:
            arrow = "↑" if delta > 0 else "↓"
            if show_abs_change:
                unit = metric.get("abs_unit", "")
                if unit == "s":
                    delta_str = f"{delta:+.1f}{unit}"
                elif unit == "m/s":
                    delta_str = f"{delta:+.2f}{unit}"
                elif unit == "m":
                    delta_str = f"{delta:+.1f}{unit}"
                elif unit == "pp":
                    delta_str = f"{delta:+.1f}{unit}"
                else:
                    delta_str = f"{delta:+.2f}"
            else:
                delta_str = f"{delta:+.0f}%"

            pill_html = (
                f"<div style='position:absolute; top:6px; right:6px; "
                f"background:{pill_color}; color:white; padding:4px 8px; "
                f"border-radius:999px; font-size:11px; font-weight:600;'>"
                f"{arrow} {delta_str}</div>"
            )

        cards_html += (
            "<div style='flex:1; min-width:120px; text-align:center;'>"
            f"<div style='position:relative; margin:0 auto; width:110px; height:110px; "
            f"border-radius:50%; background:{circle_bg}; display:flex; "
            f"align-items:center; justify-content:center;'>"
            f"<div style='font-size:22px; font-weight:700; color:#111827;'>{metric['value']}</div>"
            f"{pill_html}</div>"
            f"<div style='font-size:12px; color:#6B7280; margin-top:6px;'>{metric['label']}</div>"
            "</div>"
        )

    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

with metrics_row2:
    show_abs_change = st.toggle(
        "Δ / %",
        value=st.session_state.get("metric_delta_absolute", False),
        key="metric_delta_absolute",
        help="Toggle absolute change vs % change for metric pills",
    )

# Create a 2x2 grid for charts using columns
col1, col2 = st.columns(2)

# Velocity Curve Chart
with col1:
    st.markdown("<p style='font-size:14px; font-weight:600; margin:0; color:#1E40AF; border-bottom:1px solid #f0f0f0;'>Velocity Curve</p>", unsafe_allow_html=True)
    
    # Get data for velocity curve
    row = swimmer_data.iloc[0]
    splits = np.array([row[col] for col in split_cols], dtype=float)
    speeds = 25 / splits
    cum_time = np.cumsum(splits)
    CV = swimmer_data['CV'].iloc[0]
    
    # Create velocity curve with Plotly
    fig_velocity = go.Figure()
    
    # Prepend x=0 to start the velocity curve at the y-axis
    velocity_x = np.concatenate([[0], cum_time])
    velocity_y = np.concatenate([[speeds[0]], speeds])
    
    # Add velocity points and line
    fig_velocity.add_trace(go.Scatter(
        x=velocity_x, 
        y=velocity_y, 
        mode='lines+markers',
        name='Velocity',
        line=dict(color=COLOR_BLUE, width=2),
        marker=dict(size=6, color=COLOR_BLUE)
    ))
    
    # Add critical velocity line
    fig_velocity.add_trace(go.Scatter(
        x=[0, cum_time[-1]],
        y=[CV, CV],
        mode='lines',
        name='Critical Velocity',
        line=dict(color=COLOR_RED, width=2, dash='dash')
    ))
    
    # Add D' area - updated to start from x=0
    fig_velocity.add_trace(go.Scatter(
        x=np.concatenate([[0], cum_time, [cum_time[-1]], [0]]),
        y=np.concatenate([[speeds[0]], speeds, [CV], [CV]]),
        fill='toself',
        fillcolor='rgba(147, 197, 253, 0.3)',
        line=dict(color='rgba(0,0,0,0)'),
        name="D' Area",
        showlegend=True
    ))
    
    # Update layout
    fig_velocity.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=200,
        xaxis_title="Cumulative Time (s)",
        yaxis_title="Velocity (m/s)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=8)
        ),
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    )
    
    st.plotly_chart(fig_velocity, use_container_width=True, config={'displayModeBar': False})

# Split Times Chart
with col2:
    st.markdown("<p style='font-size:14px; font-weight:600; margin:0; color:#1E40AF; border-bottom:1px solid #f0f0f0;'>Split Times</p>", unsafe_allow_html=True)
    
    # Create split times chart with Plotly - smooth line with markers
    fig_splits = go.Figure()
    
    # Add split times as smooth line with markers
    fig_splits.add_trace(go.Scatter(
        x=list(range(1, 13)),
        y=splits,
        mode='lines+markers',
        line=dict(color=COLOR_BLUE, width=2, shape='spline', smoothing=1.3),
        marker=dict(size=8, color=COLOR_BLUE),
        name='Split Time'
    ))
    
    # Calculate y-axis range to ensure line doesn't overlap with x-axis
    min_split = min(splits)
    max_split = max(splits)
    y_range = [min_split - 1, max_split + 0.5]
    
    # Update layout
    fig_splits.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=200,
        xaxis_title="Repetition",
        yaxis_title="Time (s)",
        xaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=1,
            showgrid=True, 
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(0,0,0,0.1)',
            range=y_range
        )
    )
    
    st.plotly_chart(fig_splits, use_container_width=True, config={'displayModeBar': False})

# Create another row for additional charts
col3, col4 = st.columns(2)

# Stroke Rate Chart (if available)
with col3:
    stroke_rate_cols = [f"Stroke Rate {i}" for i in range(1, 13)]
    if all(col in swimmer_data.columns for col in stroke_rate_cols):
        st.markdown("<p style='font-size:14px; font-weight:600; margin:0; color:#1E40AF; border-bottom:1px solid #f0f0f0;'>Stroke Rate</p>", unsafe_allow_html=True)
        
        # Get stroke rate data
        stroke_rates = np.array([row[col] for col in stroke_rate_cols], dtype=float)
        
        # Create stroke rate chart with Plotly
        fig_stroke_rate = go.Figure()
        
        # Add stroke rate line
        fig_stroke_rate.add_trace(go.Scatter(
            x=list(range(1, 13)),
            y=stroke_rates,
            mode='lines+markers',
            name='Stroke Rate',
            line=dict(color=COLOR_PURPLE, width=2),
            marker=dict(size=6, color=COLOR_PURPLE)
        ))
        
        # Update layout
        fig_stroke_rate.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=200,
            xaxis_title="Repetition",
            yaxis_title="Stroke Rate (spm)",
            xaxis=dict(
                tickmode='linear',
                tick0=1,
                dtick=1,
                showgrid=True, 
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
        )
        
        st.plotly_chart(fig_stroke_rate, use_container_width=True, config={'displayModeBar': False})
    else:
        st.markdown("<p style='font-size:14px; font-weight:600; margin:0; color:#1E40AF; border-bottom:1px solid #f0f0f0;'>Stroke Rate</p>", unsafe_allow_html=True)
        st.markdown("<div class='info-message'>Stroke rate data not available</div>", unsafe_allow_html=True)

# Stroke Count Chart (if available)
with col4:
    stroke_count_cols = [f"Stroke Count {i}" for i in range(1, 13)]
    if all(col in swimmer_data.columns for col in stroke_count_cols):
        st.markdown("<p style='font-size:14px; font-weight:600; margin:0; color:#1E40AF; border-bottom:1px solid #f0f0f0;'>Stroke Count</p>", unsafe_allow_html=True)
        
        # Get stroke count data
        stroke_counts = np.array([row[col] for col in stroke_count_cols], dtype=float)
        
        # Create stroke count chart with Plotly
        fig_stroke_count = go.Figure()
        
        # Add stroke count line
        fig_stroke_count.add_trace(go.Scatter(
            x=list(range(1, 13)),
            y=stroke_counts,
            mode='lines+markers',
            name='Stroke Count',
            line=dict(color=COLOR_GREEN, width=2),
            marker=dict(size=6, color=COLOR_GREEN)
        ))
        
        # Update layout
        fig_stroke_count.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=200,
            xaxis_title="Repetition",
            yaxis_title="Stroke Count",
            xaxis=dict(
                tickmode='linear',
                tick0=1,
                dtick=1,
                showgrid=True, 
                gridcolor='rgba(0,0,0,0.1)'
            ),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
        )
        
        st.plotly_chart(fig_stroke_count, use_container_width=True, config={'displayModeBar': False})
    else:
        st.markdown("<p style='font-size:14px; font-weight:600; margin:0; color:#1E40AF; border-bottom:1px solid #f0f0f0;'>Stroke Count</p>", unsafe_allow_html=True)
        st.markdown("<div class='info-message'>Stroke count data not available</div>", unsafe_allow_html=True)

###############################################################################
# PERCENTILE ANALYSIS SECTION
###############################################################################
st.markdown("<p style='font-size:14px; font-weight:600; margin:10px 0 5px 0; color:#1E40AF; border-bottom:1px solid #f0f0f0;'>Percentile Analysis</p>", unsafe_allow_html=True)
st.markdown("<p style='font-size:9px; color:#6B7280; margin-bottom:5px;'>Dotted lines denote the 10th, 50th and 90th percentiles. Gold line shows swimmer's value.</p>", unsafe_allow_html=True)

# Get swimmer's gender and stroke for filtering
swimmer_gender = row.get('Gender', 'Male')
swimmer_stroke = row.get('Stroke', 'Freestyle')
pb_100m = row.get('100 m PB', None)

# Filter percentile reference data by gender and stroke
filtered_percentile_data = [d for d in percentile_reference_data 
                            if d.get('Gender') == swimmer_gender and d.get('Stroke') == swimmer_stroke]

if filtered_percentile_data and pb_100m and not pd.isna(pb_100m):
    # Calculate swimmer's metrics
    peak_speed_val_num = swimmer_data['Peak Speed'].iloc[0]
    cv_val_num = swimmer_data['CV'].iloc[0]
    dprime_val_num = swimmer_data['Dprime'].iloc[0]
    pb_velocity = 100 / pb_100m  # Convert 100m PB time to velocity
    
    rel_peak_speed = (peak_speed_val_num / pb_velocity) * 100
    rel_cs = (cv_val_num / pb_velocity) * 100
    asr = ((peak_speed_val_num - cv_val_num) / peak_speed_val_num) * 100
    
    # Extract reference values for each metric
    ref_ps = [d['PS'] for d in filtered_percentile_data]
    ref_cs = [d['CS'] for d in filtered_percentile_data]
    ref_d = [d['D'] for d in filtered_percentile_data]
    ref_rel_ps = [d['RelPS'] * 100 for d in filtered_percentile_data]
    ref_rel_cs = [d['RelCS'] * 100 for d in filtered_percentile_data]
    ref_asr = [d['ASR'] * 100 for d in filtered_percentile_data]
    
    # Calculate percentiles for each metric
    percentiles = {
        'Peak Speed': calculate_percentile(ref_ps, peak_speed_val_num),
        'Critical Speed': calculate_percentile(ref_cs, cv_val_num),
        "D'": calculate_percentile(ref_d, dprime_val_num),
        'Relative Peak Speed': calculate_percentile(ref_rel_ps, rel_peak_speed),
        'Relative Critical Speed': calculate_percentile(ref_rel_cs, rel_cs),
        'Anaerobic Speed Reserve': calculate_percentile(ref_asr, asr)
    }
    
    # Calculate quantiles (10th, 50th, 90th) for each metric
    def get_quantiles(values):
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        return {
            'p10': sorted_vals[int(n * 0.10)],
            'p50': sorted_vals[int(n * 0.50)],
            'p90': sorted_vals[int(n * 0.90)]
        }
    
    quantiles_ps = get_quantiles(ref_ps)
    quantiles_cs = get_quantiles(ref_cs)
    quantiles_d = get_quantiles(ref_d)
    quantiles_rel_ps = get_quantiles(ref_rel_ps)
    quantiles_rel_cs = get_quantiles(ref_rel_cs)
    quantiles_asr = get_quantiles(ref_asr)
    
    # Create horizontal bar chart for percentiles
    perc_col1, perc_col2 = st.columns([1, 2])
    
    with perc_col1:
        # Horizontal bar chart with gradient colors
        metric_names = list(percentiles.keys())[::-1]  # Reverse for bottom-to-top display
        metric_values = [percentiles[m] for m in metric_names]
        
        # Create color gradient (red -> gold -> green)
        def get_gradient_color(value):
            if value < 50:
                # Red to Gold
                r = 255
                g = int(255 * (value / 50))
                b = 0
            else:
                # Gold to Green
                r = int(255 * (1 - (value - 50) / 50))
                g = int(180 + 75 * ((value - 50) / 50))
                b = int(80 * ((value - 50) / 50))
            return f'rgb({r},{g},{b})'
        
        bar_colors = [get_gradient_color(v) for v in metric_values]
        
        fig_percentile_bar = go.Figure()
        fig_percentile_bar.add_trace(go.Bar(
            y=metric_names,
            x=metric_values,
            orientation='h',
            marker=dict(color=bar_colors),
            text=[f'{v:.0f}' for v in metric_values],
            textposition='inside',
            textfont=dict(color='white', size=10)
        ))
        
        fig_percentile_bar.update_layout(
            margin=dict(l=0, r=10, t=5, b=5),
            height=250,
            xaxis=dict(title='Percentile', range=[0, 100], showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(title=''),
            showlegend=False
        )
        
        st.plotly_chart(fig_percentile_bar, use_container_width=True, config={'displayModeBar': False})
    
    with perc_col2:
        # Create 2 rows of 3 density charts
        density_row1_cols = st.columns(3)
        density_row2_cols = st.columns(3)
        
        # Helper function to create density chart
        def create_density_chart(ref_values, swimmer_value, quantiles, title, fill_color, height=120):
            fig = go.Figure()
            
            # Create histogram as approximation of density
            fig.add_trace(go.Histogram(
                x=ref_values,
                nbinsx=30,
                histnorm='probability density',
                marker=dict(color=fill_color, line=dict(width=0)),
                opacity=0.3,
                showlegend=False
            ))
            
            # Add quantile lines (10th, 50th, 90th)
            for q_val in [quantiles['p10'], quantiles['p50'], quantiles['p90']]:
                fig.add_vline(x=q_val, line=dict(color='gray', width=1, dash='dot'))
            
            # Add swimmer's value line (gold, dashed, bold)
            fig.add_vline(x=swimmer_value, line=dict(color='gold', width=3, dash='dash'))
            
            fig.update_layout(
                margin=dict(l=5, r=5, t=20, b=5),
                height=height,
                title=dict(text=title, font=dict(size=9), x=0.5),
                xaxis=dict(title='', showgrid=False, tickfont=dict(size=7)),
                yaxis=dict(visible=False),
                showlegend=False
            )
            
            return fig
        
        # Row 1: Peak Speed, Critical Speed, D'
        with density_row1_cols[0]:
            fig = create_density_chart(ref_ps, peak_speed_val_num, quantiles_ps, 
                                       'Peak Speed (m/s)', 'rgba(70, 130, 180, 0.5)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with density_row1_cols[1]:
            fig = create_density_chart(ref_cs, cv_val_num, quantiles_cs,
                                       'Critical Speed (m/s)', 'rgba(178, 34, 34, 0.3)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with density_row1_cols[2]:
            fig = create_density_chart(ref_d, dprime_val_num, quantiles_d,
                                       "D' (m)", 'rgba(34, 139, 34, 0.3)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Row 2: Relative Peak Speed, Relative Critical Speed, ASR
        with density_row2_cols[0]:
            fig = create_density_chart(ref_rel_ps, rel_peak_speed, quantiles_rel_ps,
                                       'Relative Peak Speed (%)', 'rgba(70, 130, 180, 0.5)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with density_row2_cols[1]:
            fig = create_density_chart(ref_rel_cs, rel_cs, quantiles_rel_cs,
                                       'Relative Critical Speed (%)', 'rgba(178, 34, 34, 0.3)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with density_row2_cols[2]:
            fig = create_density_chart(ref_asr, asr, quantiles_asr,
                                       'Anaerobic Speed Reserve (%)', 'rgba(34, 139, 34, 0.3)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

else:
    st.markdown("<div class='info-message'>Percentile analysis requires Gender, Stroke, and 100m PB data</div>", unsafe_allow_html=True)

###############################################################################
# HISTORICAL ANALYSIS SECTION
###############################################################################
if len(history) > 1:
    history_rows = []
    for _, hist_row in history.iterrows():
        hist_metrics = _metrics_for_row(hist_row)
        if hist_metrics is None:
            continue
        hist_date = pd.to_datetime(hist_row.get('Date'), errors='coerce', dayfirst=True)
        history_rows.append((hist_row, hist_metrics, hist_date))

    if len(history_rows) > 1:
        st.markdown(
            "<p style='font-size:14px; font-weight:600; margin:10px 0 5px 0; color:#1E40AF; "
            "border-bottom:1px solid #f0f0f0;'>Historical Analysis</p>",
            unsafe_allow_html=True
        )

        # Historical velocity curves
        fig_hist_vel = go.Figure()
        color_cycle = [COLOR_BLUE, COLOR_NAVY, COLOR_GREEN, COLOR_RED, COLOR_PURPLE, '#f97316']
        for idx, (_, metrics, hist_date) in enumerate(history_rows):
            label = _format_date_display(hist_date)
            fig_hist_vel.add_trace(go.Scatter(
                x=metrics['cum_time'],
                y=metrics['speeds'],
                mode='lines+markers',
                name=label,
                line=dict(color=color_cycle[idx % len(color_cycle)], width=2),
                marker=dict(size=5)
            ))

        fig_hist_vel.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=240,
            xaxis_title="Cumulative Time (s)",
            yaxis_title="Velocity (m/s)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
        )
        st.markdown("<p style='font-size:13px; font-weight:600; margin:6px 0 4px 0; color:#1E40AF;'>Historical Velocity Curves</p>", unsafe_allow_html=True)
        st.plotly_chart(fig_hist_vel, use_container_width=True, config={'displayModeBar': False})

        # Trend charts
        trend_cols = st.columns(3)
        trend_dates = [row_date for _, _, row_date in history_rows if pd.notna(row_date)]
        trend_ps = [metrics['peak_speed'] for _, metrics, row_date in history_rows if pd.notna(row_date)]
        trend_cv = [metrics['cv'] for _, metrics, row_date in history_rows if pd.notna(row_date)]
        trend_d = [metrics['dprime'] for _, metrics, row_date in history_rows if pd.notna(row_date)]

        for col, values, title, color in [
            (trend_cols[0], trend_ps, "Peak Speed", COLOR_BLUE),
            (trend_cols[1], trend_cv, "Critical Speed", COLOR_RED),
            (trend_cols[2], trend_d, "D'", COLOR_GREEN),
        ]:
            with col:
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=trend_dates,
                    y=values,
                    mode='lines+markers',
                    line=dict(color=color, width=2),
                    marker=dict(size=6)
                ))
                fig_trend.update_layout(
                    margin=dict(l=0, r=0, t=20, b=0),
                    height=180,
                    title=dict(text=title, font=dict(size=11), x=0.5),
                    xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
                )
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

        # Historical splits table
        history_table = []
        for hist_row, _, _ in history_rows:
            date_label = _format_date_display(hist_row.get('Date', ''))
            splits_row = [_to_float(hist_row.get(col)) for col in split_cols]
            row_vals = [
                date_label,
                *[f"{v:.2f}" if not np.isnan(v) else "N/A" for v in splits_row]
            ]
            history_table.append(row_vals)

        hist_columns = ["Date"] + [str(i) for i in range(1, 13)]
        history_df = pd.DataFrame(history_table, columns=hist_columns)
        st.markdown("<p style='font-size:13px; font-weight:600; margin:6px 0 4px 0; color:#1E40AF;'>Historical Splits</p>", unsafe_allow_html=True)
        st.dataframe(history_df, use_container_width=True, hide_index=True)

# Display data table with collapsible expander
with st.expander("📊 View Raw Data", expanded=False):
    # Create a transposed table matching the visual reference
    # Rows: Time, Stroke Rate, Stroke Count, SEI, Velocity
    # Columns: Rep numbers 1-12
    
    # Prepare data rows
    time_row = [f"{splits[i]:.2f}" for i in range(12)]
    velocity_row = [f"{speeds[i]:.2f}" for i in range(12)]
    
    # Build the HTML table
    table_html = """
    <style>
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .custom-table thead tr {
            background-color: #1e3a8a;
            color: white;
            text-align: center;
            font-weight: bold;
        }
        .custom-table th, .custom-table td {
            padding: 8px 10px;
            border: 1px solid #e5e7eb;
            text-align: center;
        }
        .custom-table tbody tr {
            background-color: white;
        }
        .custom-table tbody tr:nth-child(even) {
            background-color: #f9fafb;
        }
        .custom-table tbody tr:hover {
            background-color: #f3f4f6;
        }
        .custom-table .row-label {
            background-color: #1e3a8a;
            color: white;
            font-weight: bold;
            text-align: left;
            padding-left: 15px;
        }
    </style>
    <table class="custom-table">
        <thead>
            <tr>
                <th></th>
    """
    
    # Add column headers (rep numbers 1-12)
    for i in range(1, 13):
        table_html += f"<th>{i}</th>"
    table_html += "</tr></thead><tbody>"
    
    # Add Time row
    table_html += '<tr><td class="row-label">Time (sec)</td>'
    for val in time_row:
        table_html += f"<td>{val}</td>"
    table_html += "</tr>"
    
    # Add Stroke Rate row if available
    if all(col in swimmer_data.columns for col in stroke_rate_cols):
        table_html += '<tr><td class="row-label">Stroke Rate</td>'
        for i in range(12):
            sr_val = row[stroke_rate_cols[i]]
            table_html += f"<td>{sr_val:.1f}</td>"
        table_html += "</tr>"
    
    # Add Stroke Count row if available
    if all(col in swimmer_data.columns for col in stroke_count_cols):
        table_html += '<tr><td class="row-label">Stroke Count</td>'
        for i in range(12):
            sc_val = row[stroke_count_cols[i]]
            table_html += f"<td>{sc_val:.0f}</td>"
        table_html += "</tr>"
    
    # Add Stroke Efficiency Index row if available
    sei_cols = [f"Stroke Efficiency Index {i}" for i in range(1, 13)]
    if all(col in swimmer_data.columns for col in sei_cols):
        table_html += '<tr><td class="row-label">Stroke Efficiency Index</td>'
        for i in range(12):
            sei_val = row[sei_cols[i]]
            table_html += f"<td>{sei_val:.2f}</td>"
        table_html += "</tr>"
    
    # Add Velocity row
    table_html += '<tr><td class="row-label">Velocity</td>'
    for val in velocity_row:
        table_html += f"<td>{val}</td>"
    table_html += "</tr>"
    
    table_html += "</tbody></table>"
    
    st.markdown(table_html, unsafe_allow_html=True)

# Add a footer
st.markdown("<footer>Report generated thanks to Gio Postiglione</footer>", unsafe_allow_html=True)
