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
    page_title="Route Cost Estimator",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .profit-positive {
        color: #28a745;
        font-weight: bold;
    }
    .profit-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
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
    styles = getSampleStyleBook()
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
    st.title("🚛 Route Cost Estimator")
    st.markdown("**Plan smarter transport routes with instant cost estimates, profit analysis, and dynamic what-if simulations**")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📋 Trip Details")
        
        # Route Information
        st.subheader("🗺️ Route Information")
        loading_point = st.text_input("Loading Point", placeholder="e.g., Johannesburg")
        offloading_point = st.text_(placeholder="e.g., Cape Town")
        distance = st.number_input("Distance (km)", min_value=0.0, step=1.0, help="Total distance for the trip")
        
        # Load Information
        st.subheader("📦 Load Information")
        load = st.number_input("Load Weight (tons)", min_value=0.0, step=0.1, help="Weight of cargo in tons")
        
        # Cost Inputs
        st.subheader("💰 Cost Parameters")
        fuel_price = st.number_input("Fuel Price (R/litre)", min_value=0.0, value=23.50, step=0.10)
        toll_fees = st.number_input("Toll Fees (R)", min_value=0.0, step=1.0, help="Total toll costs for the route")
        turnaround_time = st.number_input("Turnaround Time (hours)", min_value=0.0, step=0.5, help="Total time including loading, driving, and offloading")
        
        # Revenue Parameters
        st.subheader("💵 Revenue Parameters")
        rate_per_ton = st.number_input("Rate per Ton (R/ton)", min_value=0.0, step=1.0, help="What you're charging per ton")
        payment_terms = st.selectbox("Payment Terms", ["Cash", "Daily", "Weekly", "Monthly"])
        
        # Calculate button
        calculate_button = st.button("🧮 Calculate Route Economics", type="primary")
    
    # Main content area
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
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Revenue", f"R {results['total_revenue']:,.2f}")
        
        with col2:
            st.metric("💸 Total Cost", f"R {results['total_cost']:,.2f}")
        
        with col3:
            profit_color = "normal" if results['profit'] >= 0 else "inverse"
            st.metric("📈 Profit/Loss", f"R {results['profit']:,.2f}", delta=f"{results['profit_margin']:.1f}%")
        
        with col4:
            risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
            st.metric("⚠️ Cashflow Risk", f"{risk_color.get(cashflow_analysis['risk_level'], '⚪')} {cashflow_analysis['risk_level']}")
        
        # Detailed Cost Breakdown
        st.subheader("📊 Cost Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
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
            
            st.dataframe(cost_breakdown, use_container_width=True)
            
            # Total cost highlight
            st.markdown(f"### **Total Cost: R {results['total_cost']:,.2f}**")
        
        with col2:
            # Profit Analysis
            if results['profit'] >= 0:
                st.markdown(f"""
                <div class="success-box">
                    <h4>✅ Profitable Route</h4>
                    <p><strong>Profit:</strong> R {results['profit']:,.2f}</p>
                    <p><strong>Margin:</strong> {results['profit_margin']:.1f}%</p>
                    <p><strong>Cost per Ton:</strong> R {results['cost_per_ton']:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="warning-box">
                    <h4>⚠️ Loss-Making Route</h4>
                    <p><strong>Loss:</strong> R {abs(results['profit']):,.2f}</p>
                    <p><strong>Recommended Rate:</strong> R {results['recommended_rate_per_ton']:,.2f}/ton</p>
                    <p><strong>Current Rate:</strong> R {rate_per_ton:,.2f}/ton</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Cashflow Analysis
        st.subheader("💳 Cashflow Risk Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Days to Payment", f"{cashflow_analysis['days_to_payment']} days")
        
        with col2:
            st.metric("Cash Tied Up", f"R {cashflow_analysis['cash_tied_up']:,.2f}")
        
        with col3:
            st.metric("Opportunity Cost", f"R {cashflow_analysis['opportunity_cost']:,.2f}")
        
        # What-if Simulator
        st.subheader("🧪 What-If Simulator")
        
        with st.expander("Test Different Scenarios", expanded=False):
            sim_col1, sim_col2 = st.columns(2)
            
            with sim_col1:
                st.write("**Adjust Parameters:**")
                sim_fuel_price = st.slider("Fuel Price (R/litre)", 15.0, 35.0, fuel_price, 0.5)
                sim_rate_per_ton = st.slider("Rate per Ton (R/ton)", 0.0, rate_per_ton * 2, rate_per_ton, 10.0)
                sim_load = st.slider("Load Weight (tons)", 0.1, load * 2, load, 0.1)
                sim_toll_fees = st.slider("Toll Fees (R)", 0.0, toll_fees * 2 if toll_fees > 0 else 1000.0, toll_fees, 50.0)
            
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
        
        # Export Options
        st.subheader("📁 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel Export
            excel_data = create_excel_export(inputs, results, cashflow_analysis)
            st.download_button(
                label="📊 Download Excel Report",
                data=excel_data,
                file_name=f"route_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            # PDF Export
            pdf_data = create_pdf_export(inputs, results, cashflow_analysis)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name=f"route_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
        
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
        ## 🚀 Welcome to Route Cost Estimator
        
        **Your logistics profit calculator in your pocket!** Whether you're quoting on WhatsApp or in the field, 
        you'll know your numbers, risks, and upside before you move a single load.
        
        ### 📋 How to Use:
        1. **Enter route details** in the sidebar (loading/offloading points, distance)
        2. **Add load information** (weight in tons)
        3. **Input cost parameters** (fuel price, tolls, turnaround time)
        4. **Set revenue parameters** (your rate per ton, payment terms)
        5. **Click Calculate** to see instant profit analysis
        6. **Use the What-If Simulator** to test different scenarios
        7. **Export professional reports** in Excel or PDF format
        
        ### 💡 Key Features:
        - **Instant Cost Breakdown**: See exactly where your money goes
        - **Profit Analysis**: Know your margins before you commit
        - **Cashflow Risk Assessment**: Understand payment term impacts
        - **What-If Scenarios**: Test different rates, fuel prices, and loads
        - **Professional Exports**: Generate reports for clients and records
        
        ### 🎯 Perfect For:
        - Trucking company owners
        - Freelance transporters  
        - Logistics coordinators
        - SME fleet managers
        
        **Start by entering your trip details in the sidebar! 👈**
        """)
        
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
