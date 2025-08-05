
import streamlit as st

st.set_page_config(page_title="LOI Calculator", layout="centered")

st.title("🚛 LOI Calculator for Trucking Profitability")

st.markdown("Use this calculator to estimate the profitability of a trucking route based on distance, load, diesel price, and truck efficiency.")

tons = st.number_input("Load (Tons)", min_value=1.0)
distance = st.number_input("Distance (km)", min_value=1.0)
rate_per_ton = st.number_input("Rate per Ton (ZAR)", min_value=0.0)
diesel_price = st.number_input("Diesel Price per Litre (ZAR)", min_value=0.0)
fuel_efficiency = st.number_input("Fuel Efficiency (km per litre)", min_value=0.1)

if st.button("Calculate LOI"):
    revenue = tons * rate_per_ton
    diesel_needed = distance / fuel_efficiency
    diesel_cost = diesel_needed * diesel_price
    profit = revenue - diesel_cost
    loi = (profit / revenue * 100) if revenue > 0 else 0

    st.markdown("### 🧾 Results")
    st.write(f"**Revenue:** ZAR {revenue:,.2f}")
    st.write(f"**Diesel Needed:** {diesel_needed:.2f} litres")
    st.write(f"**Diesel Cost:** ZAR {diesel_cost:,.2f}")
    st.write(f"**Profit:** ZAR {profit:,.2f}")
    st.write(f"**LOI (Profit Margin):** {loi:.2f}%")
