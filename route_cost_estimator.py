import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="LOI Profitability Calculator",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .profit-positive {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
    }
    
    .profit-negative {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }
    
    .info-box {
        background: #f8fafc;
        padding: 1rem;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
        margin: 2rem 0;
        border-radius: 1px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🚛 LOI Profitability Calculator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6b7280; font-size: 1.2rem;">Make informed decisions before accepting your next job</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📝 Job Details")
        
        # Route Information
        st.subheader("🗺️ Route Information")
        loading_point = st.text_input(
            "Loading Point",
            placeholder="e.g., Johannesburg",
            help="Starting location for pickup"
        )
        
        offloading_point = st.text_input(
            "Offloading Point", 
            placeholder="e.g., Cape Town",
            help="Destination for delivery"
        )
        
        distance = st.number_input(
            "Distance (one-way km)",
            min_value=1,
            value=500,
            help="One-way distance in kilometers"
        )
        
        # Financial Inputs
        st.subheader("💰 Financial Details")
        rate_per_ton = st.number_input(
            "Rate per Ton (ZAR)",
            min_value=0.0,
            value=150.0,
            step=10.0,
            help="How much you'll be paid per ton of cargo"
        )
        
        fuel_price = st.number_input(
            "Fuel Price per Litre (ZAR)",
            min_value=0.0,
            value=23.50,
            step=0.10,
            help="Current fuel price per litre"
        )
        
        toll_fees = st.number_input(
            "Toll Fees (ZAR)",
            min_value=0.0,
            value=500.0,
            step=50.0,
            help="Total toll fees for the route"
        )
        
        # Operational Inputs
        st.subheader("⚙️ Operations")
        loads_per_day = st.number_input(
            "Loads per Day",
            min_value=1,
            max_value=10,
            value=1,
            help="How many loads you can complete per day"
        )
        
        payment_terms = st.selectbox(
            "Payment Terms",
            [30, 45, 60, 90],
            help="Days until payment is received"
        )
        
        # Advanced Settings
        with st.expander("🔧 Advanced Settings"):
            truck_capacity = st.number_input("Truck Capacity (tons)", value=34.0, help="Maximum payload capacity")
            fuel_efficiency = st.number_input("Fuel Efficiency (km/L)", value=3.5, help="Kilometers per litre")
            driver_cost_per_day = st.number_input("Driver Cost per Day (ZAR)", value=800.0)
            maintenance_per_km = st.number_input("Maintenance per KM (ZAR)", value=2.50)
            insurance_per_day = st.number_input("Insurance per Day (ZAR)", value=300.0)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔍 Calculate Profitability", type="primary", use_container_width=True):
            # Calculations (placeholder logic - you'll implement the actual engine)
            
            # Revenue calculations
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
            
            # Display results
            st.subheader("📊 Profitability Analysis")
            
            # Key metrics in cards
            metric_cols = st.columns(4)
            
            with metric_cols[0]:
                profit_class = "profit-positive" if profit_per_trip > 0 else "profit-negative"
                st.markdown(f'''
                <div class="metric-card {profit_class}">
                    <h3>Profit per Trip</h3>
                    <h2>R {profit_per_trip:,.2f}</h2>
                    <p>{"✅ Profitable" if profit_per_trip > 0 else "❌ Loss"}</p>
                </div>
                ''', unsafe_allow_html=True)
            
            with metric_cols[1]:
                profit_class = "profit-positive" if daily_profit > 0 else "profit-negative"
                st.markdown(f'''
                <div class="metric-card {profit_class}">
                    <h3>Daily Profit</h3>
                    <h2>R {daily_profit:,.2f}</h2>
                    <p>{loads_per_day} loads/day</p>
                </div>
                ''', unsafe_allow_html=True)
            
            with metric_cols[2]:
                st.markdown(f'''
                <div class="metric-card">
                    <h3>Cost per KM</h3>
                    <h2>R {cost_per_km:.2f}</h2>
                    <p>Total operating cost</p>
                </div>
                ''', unsafe_allow_html=True)
            
            with metric_cols[3]:
                st.markdown(f'''
                <div class="metric-card">
                    <h3>Breakeven Rate</h3>
                    <h2>R {breakeven_rate:.2f}</h2>
                    <p>per ton</p>
                </div>
                ''', unsafe_allow_html=True)
            
            # Detailed breakdown
            st.subheader("💼 Cost Breakdown")
            
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
            st.dataframe(df_breakdown, use_container_width=True)
            
            # Cash Flow Timeline
            st.subheader("💹 Cash Flow Timeline")
            
            # Generate cash flow data
            payment_date = datetime.now() + timedelta(days=payment_terms)
            
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
            
            fig = px.line(df_cashflow, x='Date', y='Cumulative Cash Flow', 
                         title='Cash Flow Projection')
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.subheader("💡 Recommendations")
            
            if profit_per_trip > 0:
                st.success("✅ This job appears profitable! Consider accepting this LOI.")
                if profit_per_trip < 1000:
                    st.warning("⚠️ Profit margin is low. Consider negotiating a higher rate or reducing costs.")
            else:
                st.error("❌ This job will result in a loss. Consider:")
                st.write("- Negotiating a higher rate (minimum R{:.2f} per ton)".format(breakeven_rate))
                st.write("- Finding ways to reduce operational costs")
                st.write("- Looking for return loads to improve efficiency")
    
    with col2:
        st.subheader("ℹ️ Quick Tips")
        
        st.markdown('''
        <div class="info-box">
            <h4>💡 Rate Negotiation</h4>
            <p>Your breakeven rate is your minimum acceptable rate per ton. Always aim higher to ensure profitability.</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="info-box">
            <h4>⛽ Fuel Efficiency</h4>
            <p>Improving fuel efficiency by just 0.5 km/L can significantly impact profitability on long routes.</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="info-box">
            <h4>💰 Payment Terms</h4>
            <p>Longer payment terms require more working capital. Factor this into your cash flow planning.</p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="info-box">
            <h4>🔄 Return Loads</h4>
            <p>Finding return loads can double your revenue while only increasing costs marginally.</p>
        </div>
        ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
