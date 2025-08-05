import streamlit as st
import pandas as pd
import io
from PIL import Image
import pytesseract
from datetime import datetime
import re

# Configure page
st.set_page_config(page_title="Slip Data Extractor", layout="centered")
st.title("📄 Slip Data Extractor")

st.markdown("""
Upload an image of your slip (delivery/loading or fuel) for automatic data extraction.  
You can verify and edit the extracted data before generating the report.
""")

# File uploader
uploaded_file = st.file_uploader("Upload Slip Image", type=["png", "jpg", "jpeg"])

# Initialize session state for extracted data
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {
        'date': '',
        'truck_id': '',
        'quantity': '',
        'quantity_type': 'litres',  # default to litres
        'slip_number': ''
    }

def extract_data_from_image(image):
    """Extract text from image using OCR and try to find key information"""
    try:
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(image)
        
        # Initialize result dictionary
        result = {
            'date': '',
            'truck_id': '',
            'quantity': '',
            'quantity_type': 'litres',  # default to litres
            'slip_number': ''
        }
        
        # Try to find date (common formats)
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{2}-\d{2}-\d{4}',   # DD-MM-YYYY
            r'\d{4}/\d{2}/\d{2}',   # YYYY/MM/DD
            r'\d{2} \w{3} \d{4}',   # DD MMM YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    result['date'] = match.group()
                    break
                except:
                    continue
        
        # Try to find truck ID (common patterns like ABC 123 GP or similar)
        truck_patterns = [
            r'[A-Z]{2,3}\s?\d{3,6}\s?[A-Z]{0,2}',  # Standard truck reg
            r'TRUCK\s?ID[:]?\s?([A-Z0-9]+)',       # With "TRUCK ID" label
            r'REG\s?[:]?\s?([A-Z0-9]+)'            # With "REG" label
        ]
        
        for pattern in truck_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['truck_id'] = match.group().strip()
                break
        
        # Try to find quantity (litres or tons)
        quantity_patterns = [
            r'LITRES\s?[:]?\s?(\d+\.?\d*)',  # Litres with label
            r'QTY\s?[:]?\s?(\d+\.?\d*)',      # Generic quantity
            r'TONS\s?[:]?\s?(\d+\.?\d*)',     # Tons with label
            r'(\d+\.?\d*)\s?(L|KG|T)',        # Number followed by unit
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['quantity'] = match.group(1)
                if 'TON' in match.group().upper() or 'T' in match.group().upper():
                    result['quantity_type'] = 'tons'
                break
        
        # Try to find slip/reference number
        slip_patterns = [
            r'SLIP\s?NO[:]?\s?(\d+)',        # With "SLIP NO" label
            r'REF\s?NO[:]?\s?(\d+)',         # With "REF NO" label
            r'DOC\s?NO[:]?\s?(\d+)',          # With "DOC NO" label
            r'\b\d{5,}\b'                     # Any long number
        ]
        
        for pattern in slip_patterns:
            match = re.search(pattern, text)
            if match:
                result['slip_number'] = match.group()
                break
        
        return result
        
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Slip", use_column_width=True)
    
    if st.button("Extract Data from Image"):
        with st.spinner("Extracting data from image..."):
            extracted_data = extract_data_from_image(image)
            
            if extracted_data:
                st.session_state.extracted_data = extracted_data
                st.success("Data extracted successfully!")
            else:
                st.error("Could not extract data from image. Please enter manually.")

# Manual input form (pre-filled with extracted data if available)
with st.form("data_form"):
    st.subheader("Verify/Enter Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.text_input("Date", value=st.session_state.extracted_data['date'])
        truck_id = st.text_input("Truck ID/Registration", value=st.session_state.extracted_data['truck_id'])
    
    with col2:
        quantity_type = st.selectbox(
            "Quantity Type",
            ["litres", "tons"],
            index=0 if st.session_state.extracted_data['quantity_type'] == 'litres' else 1
        )
        quantity = st.text_input(f"{quantity_type.capitalize()}", value=st.session_state.extracted_data['quantity'])
        slip_number = st.text_input("Slip/Reference Number", value=st.session_state.extracted_data['slip_number'])
    
    submitted = st.form_submit_button("Generate Report")

if submitted:
    # Validate data
    if not all([date, truck_id, quantity]):
        st.warning("Please fill in all required fields (Date, Truck ID, and Quantity)")
    else:
        # Create DataFrame
        report_data = {
            "Date": [date],
            "Truck ID": [truck_id],
            "Quantity Type": [quantity_type],
            "Quantity": [float(quantity) if quantity.replace('.', '', 1).isdigit() else quantity],
            "Slip/Ref Number": [slip_number]
        }
        
        df = pd.DataFrame(report_data)
        
        # Create Excel file
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, engine='openpyxl')
        towrite.seek(0)
        
        # Download button
        st.download_button(
            "📥 Download Report",
            data=towrite,
            file_name=f"slip_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Show preview
        st.subheader("Report Preview")
        st.dataframe(df)
