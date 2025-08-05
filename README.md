# 🚛 Route Cost Estimator

**Plan smarter transport routes with instant cost estimates, profit analysis, and dynamic "what-if" simulations.**

## Overview

The Route Cost Estimator is a comprehensive web application designed for truck owners, logistics managers, and transport coordinators who need to make informed decisions about route profitability. No more blind quoting or relying on outdated spreadsheets – get instant, accurate cost breakdowns and profit analysis for any route.

## 🎯 Problem Solved

- **Blind Quoting**: Eliminates guesswork when pricing transport jobs
- **Outdated Methods**: Replaces error-prone spreadsheets with dynamic calculations
- **Hidden Costs**: Reveals true trip costs including fuel, tolls, driver time, maintenance, and depreciation
- **Cash Flow Risk**: Assesses payment term risks and their impact on profitability
- **Scenario Planning**: Tests "what-if" scenarios before committing to routes

## ✨ Key Features

### 🔢 Comprehensive Cost Inputs
- **Route Details**: Loading/offloading points, distance, load weight
- **Operational Costs**: Fuel price, toll fees, turnaround time
- **Pricing**: Rate per ton, payment terms (Cash/Daily/Weekly/Monthly)
- **Advanced Settings**: Custom rates for fuel efficiency, driver costs, maintenance, insurance, depreciation

### 📊 Detailed Analysis
- **Cost Breakdown**: Itemized costs with percentages
- **Financial Metrics**: Revenue, profit, and profit margins
- **Recommendations**: Suggested rates for target profit margins
- **Risk Assessment**: Cashflow risk analysis based on payment terms

### 🧪 What-If Simulator
- **Dynamic Testing**: Adjust rates, fuel prices, load weights, and tolls
- **Instant Results**: See immediate impact on profitability
- **Comparison Views**: Side-by-side original vs. simulated scenarios
- **Negotiation Power**: Test quote sensitivity and pricing strategies

### 📁 Professional Exports
- **Excel Reports**: Detailed spreadsheet with all calculations
- **PDF Reports**: Professional summary for client presentations
- **Timestamped Files**: Organized file naming for record keeping

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. **Clone or Download the Application**
   ```bash
   git clone <repository-url>
   cd route-cost-estimator
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run route_cost_estimator.py
   ```

4. **Access the App**
   - Open your browser to `http://localhost:8501`
   - The application will automatically load

## 📖 How to Use

### 1. Enter Trip Details
Use the sidebar to input your route information:
- **Loading/Offloading Points**: Enter location names
- **Distance**: Trip distance in kilometers
- **Load**: Weight in tons
- **Fuel Price**: Current diesel price per liter
- **Toll Fees**: Total expected toll costs
- **Turnaround Time**: Total trip time including loading/unloading
- **Rate per Ton**: Your quoted or target rate
- **Payment Terms**: Choose from Cash, Daily, Weekly, or Monthly

### 2. Review Cost Analysis
The main dashboard shows:
- **Cost Breakdown**: Detailed breakdown of all trip costs
- **Financial Summary**: Revenue, costs, profit, and margins
- **Recommendations**: Suggested rates for profitable operations
- **Risk Assessment**: Payment term risk analysis

### 3. Use the What-If Simulator
- **Adjust Variables**: Use sliders to modify key parameters
- **Compare Scenarios**: See original vs. simulated results
- **Test Strategies**: Explore different pricing and cost scenarios
- **Make Informed Decisions**: Use insights for negotiations

### 4. Export Professional Reports
- **Excel Export**: Download detailed spreadsheet analysis
- **PDF Export**: Generate professional client-ready reports
- **Save Records**: Keep timestamped files for your records

## 🎛️ Advanced Settings

Access additional configuration options in the sidebar:
- **Fuel Efficiency**: Customize km per liter for your vehicle
- **Driver Rates**: Adjust daily driver compensation
- **Maintenance Costs**: Set maintenance cost per kilometer
- **Insurance Rates**: Configure insurance cost per ton
- **Depreciation**: Set vehicle depreciation per kilometer

## 💡 Pro Tips

### For Maximum Accuracy
- **Update Fuel Prices**: Use current market rates
- **Include All Tolls**: Research exact toll costs for your route
- **Realistic Turnaround**: Factor in loading/unloading and rest stops
- **Regular Maintenance**: Use actual maintenance costs from your records

### For Better Profitability
- **Target 20%+ Margins**: Use recommended rates as starting points
- **Factor Payment Terms**: Consider cashflow impact in pricing
- **Test Scenarios**: Use what-if simulator before finalizing quotes
- **Track Actuals**: Compare estimates with actual costs to improve accuracy

### For Risk Management
- **Cash Flow**: Prefer shorter payment terms when possible
- **Fuel Hedging**: Consider fuel price volatility in long-term contracts
- **Route Optimization**: Compare multiple route options
- **Market Research**: Use simulator to understand competitive pricing

## 🎯 Target Users

- **Trucking Company Owners**: Optimize fleet profitability
- **Freelance Transporters**: Price jobs competitively and profitably
- **Logistics Coordinators**: Evaluate transport options and costs
- **SME Fleet Managers**: Make data-driven operational decisions

## 📈 Business Benefits

- **Increased Profitability**: Eliminate underpriced jobs
- **Better Decision Making**: Data-driven route selection
- **Professional Image**: Client-ready reports and analysis
- **Risk Mitigation**: Understand cashflow and operational risks
- **Competitive Advantage**: Quick, accurate quoting capability

## 🔧 Technical Details

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with pandas for data processing
- **Export**: xlsxwriter (Excel) and reportlab (PDF)
- **Styling**: Custom CSS for professional appearance

### Cost Calculation Components
1. **Fuel Costs**: Distance ÷ Efficiency × Fuel Price
2. **Driver Costs**: (Turnaround Time ÷ 24) × Daily Rate
3. **Maintenance**: Distance × Maintenance Rate per km
4. **Insurance**: Load Weight × Insurance Rate per ton
5. **Depreciation**: Distance × Depreciation Rate per km
6. **Tolls**: Direct input from user

### Risk Assessment Factors
- **Cash**: 1.0x (no adjustment)
- **Daily**: 1.02x risk factor
- **Weekly**: 1.05x risk factor
- **Monthly**: 1.15x risk factor

## 🚧 Future Enhancements

Potential improvements for future versions:
- **Route Mapping**: Integration with mapping services for distance calculation
- **Fuel Price APIs**: Automatic fuel price updates
- **Historical Tracking**: Job history and performance analytics
- **Multi-Vehicle Support**: Fleet-wide cost analysis
- **Mobile App**: Native mobile application
- **API Integration**: Connect with transport management systems

## 📞 Support

For questions, feature requests, or technical support:
- Review this README for usage guidance
- Check the application's built-in help text
- Test with sample data to understand functionality

## 📄 License

This application is provided as-is for transportation cost estimation purposes. Users are responsible for validating calculations against their specific operational requirements.

---

**Transform your transport business with data-driven decision making. Start estimating smarter routes today!** 🚛✨