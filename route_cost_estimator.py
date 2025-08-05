import streamlit as st
import pandas as pd
import xlsxwriter
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import base64

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
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 3rem;
        margin-bottom: 2rem;
    }
    .cost-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 1rem 0;
    }
    .profit-positive {
        color: #28a745;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .profit-negative {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class RouteCostCalculator:
    def __init__(self):
        self.payment_risk_factors = {
            "Cash": 1.0,
            "Daily": 1.02,
            "Weekly": 1.05,
            "Monthly": 1.15
        }
        
    def calculate_fuel_cost(self, distance, fuel_efficiency, fuel_price):
        """Calculate total fuel cost for the trip"""
        fuel_needed = distance / fuel_efficiency
        return fuel_needed * fuel_price, fuel_needed
    
    def calculate_driver_cost(self, turnaround_time, daily_driver_rate=500):
        """Calculate driver cost based on turnaround time"""
        return (turnaround_time / 24) * daily_driver_rate
    
    def calculate_maintenance_cost(self, distance, rate_per_km=1.2):
        """Calculate maintenance cost based on distance"""
        return distance * rate_per_km
    
    def calculate_insurance_cost(self, load_tons, rate_per_ton=15):
        """Calculate insurance cost based on load weight"""
        return load_tons * rate_per_ton
    
    def calculate_depreciation(self, distance, rate_per_km=0.8):
        """Calculate vehicle depreciation cost"""
        return distance * rate_per_km
    
    def calculate_total_costs(self, distance, load_tons, fuel_price, toll_fees, 
                            turnaround_time, fuel_efficiency=4.0):
        """Calculate all trip costs"""
        fuel_cost, fuel_needed = self.calculate_fuel_cost(distance, fuel_efficiency, fuel_price)
        driver_cost = self.calculate_driver_cost(turnaround_time)
        maintenance_cost = self.calculate_maintenance_cost(distance)
        insurance_cost = self.calculate_insurance_cost(load_tons)
        depreciation_cost = self.calculate_depreciation(distance)
        
        total_cost = fuel_cost + driver_cost + maintenance_cost + insurance_cost + depreciation_cost + toll_fees
        
        return {
            'fuel_cost': fuel_cost,
            'fuel_needed': fuel_needed,
            'driver_cost': driver_cost,
            'maintenance_cost': maintenance_cost,
            'insurance_cost': insurance_cost,
            'depreciation_cost': depreciation_cost,
            'toll_fees': toll_fees,
            'total_cost': total_cost
        }
    
    def calculate_revenue_and_profit(self, load_tons, rate_per_ton, costs):
        """Calculate revenue and profit metrics"""
        revenue = load_tons * rate_per_ton
        profit = revenue - costs['total_cost']
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
        
        return {
            'revenue': revenue,
            'profit': profit,
            'profit_margin': profit_margin
        }
    
    def calculate_recommended_rates(self, costs, load_tons, target_margin=20):
        """Calculate recommended rates for target profit margin"""
        target_profit_multiplier = 1 + (target_margin / 100)
        recommended_revenue = costs['total_cost'] * target_profit_multiplier
        recommended_rate_per_ton = recommended_revenue / load_tons
        
        return {
            'recommended_rate_per_ton': recommended_rate_per_ton,
            'recommended_revenue': recommended_revenue
        }
    
    def assess_cashflow_risk(self, payment_terms, profit, revenue):
        """Assess cashflow risk based on payment terms"""
        risk_factor = self.payment_risk_factors.get(payment_terms, 1.1)
        adjusted_profit = profit * risk_factor
        
        risk_levels = {
            "Cash": "Low Risk - Immediate payment",
            "Daily": "Low Risk - Quick turnaround",
            "Weekly": "Medium Risk - Standard payment cycle",
            "Monthly": "High Risk - Extended payment cycle"
        }
        
        return {
            'risk_level': risk_levels.get(payment_terms, "Unknown Risk"),
            'risk_factor': risk_factor,
            'adjusted_profit': adjusted_profit
        }

def create_excel_report(trip_data, costs, financial_metrics, recommendations):
    """Create Excel report for download"""
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Route Cost Analysis')
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'bg_color': '#2E86AB',
        'font_color': 'white',
        'align': 'center'
    })
    
    subheader_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'bg_color': '#E8F4FD'
    })
    
    currency_format = workbook.add_format({'num_format': 'R #,##0.00'})
    percentage_format = workbook.add_format({'num_format': '0.00%'})
    
    # Write report
    row = 0
    worksheet.write(row, 0, 'ROUTE COST ANALYSIS REPORT', header_format)
    worksheet.merge_range(row, 0, row, 3, 'ROUTE COST ANALYSIS REPORT', header_format)
    row += 2
    
    # Trip Details
    worksheet.write(row, 0, 'TRIP DETAILS', subheader_format)
    row += 1
    for key, value in trip_data.items():
        worksheet.write(row, 0, key.replace('_', ' ').title())
        worksheet.write(row, 1, value)
        row += 1
    
    row += 1
    
    # Cost Breakdown
    worksheet.write(row, 0, 'COST BREAKDOWN', subheader_format)
    row += 1
    for key, value in costs.items():
        if key != 'fuel_needed':
            worksheet.write(row, 0, key.replace('_', ' ').title())
            worksheet.write(row, 1, value, currency_format)
            row += 1
    
    row += 1
    
    # Financial Metrics
    worksheet.write(row, 0, 'FINANCIAL ANALYSIS', subheader_format)
    row += 1
    worksheet.write(row, 0, 'Revenue')
    worksheet.write(row, 1, financial_metrics['revenue'], currency_format)
    row += 1
    worksheet.write(row, 0, 'Profit')
    worksheet.write(row, 1, financial_metrics['profit'], currency_format)
    row += 1
    worksheet.write(row, 0, 'Profit Margin')
    worksheet.write(row, 1, financial_metrics['profit_margin']/100, percentage_format)
    row += 1
    
    workbook.close()
    output.seek(0)
    return output

def create_pdf_report(trip_data, costs, financial_metrics, recommendations):
    """Create PDF report for download"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph("Route Cost Analysis Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Trip Details
    story.append(Paragraph("Trip Details", styles['Heading2']))
    trip_table_data = [['Parameter', 'Value']]
    for key, value in trip_data.items():
        trip_table_data.append([key.replace('_', ' ').title(), str(value)])
    
    trip_table = Table(trip_table_data)
    trip_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(trip_table)
    story.append(Spacer(1, 20))
    
    # Cost Breakdown
    story.append(Paragraph("Cost Breakdown", styles['Heading2']))
    cost_table_data = [['Cost Component', 'Amount (R)']]
    for key, value in costs.items():
        if key != 'fuel_needed':
            cost_table_data.append([key.replace('_', ' ').title(), f"R {value:,.2f}"])
    
    cost_table = Table(cost_table_data)
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(cost_table)
    story.append(Spacer(1, 20))
    
    # Financial Summary
    story.append(Paragraph("Financial Summary", styles['Heading2']))
    financial_data = [
        ['Metric', 'Value'],
        ['Revenue', f"R {financial_metrics['revenue']:,.2f}"],
        ['Total Costs', f"R {costs['total_cost']:,.2f}"],
        ['Profit', f"R {financial_metrics['profit']:,.2f}"],
        ['Profit Margin', f"{financial_metrics['profit_margin']:.2f}%"]
    ]
    
    financial_table = Table(financial_data)
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(financial_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    # Header
    st.markdown('<h1 class="main-header">🚛 Route Cost Estimator</h1>', unsafe_allow_html=True)
    st.markdown("**Plan smarter transport routes with instant cost estimates, profit analysis, and dynamic what-if simulations**")
    
    calculator = RouteCostCalculator()
    
    # Sidebar for inputs
    st.sidebar.header("📝 Trip Details")
    
    # Core inputs
    loading_point = st.sidebar.text_input("Loading Point", value="Johannesburg")
    offloading_point = st.sidebar.text_input("Offloading Point", value="Cape Town") 
    distance = st.sidebar.number_input("Distance (km)", min_value=1.0, value=1400.0, step=10.0)
    load_tons = st.sidebar.number_input("Load (tons)", min_value=0.1, value=30.0, step=0.5)
    fuel_price = st.sidebar.number_input("Fuel Price (R/litre)", min_value=0.1, value=22.50, step=0.10)
    toll_fees = st.sidebar.number_input("Toll Fees (R)", min_value=0.0, value=800.0, step=50.0)
    turnaround_time = st.sidebar.number_input("Turnaround Time (hours)", min_value=1.0, value=48.0, step=1.0)
    rate_per_ton = st.sidebar.number_input("Rate per Ton (R/ton)", min_value=0.0, value=250.0, step=10.0)
    
    payment_terms = st.sidebar.selectbox(
        "Payment Terms",
        ["Cash", "Daily", "Weekly", "Monthly"],
        index=2
    )
    
    # Advanced settings
    with st.sidebar.expander("⚙️ Advanced Settings"):
        fuel_efficiency = st.number_input("Fuel Efficiency (km/litre)", min_value=0.1, value=4.0, step=0.1)
        daily_driver_rate = st.number_input("Daily Driver Rate (R)", min_value=0.0, value=500.0, step=50.0)
        maintenance_rate = st.number_input("Maintenance Rate (R/km)", min_value=0.0, value=1.2, step=0.1)
        insurance_rate = st.number_input("Insurance Rate (R/ton)", min_value=0.0, value=15.0, step=1.0)
        depreciation_rate = st.number_input("Depreciation Rate (R/km)", min_value=0.0, value=0.8, step=0.1)
    
    # Calculate costs
    costs = calculator.calculate_total_costs(
        distance, load_tons, fuel_price, toll_fees, turnaround_time, fuel_efficiency
    )
    
    # Override with custom rates if provided
    costs['driver_cost'] = calculator.calculate_driver_cost(turnaround_time, daily_driver_rate)
    costs['maintenance_cost'] = distance * maintenance_rate
    costs['insurance_cost'] = load_tons * insurance_rate
    costs['depreciation_cost'] = distance * depreciation_rate
    costs['total_cost'] = (costs['fuel_cost'] + costs['driver_cost'] + 
                          costs['maintenance_cost'] + costs['insurance_cost'] + 
                          costs['depreciation_cost'] + toll_fees)
    
    financial_metrics = calculator.calculate_revenue_and_profit(load_tons, rate_per_ton, costs)
    recommendations = calculator.calculate_recommended_rates(costs, load_tons)
    cashflow_risk = calculator.assess_cashflow_risk(payment_terms, financial_metrics['profit'], financial_metrics['revenue'])
    
    # Main content layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Cost Analysis")
        
        # Cost breakdown
        st.subheader("Cost Breakdown")
        cost_data = {
            'Component': ['Fuel', 'Driver', 'Maintenance', 'Insurance', 'Depreciation', 'Tolls', 'TOTAL'],
            'Amount (R)': [
                f"{costs['fuel_cost']:,.2f}",
                f"{costs['driver_cost']:,.2f}",
                f"{costs['maintenance_cost']:,.2f}",
                f"{costs['insurance_cost']:,.2f}",
                f"{costs['depreciation_cost']:,.2f}",
                f"{costs['toll_fees']:,.2f}",
                f"{costs['total_cost']:,.2f}"
            ],
            'Percentage': [
                f"{(costs['fuel_cost']/costs['total_cost']*100):.1f}%",
                f"{(costs['driver_cost']/costs['total_cost']*100):.1f}%",
                f"{(costs['maintenance_cost']/costs['total_cost']*100):.1f}%",
                f"{(costs['insurance_cost']/costs['total_cost']*100):.1f}%",
                f"{(costs['depreciation_cost']/costs['total_cost']*100):.1f}%",
                f"{(costs['toll_fees']/costs['total_cost']*100):.1f}%",
                "100.0%"
            ]
        }
        
        df_costs = pd.DataFrame(cost_data)
        st.dataframe(df_costs, use_container_width=True, hide_index=True)
        
        # Financial summary
        st.subheader("Financial Summary")
        
        profit_class = "profit-positive" if financial_metrics['profit'] > 0 else "profit-negative"
        
        st.markdown(f"""
        <div class="cost-card">
            <h4>Revenue: R {financial_metrics['revenue']:,.2f}</h4>
            <h4>Total Costs: R {costs['total_cost']:,.2f}</h4>
            <h4 class="{profit_class}">Profit: R {financial_metrics['profit']:,.2f}</h4>
            <h4 class="{profit_class}">Profit Margin: {financial_metrics['profit_margin']:.2f}%</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Recommendations
        st.subheader("💡 Recommendations")
        st.info(f"""
        **Recommended Rate for 20% Profit Margin:** R {recommendations['recommended_rate_per_ton']:,.2f} per ton
        
        **Current vs Recommended:**
        - Current Rate: R {rate_per_ton:,.2f}/ton
        - Recommended Rate: R {recommendations['recommended_rate_per_ton']:,.2f}/ton
        - Difference: R {(recommendations['recommended_rate_per_ton'] - rate_per_ton):,.2f}/ton
        """)
        
        # Cashflow risk
        st.subheader("💰 Cashflow Risk Assessment")
        risk_color = {
            "Low Risk": "🟢",
            "Medium Risk": "🟡", 
            "High Risk": "🔴"
        }
        risk_icon = risk_color.get(cashflow_risk['risk_level'].split(' - ')[0], "⚪")
        
        st.markdown(f"""
        **Payment Terms:** {payment_terms}  
        **Risk Level:** {risk_icon} {cashflow_risk['risk_level']}  
        **Risk-Adjusted Profit:** R {cashflow_risk['adjusted_profit']:,.2f}
        """)
    
    with col2:
        st.header("🧪 What-If Simulator")
        
        st.subheader("Adjust Parameters")
        
        # What-if inputs
        sim_rate = st.slider("Rate per Ton (R)", 
                           min_value=float(rate_per_ton * 0.5), 
                           max_value=float(rate_per_ton * 2), 
                           value=float(rate_per_ton), 
                           step=5.0)
        
        sim_fuel_price = st.slider("Fuel Price (R/litre)", 
                                 min_value=float(fuel_price * 0.7), 
                                 max_value=float(fuel_price * 1.5), 
                                 value=float(fuel_price), 
                                 step=0.5)
        
        sim_load = st.slider("Load (tons)", 
                           min_value=float(load_tons * 0.5), 
                           max_value=float(load_tons * 1.5), 
                           value=float(load_tons), 
                           step=1.0)
        
        sim_tolls = st.slider("Toll Fees (R)", 
                            min_value=0.0, 
                            max_value=float(toll_fees * 2), 
                            value=float(toll_fees), 
                            step=50.0)
        
        # Simulate with new parameters
        sim_costs = calculator.calculate_total_costs(
            distance, sim_load, sim_fuel_price, sim_tolls, turnaround_time, fuel_efficiency
        )
        sim_costs['driver_cost'] = calculator.calculate_driver_cost(turnaround_time, daily_driver_rate)
        sim_costs['maintenance_cost'] = distance * maintenance_rate
        sim_costs['insurance_cost'] = sim_load * insurance_rate
        sim_costs['depreciation_cost'] = distance * depreciation_rate
        sim_costs['total_cost'] = (sim_costs['fuel_cost'] + sim_costs['driver_cost'] + 
                                  sim_costs['maintenance_cost'] + sim_costs['insurance_cost'] + 
                                  sim_costs['depreciation_cost'] + sim_tolls)
        
        sim_financial = calculator.calculate_revenue_and_profit(sim_load, sim_rate, sim_costs)
        
        # Show simulation results
        st.subheader("📈 Simulation Results")
        
        profit_change = sim_financial['profit'] - financial_metrics['profit']
        margin_change = sim_financial['profit_margin'] - financial_metrics['profit_margin']
        
        profit_change_color = "🟢" if profit_change > 0 else "🔴" if profit_change < 0 else "🟡"
        margin_change_color = "🟢" if margin_change > 0 else "🔴" if margin_change < 0 else "🟡"
        
        st.markdown(f"""
        **New Revenue:** R {sim_financial['revenue']:,.2f}  
        **New Profit:** R {sim_financial['profit']:,.2f}  
        **New Margin:** {sim_financial['profit_margin']:.2f}%
        
        **Changes:**  
        {profit_change_color} Profit: R {profit_change:+,.2f}  
        {margin_change_color} Margin: {margin_change:+.2f}%
        """)
        
        # Comparison chart
        comparison_data = {
            'Scenario': ['Original', 'Simulation'],
            'Revenue': [financial_metrics['revenue'], sim_financial['revenue']],
            'Profit': [financial_metrics['profit'], sim_financial['profit']],
            'Margin (%)': [financial_metrics['profit_margin'], sim_financial['profit_margin']]
        }
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)
    
    # Export section
    st.header("📁 Export Options")
    
    col_export1, col_export2 = st.columns(2)
    
    # Prepare data for export
    trip_data = {
        'loading_point': loading_point,
        'offloading_point': offloading_point,
        'distance_km': distance,
        'load_tons': load_tons,
        'fuel_price_per_litre': fuel_price,
        'toll_fees': toll_fees,
        'turnaround_time_hours': turnaround_time,
        'rate_per_ton': rate_per_ton,
        'payment_terms': payment_terms
    }
    
    with col_export1:
        if st.button("📊 Download Excel Report", type="primary"):
            excel_buffer = create_excel_report(trip_data, costs, financial_metrics, recommendations)
            
            st.download_button(
                label="Download Excel File",
                data=excel_buffer.getvalue(),
                file_name=f"route_cost_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col_export2:
        if st.button("📄 Download PDF Report", type="primary"):
            pdf_buffer = create_pdf_report(trip_data, costs, financial_metrics, recommendations)
            
            st.download_button(
                label="Download PDF File",
                data=pdf_buffer.getvalue(),
                file_name=f"route_cost_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()