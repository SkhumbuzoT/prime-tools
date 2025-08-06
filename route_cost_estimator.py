import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Route Profitability Analyzer | Enterprise",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --secondary: #1e40af;
        --success: #16a34a;
        --danger: #dc2626;
        --warning: #d97706;
        --info: #0284c7;
        --dark: #1e293b;
        --light: #f8fafc;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--dark);
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        color: var(--dark);
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 4px solid var(--primary);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .profit-positive {
        border-left-color: var(--success);
    }
    
    .profit-negative {
        border-left-color: var(--danger);
    }
    
    .info-box {
        background: white;
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 4px solid var(--info);
    }
    
    .section-divider {
        height: 1px;
        background: #e2e8f0;
        margin: 2rem 0;
    }
    
    .stButton>button {
        background-color: var(--primary);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary);
        transform: translateY(-1px);
    }
    
    .sidebar .sidebar-content {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    .stNumberInput, .stTextInput, .stSelectbox {
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px 4px 0 0;
        background: #f1f5f9;
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Enterprise Header with Logo Space
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 class="main-header">Route Profitability Analyzer</h1>
            <p style="color: #64748b; font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
                Advanced financial modeling for transportation contracts with predictive analytics
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Professional Sidebar with Organized Inputs
    with st.sidebar:
        # Company Logo Placeholder
        st.image("https://via.placeholder.com/250x80?text=Your+Logo", use_column_width=True)
        
        # Version and Last Updated
        st.caption("v2.1.0 | Last Updated: August 2023")
        
        # Input Sections in Expandable Containers
        with st.expander("📌 Route Details", expanded=True):
            loading_point = st.text_input(
                "Origin Location",
                placeholder="e.g., Johannesburg",
                help="Starting location for pickup"
            )
            offloading_point = st.text_input(
                "Destination", 
                placeholder="e.g., Cape Town",
                help="Final delivery location"
            )
            distance = st.number_input(
                "One-Way Distance (km)",
                min_value=1,
                value=500,
                help="Point-to-point distance in kilometers"
            )
        
        with st.expander("💰 Financial Parameters", expanded=True):
            rate_per_ton = st.number_input(
                "Contract Rate (ZAR/ton)",
                min_value=0.0,
                value=150.0,
                step=10.0,
                format="%.2f"
            )
            fuel_price = st.number_input(
                "Current Fuel Price (ZAR/L)",
                min_value=0.0,
                value=23.50,
                step=0.10,
                format="%.2f"
            )
            toll_fees = st.number_input(
                "Estimated Toll Fees (ZAR)",
                min_value=0.0,
                value=500.0,
                step=50.0,
                format="%.2f"
            )
        
        with st.expander("⚙️ Operational Settings", expanded=False):
            loads_per_day = st.number_input(
                "Daily Load Capacity",
                min_value=1,
                max_value=10,
                value=1
            )
            payment_terms = st.selectbox(
                "Payment Terms (days)",
                [30, 45, 60, 90],
                index=0
            )
        
        with st.expander("🔧 Fleet Configuration", expanded=False):
            truck_capacity = st.number_input(
                "Vehicle Capacity (tons)", 
                value=34.0,
                step=0.5
            )
            fuel_efficiency = st.number_input(
                "Fuel Economy (km/L)", 
                value=3.5,
                step=0.1,
                min_value=1.0
            )
            driver_cost_per_day = st.number_input(
                "Driver Daily Rate (ZAR)", 
                value=800.0,
                step=50.0
            )
            maintenance_per_km = st.number_input(
                "Maintenance Cost (ZAR/km)", 
                value=2.50,
                step=0.10
            )
            insurance_per_day = st.number_input(
                "Daily Insurance (ZAR)", 
                value=300.0,
                step=25.0
            )
    
    # Main Content Area
    if st.button("Analyze Profitability", type="primary", use_container_width=True):
        # Calculations
        revenue_per_trip = rate_per_ton * truck_capacity
        daily_revenue = revenue_per_trip * loads_per_day
        
        # Cost calculations
        fuel_cost_per_trip = (distance * 2 / fuel_efficiency) * fuel_price  # Round trip
        total_variable_cost_per_trip = fuel_cost_per_trip + toll_fees + (maintenance_per_km * distance * 2)
        fixed_cost_per_day = driver_cost_per_day + insurance_per_day
        total_cost_per_trip = total_variable_cost_per_trip + (fixed_cost_per_day / loads_per_day)
        daily_total_cost = total_cost_per_trip * loads_per_day
        
        # Profitability
        profit_per_trip = revenue_per_trip - total_cost_per_trip
        daily_profit = daily_revenue - daily_total_cost
        
        cost_per_km = total_cost_per_trip / (distance * 2)
        breakeven_rate = total_cost_per_trip / truck_capacity
        
        # Cost Breakdown Data
        breakdown_data = {
            'Cost Category': [
                'Fuel Cost',
                'Toll Fees', 
                'Maintenance',
                'Driver Cost (per trip)',
                'Insurance (per trip)',
                'Total Cost per Trip'
            ],
            'Amount (ZAR)': [
                fuel_cost_per_trip,
                toll_fees,
                maintenance_per_km * distance * 2,
                driver_cost_per_day / loads_per_day,
                insurance_per_day / loads_per_day,
                total_cost_per_trip
            ]
        }
        
        df_breakdown = pd.DataFrame(breakdown_data)
        
        # Cash Flow Timeline
        cash_flow_data = []
        for i in range(payment_terms + 30):  # Show 30 days after payment
            date = datetime.now() + timedelta(days=i)
            if i == 0:
                cash_flow = -daily_total_cost  # Initial expense
            elif i == payment_terms:
                cash_flow = daily_revenue  # Payment received
            else:
                cash_flow = 0
            
            cumulative = sum([cf['Daily Cash Flow'] for cf in cash_flow_data]) + cash_flow
            
            cash_flow_data.append({
                'Date': date,
                'Daily Cash Flow': cash_flow,
                'Cumulative Cash Flow': cumulative
            })
        
        df_cashflow = pd.DataFrame(cash_flow_data)
        
        # Results Display
        st.subheader("Financial Performance Summary")
        
        # Key Metrics in Columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Projected Profit per Trip",
                f"R {profit_per_trip:,.2f}",
                delta_color="normal",
                help="Estimated net profit after all expenses"
            )
            
        with col2:
            st.metric(
                "Daily Operating Profit",
                f"R {daily_profit:,.2f}",
                delta=f"{loads_per_day} loads/day",
                delta_color="normal"
            )
            
        with col3:
            st.metric(
                "Cost Efficiency",
                f"R {cost_per_km:.2f}/km",
                help="All-inclusive cost per kilometer"
            )
        
        # Tabbed Interface for Detailed Analysis
        tab1, tab2, tab3 = st.tabs(["📊 Cost Breakdown", "📅 Cash Flow", "📈 Scenario Analysis"])
        
        with tab1:
            # Enhanced Cost Breakdown Visualization
            fig = px.bar(df_breakdown, x='Cost Category', y='Amount (ZAR)', 
                         color='Cost Category', text='Amount (ZAR)',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(texttemplate='R%{text:,.2f}', textposition='outside')
            fig.update_layout(
                showlegend=False, 
                yaxis_title="Cost (ZAR)",
                xaxis_title="",
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Data Table
            st.dataframe(
                df_breakdown.style.format({'Amount (ZAR)': 'R{:,.2f}'}),
                use_container_width=True,
                hide_index=True
            )
            
        with tab2:
            # Enhanced Cash Flow Visualization
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_cashflow['Date'],
                y=df_cashflow['Cumulative Cash Flow'],
                fill='tozeroy',
                line=dict(color='#2563eb'),
                name="Cumulative Cash Flow"
            ))
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            fig.update_layout(
                title="Cash Flow Projection",
                yaxis_title="Cumulative Cash Flow (ZAR)",
                hovermode="x unified",
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Payment Date Indicator
            payment_date = datetime.now() + timedelta(days=payment_terms)
            st.info(f"**Payment Due Date:** {payment_date.strftime('%d %B %Y')}")
            
        with tab3:
            # Scenario Analysis Placeholder
            st.write("## Scenario Modeling")
            st.write("Compare different operational scenarios to optimize profitability.")
            
            # Create two scenarios
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Current Scenario**")
                st.metric("Profit/Trip", f"R{profit_per_trip:,.2f}")
                st.metric("Margin", f"{(profit_per_trip/revenue_per_trip)*100:.1f}%")
                
            with col2:
                st.write("**Optimized Scenario**")
                optimized_profit = profit_per_trip * 1.15  # 15% improvement
                st.metric("Profit/Trip", f"R{optimized_profit:,.2f}", delta="+15%")
                st.metric("Margin", f"{(optimized_profit/(revenue_per_trip*1.05))*100:.1f}%")
                
            st.progress(0.65, text="Scenario analysis in development - coming in v2.2")
        
        # Professional Recommendations Section
        st.subheader("Strategic Recommendations")
        
        if profit_per_trip > 0:
            with st.container(border=True):
                st.success("**Profitability Assessment:** Positive")
                st.write(f"✅ This contract meets profitability thresholds with a margin of R{profit_per_trip:,.2f} per trip.")
                
                if profit_per_trip < (revenue_per_trip * 0.15):
                    st.warning("**Margin Alert:** Profit margin below 15%")
                    st.write("Consider these optimization strategies:")
                    
                    cols = st.columns(2)
                    with cols[0]:
                        st.write("**Operational Efficiency**")
                        st.write("- Reduce empty miles by 10% (+R{:.2f})".format(revenue_per_trip * 0.10))
                        st.write("- Improve fuel efficiency to {:.1f} km/L (+R{:.2f})".format(
                            fuel_efficiency + 0.3, (distance * 2 * fuel_price * (1/fuel_efficiency - 1/(fuel_efficiency+0.3)))))
                        
                    with cols[1]:
                        st.write("**Financial Optimization**")
                        st.write("- Negotiate 5% rate increase (+R{:.2f})".format(revenue_per_trip * 0.05))
                        st.write("- Secure toll reimbursement (+R{:.2f})".format(toll_fees))
        else:
            with st.container(border=True):
                st.error("**Profitability Assessment:** Negative")
                st.write("❌ This contract would operate at a loss. Critical actions required:")
                
                cols = st.columns(2)
                with cols[0]:
                    st.write("**Immediate Negotiation Needed**")
                    st.write(f"- Minimum viable rate: R{breakeven_rate:,.2f}/ton (current: R{rate_per_ton:,.2f})")
                    st.write("- Request fuel surcharge adjustment")
                    st.write("- Negotiate toll reimbursement")
                    
                with cols[1]:
                    st.write("**Operational Improvements**")
                    st.write(f"- Reduce distance by 10% (-{distance * 0.1:.0f} km)")
                    st.write(f"- Improve fuel efficiency to {fuel_efficiency + 0.5:.1f} km/L")
                    st.write("- Secure backhaul loads to double revenue")
    
    # Right Sidebar with Professional Tips
    with st.sidebar:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.subheader("Analyst Insights")
        
        st.markdown('''
        <div class="info-box">
            <h4>📌 Key Performance Indicators</h4>
            <p>Monitor these metrics closely: Cost/km below R12.50, Profit margin above 15%, and Utilization over 80%.</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="info-box">
            <h4>⛽ Fuel Management</h4>
            <p>A 5% improvement in fuel efficiency typically increases profitability by 8-12% on long-haul routes.</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="info-box">
            <h4>💰 Working Capital</h4>
            <p>For 60-day payment terms, maintain 2 months of operating expenses in reserve.</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="info-box">
            <h4>📊 Data-Driven Decisions</h4>
            <p>Analyze historical data to identify your most profitable routes and customers.</p>
        </div>
        ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
