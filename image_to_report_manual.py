
import streamlit as st
import pandas as pd
import io
from PIL import Image

st.set_page_config(page_title="Image to Report (Manual)", layout="centered")

st.title("📸 Image to Report (Manual Entry)")

st.markdown("""
Upload a photo of your slip for reference, then manually enter the values below.  
We'll generate a structured Excel report you can download.
""")

uploaded_file = st.file_uploader("Upload Image (optional)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Slip", use_column_width=True)

# Manual input form
litres = st.number_input("Litres", min_value=0.0)
price_per_litre = st.number_input("Price per Litre (ZAR)", min_value=0.0)
total = litres * price_per_litre
truck_reg = st.text_input("Truck Registration Number")
date = st.date_input("Slip Date")

if st.button("Generate Excel Report"):
    df = pd.DataFrame([{
        "Date": date,
        "Truck Reg": truck_reg,
        "Litres": litres,
        "Price/Litre": price_per_litre,
        "Total (ZAR)": total
    }])
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    st.download_button(
        "📥 Download Report",
        data=towrite,
        file_name="image_to_report_manual.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
