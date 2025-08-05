import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import xlsxwriter

# Page configuration
st.set_page_config(
    page_title="Route Cost Estimator - Prime Chain Solutions",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with the new design
st.markdown("""
<style>
    :root {
        --navy: #0a1628;
        --navy-light: #1a2332;
        --teal: #0891b2;
        --teal-light: #06b6d4;
        --teal-dark: #0e7490;
        --gold: #f59e0b;
        --gold-light: #fbbf24;
        --charcoal: #1f2937;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-800: #1f2937;
        --gray-900: #111827;
        --white: #ffffff;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--charcoal);
        line-height: 1.6;
        background: var(--gray-50);
    }
    
    /* Header */
    .header {
        background: linear-gradient(135deg, rgba(10, 22, 40, 0.95) 0%, rgba(8, 145, 178, 0.85) 100%);
        color: var(--white);
        padding: 40px 0 80px;
        position: relative;
        overflow: hidden;
        margin-bottom: -40px;
    }
    
    .header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 50%, rgba(8, 145, 178, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(245, 158, 11, 0.15) 0%, transparent 50%);
    }
    
    .header-content {
        position: relative;
        z-index: 2;
        text-align: center;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .header-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 8px 20px;
        border-radius: 50px;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 20px;
    }
    
    .header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 16px;
        letter-spacing: -0.025em;
    }
    
    .header-highlight {
        background: linear-gradient(135deg, var(--teal-light), var(--gold-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Sidebar */
    .sidebar {
        background: var(--white);
        border-radius: 24px;
        box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
        border: 1px solid var(--gray-100);
        overflow: hidden;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, var(--teal-light) 0%, var(--teal-dark) 100%);
        color: var(--white);
        padding: 32px 24px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .sidebar-header h2 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 8px;
        position: relative;
        z-index: 1;
    }
    
    .sidebar-header p {
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    .section-title {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--navy);
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--gray-100);
    }
    
    /* Form elements */
    .stTextInput input, 
    .stNumberInput input,
    .stSelectbox select {
        width: 100%;
        padding: 16px 20px;
        border: 2px solid var(--gray-200);
        border-radius: 12px;
        font-size: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: var(--white);
    }
    
    .stTextInput input:focus, 
    .stNumberInput input:focus,
    .stSelectbox select:focus {
        outline: none;
        border-color: var(--teal);
        box-shadow: 0 0 0 4px rgba(8, 145, 178, 0.1);
    }
    
    /* Calculate button */
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, var(--teal-light) 0%, var(--teal-dark) 100%);
        color: var(--white);
        border: none;
        padding: 20px 32px;
        border-radius: 16px;
        font-size: 1.1rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
    }
    
    /* Metrics cards */
    .metric-card {
        background: var(--white);
        padding: 24px 20px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid var(--gray-100);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--teal);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--teal);
        margin-bottom: 8px;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: var(--gray-800);
        font-weight: 600;
    }
    
    /* Analysis cards */
    .analysis-card {
        background: var(--white);
        border-radius: 20px;
        padding: 32px;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        border: 1px solid var(--gray-100);
    }
    
    .analysis-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .analysis-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--navy);
    }
    
    /* Profit alerts */
    .profit-alert {
        padding: 20px;
        border-radius: 16px;
        margin-top: 20px;
        display: flex;
        align-items: center;
        gap: 16px;
        font-weight: 600;
    }
    
    .profit-alert.success {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.2);
        color: var(--success);
    }
    
    .profit-alert.warning {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.2);
        color: var(--warning);
    }
    
    /* Risk indicators */
    .risk-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .risk-indicator.low {
        background: rgba(16, 185, 129, 0.1);
        color: var(--success);
    }
    
    .risk-indicator.medium {
        background: rgba(245, 158, 11, 0.1);
        color: var(--warning);
    }
    
    .risk-indicator.high {
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger);
    }
    
    /* What-if simulator */
    .simulator-section {
        background: var(--gray-50);
        border-radius: 20px;
        padding: 32px;
        margin: 32px 0;
        border: 1px solid var(--gray-100);
    }
    
    /* Export buttons */
    .export-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 16px 24px;
        border: 2px solid var(--teal);
        background: var(--white);
        color: var(--teal);
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .export-btn:hover {
        background: var(--teal);
        color: var(--white);
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }
    
    /* Welcome state */
    .welcome-icon {
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, var(--teal-light) 0%, var(--teal-dark) 100%);
        border-radius: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 32px;
        font-size: 3rem;
        color: var(--white);
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .header h1 {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Constants
FUEL_CONSUMPTION_PER_KM = 0.35  # litres per km
DRIVER_COST_PER_HOUR = 85  # R per hour
VEHICLE_OPERATING_COST_PER_KM = 4.50  # R per km (maintenance, insurance, depreciation)
ADMIN_OVERHEAD_PERCENTAGE = 0.08  # 8% for admin costs

def calculate_costs_and_profit(inputs):
    """Calculate all costs, revenue, and profit metrics"""
    
    # Extract inputs
    distance = float(inputs.get('distance', 0))
    load = float(inputs.get('load', 0))
    fuel_price = float(inputs.get('fuel_price', 0))
    toll_fees = float(inputs.get('toll_fees', 0))
    turnaround_time = float(inputs.get('turnaround_time', 0))
    rate_per_ton = float(inputs.get('rate_per_ton', 0))
    
    # Calculate costs
    fuel_cost = distance * FUEL_CONSUMPTION_PER_KM * fuel_price
    driver_cost = turnaround_time * DRIVER_COST_PER_HOUR
    vehicle_operating_cost = distance * VEHICLE_OPERATING_COST_PER_KM
    admin_cost = (fuel_cost + driver_cost + vehicle_operating_cost + toll_fees) * ADMIN_OVERHEAD_PERCENTAGE
    
    total_cost = fuel_cost + driver_cost + vehicle_operating_cost + toll_fees + admin_cost
    
    # Calculate revenue
    total_revenue = load * rate_per_ton
    
    # Calculate profit metrics
    profit = total_revenue - total_cost
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Calculate recommended rates
    cost_per_ton = total_cost / load if load > 0 else 0
    recommended_rate_per_ton = cost_per_ton * 1.2  # 20% markup
    recommended_rate_per_km = total_revenue / distance if distance > 0 else 0
    
    return {
        'fuel_cost': fuel_cost,
        'driver_cost': driver_cost,
        'vehicle_operating_cost': vehicle_operating_cost,
        'toll_fees': toll_fees,
        'admin_cost': admin_cost,
        'total_cost': total_cost,
        'total_revenue': total_revenue,
        'profit': profit,
        'profit_margin': profit_margin,
        'cost_per_ton': cost_per_ton,
        'recommended_rate_per_ton': recommended_rate_per_ton,
        'recommended_rate_per_km': recommended_rate_per_km
    }

def get_cashflow_risk_analysis(payment_terms, profit, total_cost):
    """Analyze cashflow risk based on payment terms"""
    
    risk_levels = {
        'Cash': {'risk': 'Low', 'color': 'success', 'days': 0},
        'Daily': {'risk': 'Low', 'color': 'success', 'days': 1},
        'Weekly': {'risk': 'Medium', 'color': 'warning', 'days': 7},
        'Monthly': {'risk': 'High', 'color': 'danger', 'days': 30}
    }
    
    risk_info = risk_levels.get(payment_terms, risk_levels['Weekly'])
    
    # Calculate cash tied up
    cash_tied_up = total_cost
    opportunity_cost = cash_tied_up * (0.10 / 365) * risk_info['days']  # 10% annual opportunity cost
    
    analysis = {
        'risk_level': risk_info['risk'],
        'color': risk_info['color'],
        'days_to_payment': risk_info['days'],
        'cash_tied_up': cash_tied_up,
        'opportunity_cost': opportunity_cost,
        'adjusted_profit': profit - opportunity_cost
    }
    
    return analysis

def create_excel_export(inputs, results, cashflow_analysis):
    """Create Excel export of the route analysis"""
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Create summary data
        summary_data = {
            'Route Information': [
                inputs.get('loading_point', ''),
                inputs.get('offloading_point', ''),
                f"{inputs.get('distance', 0)} km",
                f"{inputs.get('load', 0)} tons",
                f"{inputs.get('turnaround_time', 0)} hours"
            ],
            'Financial Summary': [
                f"R {results['total_revenue']:,.2f}",
                f"R {results['total_cost']:,.2f}",
                f"R {results['profit']:,.2f}",
                f"{results['profit_margin']:.1f}%",
                cashflow_analysis['risk_level']
            ]
        }
        
        # Cost breakdown
        cost_breakdown = {
            'Cost Item': ['Fuel', 'Driver', 'Vehicle Operating', 'Toll Fees', 'Admin Overhead', 'TOTAL'],
            'Amount (R)': [
                results['fuel_cost'],
                results['driver_cost'],
                results['vehicle_operating_cost'],
                results['toll_fees'],
                results['admin_cost'],
                results['total_cost']
            ]
        }
        
        # Write to Excel
        summary_df = pd.DataFrame(summary_data, index=['Loading Point', 'Offloading Point', 'Distance', 'Load Weight', 'Turnaround Time'])
        cost_df = pd.DataFrame(cost_breakdown)
        
        summary_df.to_excel(writer, sheet_name='Route Analysis', startrow=0)
        cost_df.to_excel(writer, sheet_name='Route Analysis', startrow=8, index=False)
        
        # Format the Excel file
        workbook = writer.book
        worksheet = writer.sheets['Route Analysis']
        
        # Add formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BD'})
        currency_format = workbook.add_format({'num_format': 'R #,##0.00'})
        
        worksheet.set_column('A:B', 20)
        worksheet.set_column('C:C', 15, currency_format)
    
    return output.getvalue()

def create_pdf_export(inputs, results, cashflow_analysis):
    """Create PDF export of the route analysis"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30
    )
    story.append(Paragraph("Route Cost Analysis Report", title_style))
    story.append(Spacer(1, 12))
    
    # Route Information
    route_data = [
        ['Route Information', ''],
        ['Loading Point', inputs.get('loading_point', '')],
        ['Offloading Point', inputs.get('offloading_point', '')],
        ['Distance', f"{inputs.get('distance', 0)} km"],
        ['Load Weight', f"{inputs.get('load', 0)} tons"],
        ['Turnaround Time', f"{inputs.get('turnaround_time', 0)} hours"],
        ['Rate per Ton', f"R {inputs.get('rate_per_ton', 0):.2f}"],
        ['Payment Terms', inputs.get('payment_terms', '')]
    ]
    
    route_table = Table(route_data, colWidths=[2*inch, 3*inch])
    route_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(route_table)
    story.append(Spacer(1, 20))
    
    # Financial Summary
    financial_data = [
        ['Financial Summary', ''],
        ['Total Revenue', f"R {results['total_revenue']:,.2f}"],
        ['Total Cost', f"R {results['total_cost']:,.2f}"],
        ['Profit/Loss', f"R {results['profit']:,.2f}"],
        ['Profit Margin', f"{results['profit_margin']:.1f}%"],
        ['Cashflow Risk', cashflow_analysis['risk_level']]
    ]
    
    financial_table = Table(financial_data, colWidths=[2*inch, 3*inch])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(financial_table)
    story.append(Spacer(1, 20))
    
    # Cost Breakdown
    cost_data = [
        ['Cost Breakdown', 'Amount (R)'],
        ['Fuel Cost', f"R {results['fuel_cost']:,.2f}"],
        ['Driver Cost', f"R {results['driver_cost']:,.2f}"],
        ['Vehicle Operating', f"R {results['vehicle_operating_cost']:,.2f}"],
        ['Toll Fees', f"R {results['toll_fees']:,.2f}"],
        ['Admin Overhead', f"R {results['admin_cost']:,.2f}"],
        ['TOTAL COST', f"R {results['total_cost']:,.2f}"]
    ]
    
    cost_table = Table(cost_data, colWidths=[2*inch, 3*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.lightblue),
        ('BACKGROUND', (0, -1), (-1, -1), colors.yellow),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(cost_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Main App
def main():
    # Header section
    st.markdown("""
    <div class="header">
        <div class="header-content">
            <div class="header-badge">
                <i class="fas fa-calculator"></i>
                <span>Smart Route Planning</span>
            </div>
            <h1>Route <span class="header-highlight">Cost Estimator</span></h1>
            <p>Plan smarter transport routes with instant cost estimates, profit analysis, and dynamic what-if simulations</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main layout
    col1, col2 = st.columns([1, 3], gap="large")
    
    # Sidebar for inputs
    with col1:
        with st.container():
            st.markdown("""
            <div class="sidebar">
                <div class="sidebar-header">
                    <h2>Trip Calculator</h2>
                    <p>Enter your route details for instant analysis</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Route Information
            st.markdown("""
            <div class="section-title">
                <div class="section-icon">
                    <i class="fas fa-map-marked-alt"></i>
                </div>
                Route Information
            </div>
            """, unsafe_allow_html=True)
            
            loading_point = st.text_input("Loading Point", placeholder="e.g., Johannesburg", key="loading_point")
            offloading_point = st.text_input("Offloading Point", placeholder="e.g., Cape Town", key="offloading_point")
            distance = st.number_input("Distance (km)", min_value=0.0, step=1.0, help="Total distance for the trip", key="distance")
            
            # Load Information
            st.markdown("""
            <div class="section-title">
                <div class="section-icon">
                    <i class="fas fa-weight-hanging"></i>
                </div>
                Load Information
            </div>
            """, unsafe_allow_html=True)
            
            load = st.number_input("Load Weight (tons)", min_value=0.0, step=0.1, help="Weight of cargo in tons", key="load")
            
            # Cost Inputs
            st.markdown("""
            <div class="section-title">
                <div class="section-icon">
                    <i class="fas fa-money-bill-wave"></i>
                </div>
                Cost Parameters
            </div>
            """, unsafe_allow_html=True)
            
            fuel_price = st.number_input("Fuel Price (R/litre)", min_value=0.0, value=23.50, step=0.10, key="fuel_price")
            toll_fees = st.number_input("Toll Fees (R)", min_value=0.0, step=1.0, help="Total toll costs for the route", key="toll_fees")
            turnaround_time = st.number_input("Turnaround Time (hours)", min_value=0.0, step=0.5, help="Total time including loading, driving, and offloading", key="turnaround_time")
            
            # Revenue Parameters
            st.markdown("""
            <div class="section-title">
                <div class="section-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                Revenue Parameters
            </div>
            """, unsafe_allow_html=True)
            
            rate_per_ton = st.number_input("Rate per Ton (R/ton)", min_value=0.0, step=1.0, help="What you're charging per ton", key="rate_per_ton")
            payment_terms = st.selectbox("Payment Terms", ["Cash", "Daily", "Weekly", "Monthly"], key="payment_terms")
            
            # Calculate button
            calculate_button = st.button("🧮 Calculate Route Economics", type="primary", use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close sidebar container
    
    # Main content area
    with col2:
        if calculate_button and all([distance, load, fuel_price, turnaround_time, rate_per_ton]):
            # Prepare inputs
            inputs = {
                'loading_point': loading_point,
                'offloading_point': offloading_point,
                'distance': distance,
                'load': load,
                'fuel_price': fuel_price,
                'toll_fees': toll_fees,
                'turnaround_time': turnaround_time,
                'rate_per_ton': rate_per_ton,
                'payment_terms': payment_terms
            }
            
            # Calculate results
            results = calculate_costs_and_profit(inputs)
            cashflow_analysis = get_cashflow_risk_analysis(payment_terms, results['profit'], results['total_cost'])
            
            # Display results
            st.markdown("""
            <div class="content-header">
                <h2>Route Analysis Results</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics grid
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">R {results['total_revenue']:,.2f}</div>
                    <div class="metric-label">Total Revenue</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">R {results['total_cost']:,.2f}</div>
                    <div class="metric-label">Total Cost</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                profit_color = "success" if results['profit'] >= 0 else "danger"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: var(--{profit_color})">R {results['profit']:,.2f}</div>
                    <div class="metric-label">Profit/Loss</div>
                    <div class="metric-delta {'positive' if results['profit'] >= 0 else 'negative'}">
                        {results['profit_margin']:.1f}% margin
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                risk_color = cashflow_analysis['color']
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">
                        <span class="risk-indicator {risk_color}">
                            {cashflow_analysis['risk_level']}
                        </span>
                    </div>
                    <div class="metric-label">Cashflow Risk</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Detailed analysis
            st.markdown("""
            <div class="analysis-grid">
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="analysis-card">
                    <div class="analysis-header">
                        <div class="analysis-icon">
                            <i class="fas fa-receipt"></i>
                        </div>
                        <h3 class="analysis-title">Cost Breakdown</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                cost_breakdown = pd.DataFrame({
                    'Cost Item': ['Fuel', 'Driver', 'Vehicle Operating', 'Toll Fees', 'Admin Overhead'],
                    'Amount (R)': [
                        results['fuel_cost'],
                        results['driver_cost'],
                        results['vehicle_operating_cost'],
                        results['toll_fees'],
                        results['admin_cost']
                    ]
                })
                
                st.dataframe(cost_breakdown, use_container_width=True, hide_index=True)
                
                st.markdown(f"""
                <div style="margin-top: 20px; font-weight: 700; text-align: right;">
                    Total Cost: R {results['total_cost']:,.2f}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)  # Close analysis-card
            
            with col2:
                st.markdown("""
                <div class="analysis-card">
                    <div class="analysis-header">
                        <div class="analysis-icon">
                            <i class="fas fa-chart-pie"></i>
                        </div>
                        <h3 class="analysis-title">Profit Analysis</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                if results['profit'] >= 0:
                    st.markdown(f"""
                    <div class="profit-alert success">
                        <i class="fas fa-check-circle"></i>
                        <div>
                            <h4>Profitable Route</h4>
                            <p>Profit: R {results['profit']:,.2f} ({results['profit_margin']:.1f}% margin)</p>
                            <p>Cost per Ton: R {results['cost_per_ton']:,.2f}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="profit-alert warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div>
                            <h4>Loss-Making Route</h4>
                            <p>Loss: R {abs(results['profit']):,.2f}</p>
                            <p>Recommended Rate: R {results['recommended_rate_per_ton']:,.2f}/ton</p>
                            <p>Current Rate: R {rate_per_ton:,.2f}/ton</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)  # Close analysis-card
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close analysis-grid
            
            # Cashflow Analysis
            st.markdown("""
            <div class="analysis-card" style="margin-top: 32px;">
                <div class="analysis-header">
                    <div class="analysis-icon">
                        <i class="fas fa-money-bill-trend-up"></i>
                    </div>
                    <h3 class="analysis-title">Cashflow Risk Analysis</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{cashflow_analysis['days_to_payment']}</div>
                    <div class="metric-label">Days to Payment</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">R {cashflow_analysis['cash_tied_up']:,.2f}</div>
                    <div class="metric-label">Cash Tied Up</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">R {cashflow_analysis['opportunity_cost']:,.2f}</div>
                    <div class="metric-label">Opportunity Cost</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close analysis-card
            
            # What-if Simulator
            st.markdown("""
            <div class="simulator-section">
                <div class="simulator-header" onclick="toggleSimulator()">
                    <div class="simulator-title">
                        <i class="fas fa-flask"></i>
                        <span>What-If Simulator</span>
                    </div>
                    <div class="toggle-icon">
                        <i class="fas fa-chevron-down"></i>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Test Different Scenarios", expanded=False):
                sim_col1, sim_col2 = st.columns(2)
                
                with sim_col1:
                    st.write("**Adjust Parameters:**")
                    sim_fuel_price = st.slider("Fuel Price (R/litre)", 15.0, 35.0, fuel_price, 0.5, key="sim_fuel")
                    sim_rate_per_ton = st.slider("Rate per Ton (R/ton)", 0.0, rate_per_ton * 2, rate_per_ton, 10.0, key="sim_rate")
                    sim_load = st.slider("Load Weight (tons)", 0.1, load * 2, load, 0.1, key="sim_load")
                    sim_toll_fees = st.slider("Toll Fees (R)", 0.0, toll_fees * 2 if toll_fees > 0 else 1000.0, toll_fees, 50.0, key="sim_toll")
                
                with sim_col2:
                    # Calculate scenario results
                    sim_inputs = inputs.copy()
                    sim_inputs.update({
                        'fuel_price': sim_fuel_price,
                        'rate_per_ton': sim_rate_per_ton,
                        'load': sim_load,
                        'toll_fees': sim_toll_fees
                    })
                    
                    sim_results = calculate_costs_and_profit(sim_inputs)
                    
                    st.write("**Scenario Results:**")
                    st.metric("Revenue", f"R {sim_results['total_revenue']:,.2f}", 
                             delta=f"R {sim_results['total_revenue'] - results['total_revenue']:,.2f}")
                    st.metric("Cost", f"R {sim_results['total_cost']:,.2f}", 
                             delta=f"R {sim_results['total_cost'] - results['total_cost']:,.2f}")
                    st.metric("Profit", f"R {sim_results['profit']:,.2f}", 
                             delta=f"R {sim_results['profit'] - results['profit']:,.2f}")
                    st.metric("Margin", f"{sim_results['profit_margin']:.1f}%", 
                             delta=f"{sim_results['profit_margin'] - results['profit_margin']:.1f}%")
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close simulator-section
            
            # Export Options
            st.markdown("""
            <div class="export-section">
                <div class="export-header">
                    <i class="fas fa-file-export"></i>
                    <h3>Export Options</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Excel Export
                excel_data = create_excel_export(inputs, results, cashflow_analysis)
                st.download_button(
                    label="📊 Download Excel Report",
                    data=excel_data,
                    file_name=f"route_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col2:
                # PDF Export
                pdf_data = create_pdf_export(inputs, results, cashflow_analysis)
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_data,
                    file_name=f"route_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close export-section
            
            # Store results in session state for persistence
            st.session_state['last_results'] = {
                'inputs': inputs,
                'results': results,
                'cashflow_analysis': cashflow_analysis
            }
        
        elif calculate_button:
            st.error("⚠️ Please fill in all required fields: Distance, Load Weight, Fuel Price, Turnaround Time, and Rate per Ton")
        
        else:
            # Show welcome message and instructions
            st.markdown("""
            <div class="welcome-state">
                <div class="welcome-icon">
                    <i class="fas fa-truck"></i>
                </div>
                <h3>Welcome to Route Cost Estimator</h3>
                <p>Your logistics profit calculator in your pocket! Whether you're quoting on WhatsApp or in the field, 
                you'll know your numbers, risks, and upside before you move a single load.</p>
            </div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <h4><i class="fas fa-bolt"></i> Instant Cost Breakdown</h4>
                    <p>See exactly where your money goes with a detailed breakdown of all route expenses.</p>
                </div>
                <div class="feature-card">
                    <h4><i class="fas fa-chart-line"></i> Profit Analysis</h4>
                    <p>Know your margins before you commit to any transport job or contract.</p>
                </div>
                <div class="feature-card">
                    <h4><i class="fas fa-shield-alt"></i> Risk Assessment</h4>
                    <p>Understand how payment terms impact your cashflow and profitability.</p>
                </div>
                <div class="feature-card">
                    <h4><i class="fas fa-flask"></i> What-If Scenarios</h4>
                    <p>Test different rates, fuel prices, and loads to find the sweet spot.</p>
                </div>
            </div>
            
            <div style="margin-top: 40px;">
                <h4>How to Use:</h4>
                <ol>
                    <li>Enter route details in the sidebar (loading/offloading points, distance)</li>
                    <li>Add load information (weight in tons)</li>
                    <li>Input cost parameters (fuel price, tolls, turnaround time)</li>
                    <li>Set revenue parameters (your rate per ton, payment terms)</li>
                    <li>Click Calculate to see instant profit analysis</li>
                </ol>
                
                <div style="margin-top: 20px;">
                    <h4>Perfect For:</h4>
                    <ul>
                        <li>Trucking company owners</li>
                        <li>Freelance transporters</li>
                        <li>Logistics coordinators</li>
                        <li>SME fleet managers</li>
                    </ul>
                </div>
                
                <p style="margin-top: 20px; font-weight: 600; color: var(--teal);">
                    Start by entering your trip details in the sidebar! 👈
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show sample calculation
            with st.expander("📊 See Sample Calculation", expanded=False):
                st.markdown("""
                **Example Route: Johannesburg to Cape Town**
                - Distance: 1,400 km
                - Load: 25 tons
                - Fuel Price: R 23.50/litre
                - Toll Fees: R 850
                - Turnaround Time: 36 hours
                - Rate: R 450/ton
                - Payment Terms: Weekly
                
                **Results:**
                - Revenue: R 11,250
                - Total Cost: R 9,456
                - Profit: R 1,794 (15.9% margin)
                - Cashflow Risk: Medium
                """)

if __name__ == "__main__":
    main()
