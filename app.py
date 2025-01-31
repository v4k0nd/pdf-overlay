import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import numpy as np
import tempfile
import os

st.set_page_config(
    page_title="PDF Name Overlay",
    page_icon="📄",
    layout="wide"
)

st.title("PDF Name Overlay Tool")
st.write("Upload your Excel file with IDs and names, and a PDF file to add searchable names to it.")

def clean_and_split_names(name):
    """Clean and split names if multiple people are listed"""
    if pd.isna(name):
        return []
    
    # Convert to string in case it's a number or other type
    name = str(name).strip()
    if not name:  # Empty string
        return []
        
    # Split on common separators and clean each name
    names = []
    # First split by newline if present (for merged cells)
    for part in name.split('\n'):
        # Then split by comma or semicolon if present
        for subpart in part.split(','):
            for final_part in subpart.split(';'):
                cleaned = final_part.strip()
                if cleaned:  # Only add non-empty names
                    names.append(cleaned)
    return names

def process_files(excel_file, pdf_file):
    # Create temporary files to work with
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_excel:
        tmp_excel.write(excel_file.getvalue())
        excel_path = tmp_excel.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
        tmp_pdf.write(pdf_file.getvalue())
        pdf_path = tmp_pdf.name
        
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
        output_path = tmp_output.name

    try:
        # Read the Excel file
        df = pd.read_excel(excel_path)
        
        # Clean the data and create a dictionary with lists of names
        id_to_names = {}
        for _, row in df.iterrows():
            try:
                id_num = int(float(row['Sorszám'])) if pd.notna(row['Sorszám']) else None
                if id_num is not None:  # Only process valid IDs
                    names = clean_and_split_names(row['Név'])
                    if names:  # Only add if there are valid names
                        id_to_names[id_num] = names
            except (ValueError, TypeError):
                continue  # Skip invalid IDs
                
        st.write(f"Loaded {len(id_to_names)} IDs with names from Excel")
        
        # Display some statistics
        total_names = sum(len(names) for names in id_to_names.values())
        st.write(f"Total number of names: {total_names}")
        multi_name_count = sum(1 for names in id_to_names.values() if len(names) > 1)
        if multi_name_count > 0:
            st.write(f"Found {multi_name_count} IDs with multiple names")

        # Open the PDF
        pdf_doc = fitz.open(pdf_path)
        st.write(f"Processing PDF with {len(pdf_doc)} pages")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each page
        for page_num, page in enumerate(pdf_doc):
            status_text.write(f"Processing page {page_num + 1}")
            
            # Extract text blocks with their positions
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            # Try to convert text to integer, handling cases with decimal points
                            try:
                                id_num = int(float(text))
                                x0, y0 = span["origin"]
                                
                                # Get names from Excel data if ID exists
                                if id_num in id_to_names:
                                    names = id_to_names[id_num]
                                    # Join all names with a separator
                                    combined_text = " | ".join(names + [str(id_num)])
                                    
                                    # Add invisible but searchable text
                                    page.insert_text(
                                        (x0, y0),
                                        combined_text,
                                        fontsize=0.1,    # Very small, practically invisible
                                        color=(1, 1, 1),  # White color, invisible on white background
                                        render_mode=0
                                    )
                            except ValueError:
                                # Not a number, skip
                                continue
            
            # Update progress
            progress_bar.progress((page_num + 1) / len(pdf_doc))
        
        # Save the modified PDF
        pdf_doc.save(output_path)
        pdf_doc.close()
        
        # Read the processed file
        with open(output_path, 'rb') as file:
            processed_pdf = file.read()
            
        return processed_pdf
        
    finally:
        # Clean up temporary files
        for temp_file in [excel_path, pdf_path, output_path]:
            try:
                os.unlink(temp_file)
            except:
                pass

# File upload section
col1, col2 = st.columns(2)

with col1:
    excel_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
    if excel_file:
        st.success("Excel file uploaded successfully!")
        
with col2:
    pdf_file = st.file_uploader("Upload PDF file", type=['pdf'])
    if pdf_file:
        st.success("PDF file uploaded successfully!")

# Process button
if excel_file and pdf_file:
    if st.button("Process PDF"):
        with st.spinner("Processing your files..."):
            try:
                processed_pdf = process_files(excel_file, pdf_file)
                
                # Offer the processed file for download
                st.download_button(
                    label="Download Processed PDF",
                    data=processed_pdf,
                    file_name="processed.pdf",
                    mime="application/pdf"
                )
                st.success("Processing complete! Click the button above to download your file.")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
else:
    st.info("Please upload both Excel and PDF files to begin processing.") 
