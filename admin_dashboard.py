"""
Premium Enterprise HRMS Admin Dashboard
Modern glassmorphism UI with left sidebar navigation
"""
import streamlit as st
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database
from fpdf import FPDF
import io

# Initialize session state for navigation
def init_admin_session():
    if 'admin_page' not in st.session_state:
        st.session_state['admin_page'] = 'dashboard'
    if 'selected_employee' not in st.session_state:
        st.session_state['selected_employee'] = None

def show_premium_admin_dashboard(user):
    """Main entry point for premium admin dashboard"""
    init_admin_session()
    
    # Global CSS for premium glassmorphism design
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* Reset and base styles */
    * { font-family: 'Poppins', sans-serif !important; }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none !important; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 2rem 1rem !important;
    }
    
    /* Sidebar menu items */
    .sidebar-menu-item {
        padding: 12px 20px;
        margin: 6px 0;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
