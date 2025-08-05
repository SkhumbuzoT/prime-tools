import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
from PIL import Image
from typing import Optional, Dict

# Configure page
st.set_page_config(page_title="Precision Slip Data Extractor", layout="centered")
st.title("🔍 Precision Slip Data Extractor")

# Initialize session state for extracted data
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {
        'date': '',
        'truck_id': '',
        'quantity': '',
        'quantity_type': 'litres',
        'slip_number': ''
    }

def install_tesseract_instructions():
    """Show instructions for installing Tesseract OCR"""
    with st.expander("How to install Tesseract OCR for automatic text extraction"):
        st.markdown("""
        ### For automatic text recognition, you need to install Tesseract OCR:

        **Windows:**
        1. Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
        2. Add Tesseract to your PATH during installation
        3. Restart your computer

        **Mac:**
        ```bash
        brew install tesseract
        ```

        **Linux (Debian/Ubuntu):**
        ```bash
        sudo apt install tesseract-ocr
        sudo apt install libtesseract-dev
        ```

        Then install the Python package:
        ```bash
        pip install pytesseract
        ```
        """)

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    install_tesseract_instructions()

def extract_data_from_image(image: Image.Image) -> Optional[Dict[str, str]]:
    """Enhanced text extraction with better pattern matching"""
    try:
        # Custom OCR configuration for better accuracy
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/-:. '
        text = pytesseract.image_to_string(image, config=custom_config)
        
        result = {
            'date': '',
            'truck_id': '',
            'quantity': '',
            'quantity_type': 'litres',
            'slip_number': ''
        }
        
        # Improved date patterns (more formats and validation)
        date_patterns = [
            r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',  # DD/MM/YYYY or DD-MM-YYYY
            r'\b\d{4}[/-]\d{2}[/-]\d{2}\b',   # YYYY/MM/DD or YYYY-MM-DD
            r'\b\d{2}\s[A-Za-z]{3}\s\d{4}\b',  # DD MMM YYYY
            r'\b[A-Za-z]{3}\s\d{2},\s\d{4}\b'  # MMM DD, YYYY
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                result['date'] = matches[0]  # Take first match
                break
        
        # Enhanced truck ID patterns (regional variations)
        truck_patterns = [
            r'\b[A-Z]{2,3}\s?\d{3,6}\s?[A-Z]{0,2}\b',  # Standard plates
            r'\b[A-Z]{2}\d{3}[A-Z]{2}\b',              # Compact format
            r'(?:TRUCK|REG|VEHICLE)[\s:-]*([A-Z0-9\s]+)',  # Labeled
            r'\b\d{3}[A-Z]{2}\d{3}\b'                  # Alternative format
        ]
        
        for pattern in truck_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['truck_id'] = match.group().strip()
                break
        
        # Quantity extraction with unit detection
        quantity_patterns = [
            r'(?:LITERS|LITRES|QTY|QUANTITY|AMOUNT)[\s:-]*(\d+\.?\d*)\s*(L|KG|T|TONS?)',  # Labeled with unit
            r'\b(\d+\.?\d*)\s*(L|LTR|LITERS?|KG|KGS|TONS?|T)\b',  # Value followed by unit
            r'\b(\d+\.?\d*)\s*(?:L|KG|T)\b'  # Compact unit format
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['quantity'] = match.group(1)
                unit = match.group(2).upper() if match.group(2) else ''
                if 'T' in unit or 'KG' in unit:
                    result['quantity_type'] = 'tons'
                break
        
        # Slip number extraction with validation
        slip_patterns = [
            r'(?:SLIP|REF|DOC|INV)[\s#:-]*([A-Z0-9-]{5,})',  # Labeled
            r'\b[A-Z]{2,3}\d{5,}\b',  # Common invoice formats
            r'\b\d{5,}\b',             # Long numbers
            r'\b[A-Z0-9-]{8,}\b'       # Mixed alphanumeric
        ]
        
        for pattern in slip_patterns:
            match = re.search(pattern, text)
            if match:
                result['slip_number'] = match.group()
                break
        
        return result
        
    except Exception as e:
        st.error(f"OCR processing error: {str(e)}")
        return None

# File upload section
uploaded_file = st.file_uploader("Upload Slip Image", type=["png", "jpg", "jpeg"], 
                               help="Upload a clear image of your delivery or fuel slip")

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Slip", use_container_width=True)
    
    if OCR_AVAILABLE and st.button("Extract Data Automatically"):
        with st.spinner("Analyzing slip image..."):
            extracted_data = extract_data_from_image(image)
            
            if extracted_data:
                st.session_state.extracted_data = extracted_data
                st.success("Data extracted successfully! Please verify below.")
            else:
                st.error("Automatic extraction failed. Please enter data manually.")

# Data entry form with extracted values as defaults
with st.form("data_verification"):
    st.subheader("Verify/Enter Slip Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.text_input(
            "Date (DD/MM/YYYY)", 
            value=st.session_state.extracted_data['date'],
            help="Format: DD/MM/YYYY or any standard date format"
        )
        truck_id = st.text_input(
            "Truck ID/Registration", 
            value=st.session_state.extracted_data['truck_id'],
            help="Vehicle registration number"
        )
    
    with col2:
        quantity_type = st.selectbox(
            "Quantity Type",
            ["litres", "tons"],
            index=0 if st.session_state.extracted_data['quantity_type'] == 'litres' else 1
        )
        quantity = st.text_input(
            f"Quantity ({quantity_type})", 
            value=st.session_state.extracted_data['quantity'],
            help="Numeric value only"
        )
        slip_number = st.text_input(
            "Slip/Reference Number", 
            value=st.session_state.extracted_data['slip_number'],
            help="Document reference number"
        )
    
    submitted = st.form_submit_button("Generate Report")

if submitted:
    # Validation
    errors = []
    if not date:
        errors.append("Date is required")
    if not truck_id:
        errors.append("Truck ID is required")
    if not quantity:
        errors.append("Quantity is required")
    elif not quantity.replace('.', '', 1).isdigit():
        errors.append("Quantity must be a number")
    
    if errors:
        for error in errors:
            st.error(error)
    else:
        # Create report
        report_data = {
            "Date": [date],
            "Truck ID": [truck_id.upper()],
            "Quantity Type": [quantity_type],
            "Quantity": [float(quantity)],
            "Slip Number": [slip_number],
            "Processed Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        
        df = pd.DataFrame(report_data)
        
        # Excel generation
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Slip Data")
            # Add formatting
            workbook = writer.book
            worksheet = writer.sheets["Slip Data"]
            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white'})
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)
        
        towrite.seek(0)
        
        # Download
        st.download_button(
            "📥 Download Excel Report",
            data=towrite,
            file_name=f"slip_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Preview
        st.subheader("Report Preview")
        st.dataframe(df.style.format({"Quantity": "{:.2f}"}), hide_index=True)
