# filepath: ocr_to_excel_app.py

import streamlit as st
from paddleocr import PaddleOCR
import pandas as pd
import tempfile
import os

# Configure OCR with structure recovery
def initialize_ocr():
    return PaddleOCR(use_angle_cls=True, lang='en', show_log=False, det=True, rec=True, structure=True)

# Run OCR and extract table structure
def extract_tables(image_path, ocr_model):
    return ocr_model.ocr(image_path, det=True, rec=True, structure=True)

# Convert OCR structure output to Excel using pandas
def write_excel_from_ocr_result(result):
    output = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    writer = pd.ExcelWriter(output.name, engine='xlsxwriter')

    for i, item in enumerate(result):
        elements = item.get('res', [])
        for element in elements:
            if element['type'] == 'table':
                table = element['html']
                df_list = pd.read_html(table)
                for idx, df in enumerate(df_list):
                    df.to_excel(writer, sheet_name=f'table_{i}_{idx}', index=False)

    writer.close()
    return output.name

# Streamlit UI
def main():
    st.set_page_config(page_title="Image to Excel using PaddleOCR")
    st.title("🧾 Table Extraction to Excel")

    uploaded_file = st.file_uploader("Upload an image with table", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        st.info("Running OCR... this may take a moment.")
        ocr_model = initialize_ocr()
        result = extract_tables(tmp_path, ocr_model)
        excel_path = write_excel_from_ocr_result(result)

        with open(excel_path, "rb") as f:
            st.download_button(
                label="📥 Download Excel File",
                data=f,
                file_name="extracted_table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == '__main__':
    main()
