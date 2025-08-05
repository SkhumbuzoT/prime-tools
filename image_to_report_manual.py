import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
from PIL import Image
from typing import Optional, Dict, Literal

# Configure page
st.set_page_config(page_title="Smart Document Processor", layout="centered")
st.title("📄 Smart Document Processor")

# Document type definitions
DocumentType = Literal['fuel_slip', 'dispatch_note', 'unknown']

def detect_document_type(text: str) -> DocumentType:
    """Auto-detects document type based on content"""
    text = text.lower()
    
    # Check for fuel slip indicators
    fuel_indicators = ['diesel', 'liters', 'attendant', 'bowsers']
    if any(indicator in text for indicator in fuel_indicators):
        return 'fuel_slip'
    
    # Check for dispatch note indicators
    dispatch_indicators = ['receiving note', 'axle group', 'client', 'product']
    if any(indicator in text for indicator in dispatch_indicators):
        return 'dispatch_note'
    
    return 'unknown'

def extract_fuel_slip_data(text: str) -> Dict[str, str]:
    """Enhanced extraction for fuel slips"""
    result = {
        'document_type': 'fuel_slip',
        'date': '',
        'truck_id': '',
        'quantity': '',
        'quantity_type': 'litres',
        'slip_number': '',
        'attendant': '',
        'company': ''
    }
    
    # Improved date extraction (handles multiple formats)
    date_patterns = [
        r'Date:\s*(\d{2})\s*[-/]\s*(\d{2})\s*[-/]\s*(\d{4})',  # DD-MM-YYYY or DD/MM/YYYY
        r'Date\s*[\#:]?\s*(\d{4})[/-](\d{2})[/-](\d{2})',      # YYYY/MM/DD
        r'(\d{2})\s*([A-Za-z]{3})\s*(\d{4})'                   # DD MMM YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result['date'] = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            break
    
    # Machine/Truck ID extraction
    machine_match = re.search(r'MACHINE\s*[\|:]#?\s*([A-Z0-9]+)\b', text)
    if machine_match:
        result['truck_id'] = machine_match.group(1)
    
    # Quantity extraction
    quantity_match = re.search(r'(LITERS|LITRES|QTY)\s*[\|:]#?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if quantity_match:
        result['quantity'] = quantity_match.group(2)
        result['quantity_type'] = 'litres'
    
    # Slip number extraction
    slip_match = re.search(r'^\s*([A-Z0-9]{6})\s*$', text, re.MULTILINE) or \
                re.search(r'(SLIP|DOC|REF)\s*[\#:]?\s*([A-Z0-9]+)\b', text, re.IGNORECASE)
    if slip_match:
        result['slip_number'] = slip_match.group(1 if slip_match.lastindex == 1 else 2)
    
    # Additional fields
    attendant_match = re.search(r'Attendant\s*[\|:]#?\s*([A-Z\s]+)\b', text)
    if attendant_match:
        result['attendant'] = attendant_match.group(1).strip()
    
    company_match = re.search(r'COMPANY NAME\s*[\|:]#?\s*([A-Z]+)\b', text)
    if company_match:
        result['company'] = company_match.group(1)
    
    return result

def extract_dispatch_note_data(text: str) -> Dict[str, str]:
    """Specialized extraction for dispatch notes"""
    result = {
        'document_type': 'dispatch_note',
        'date': '',
        'client': '',
        'product': '',
        'gross_weight': '',
        'tare_weight': '',
        'net_weight': '',
        'reference': ''
    }
    
    # Date extraction
    date_match = re.search(r'Date\s*[\#:]?\s*(\d{4})[/-](\d{2})[/-](\d{2})', text)
    if date_match:
        result['date'] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    
    # Client and product
    client_match = re.search(r'Client\s*[\#:]?\s*([^\n]+)', text)
    if client_match:
        result['client'] = client_match.group(1).strip()
    
    product_match = re.search(r'Product\s*[\#:]?\s*([^\n]+)', text)
    if product_match:
        result['product'] = product_match.group(1).strip()
    
    # Weight extraction (looking for JVM which appears to be gross weight in your example)
    weight_match = re.search(r'JVM\s*[\#:]?\s*(\d+)\s*k?g', text, re.IGNORECASE)
    if weight_match:
        result['gross_weight'] = weight_match.group(1)
    
    # Reference number
    ref_match = re.search(r'Website Key:\s*([A-Z0-9]+)', text) or \
               re.search(r'Dropbox Name:\s*([^\n]+)', text)
    if ref_match:
        result['reference'] = ref_match.group(1).strip()
    
    return result

def process_uploaded_file(uploaded_file):
    """Main processing function"""
    try:
        image = Image.open(uploaded_file)
        
        # OCR with enhanced configuration
        custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
        text = pytesseract.image_to_string(image, config=custom_config)
        
        # Detect and process document type
        doc_type = detect_document_type(text)
        
        if doc_type == 'fuel_slip':
            return extract_fuel_slip_data(text)
        elif doc_type == 'dispatch_note':
            return extract_dispatch_note_data(text)
        else:
            st.warning("Document type not recognized. Using generic extraction.")
            return {'document_type': 'unknown', 'raw_text': text}
            
    except Exception as e:
        st.error(f"Processing error: {str(e)}")
        return None

# Streamlit UI
uploaded_file = st.file_uploader("Upload Document", type=["png", "jpg", "jpeg"])

if uploaded_file:
    extracted_data = process_uploaded_file(uploaded_file)
    
    if extracted_data:
        st.session_state.extracted_data = extracted_data
        st.success("Data extracted successfully!")
        
        # Show preview with document-type specific display
        if extracted_data['document_type'] == 'fuel_slip':
            st.subheader("Fuel Slip Data")
            cols = st.columns(2)
            cols[0].metric("Date", extracted_data.get('date', 'N/A'))
            cols[1].metric("Truck ID", extracted_data.get('truck_id', 'N/A'))
            st.metric("Quantity", f"{extracted_data.get('quantity', 'N/A')} {extracted_data.get('quantity_type', '')}")
            
        elif extracted_data['document_type'] == 'dispatch_note':
            st.subheader("Dispatch Note Data")
            st.metric("Gross Weight", f"{extracted_data.get('gross_weight', 'N/A')} kg")
            st.metric("Client", extracted_data.get('client', 'N/A'))
            
        # Show raw extraction for debugging
        with st.expander("View raw extracted data"):
            st.json(extracted_data)
        
        # Generate report
        if st.button("Generate Report"):
            df = pd.DataFrame([extracted_data])
            towrite = io.BytesIO()
            
            with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                
                # Format headers
                header_fmt = workbook.add_format({
                    'bold': True,
                    'border': 1,
                    'bg_color': '#4472C4',
                    'font_color': 'white'
                })
                
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_fmt)
            
            towrite.seek(0)
            
            st.download_button(
                "📥 Download Report",
                data=towrite,
                file_name=f"{extracted_data['document_type']}_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.info("Please upload a document to begin processing")
