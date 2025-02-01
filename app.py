import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import numpy as np
from collections import defaultdict
import tempfile
import os
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(
    page_title="PDF Name Overlay Tool",
    page_icon="📄",
    layout="wide"
)

def create_text_preview(text, font_size, text_color, bg_color, bg_opacity):
    # Create a sample image with the text styling
    img = Image.new('RGBA', (400, 100), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Convert colors from float (0-1) to integer (0-255)
    bg_color_int = tuple(int(c * 255) for c in bg_color)
    text_color_int = tuple(int(c * 255) for c in text_color)
    
    # Create background color with opacity
    bg_with_opacity = (*bg_color_int, int(bg_opacity * 255))
    
    # Draw background
    draw.rectangle([(0, 0), (400, 100)], fill=bg_with_opacity)
    
    # Draw text
    draw.text((10, 10), text, fill=text_color_int, font=None, size=font_size)
    return img

def process_files(excel_file, pdf_file, text_settings):
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
        
        # Create a dictionary where each ID maps to a list of names
        id_to_names = defaultdict(list)
        
        for idx, row in df.iterrows():
            if pd.notna(row['Sorszam']) and pd.notna(row['Nev']):
                id_num = int(float(row['Sorszam']))
                # Split the names on comma and clean each name
                names = [name.strip() for name in str(row['Nev']).split(',')]
                for name in names:
                    if name.strip():
                        id_to_names[id_num].append(name.strip())
        
        st.write(f"Loaded {len(id_to_names)} IDs from Excel")
        multi_names = sum(1 for names in id_to_names.values() if len(names) > 1)
        st.write(f"Found {multi_names} IDs with multiple names")

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
                            try:
                                id_num = int(float(text))
                                x0, y0 = span["origin"]
                                
                                if id_num in id_to_names:
                                    names = id_to_names[id_num]
                                    visible_text = "\n".join(names)
                                    
                                    # Calculate rectangle height based on number of names
                                    rect_height = len(names) * text_settings['font_size'] * 1.2
                                    
                                    # Create a semi-transparent text annotation
                                    shape = page.new_shape()
                                    rect = fitz.Rect(
                                        x0 + text_settings['x_offset'],
                                        y0 + text_settings['y_offset'] - rect_height,
                                        x0 + text_settings['x_offset'] + max(len(n) for n in names) * text_settings['font_size'] * 0.6,
                                        y0 + text_settings['y_offset']
                                    )
                                    shape.draw_rect(rect)
                                    shape.finish(
                                        color=text_settings['bg_color'],
                                        fill=text_settings['bg_color'],
                                        fill_opacity=text_settings['bg_opacity']
                                    )
                                    shape.commit()
                                    
                                    # Add the text
                                    page.insert_text(
                                        (x0 + text_settings['x_offset'], y0 + text_settings['y_offset'] - rect_height + text_settings['font_size']),
                                        visible_text,
                                        fontsize=text_settings['font_size'],
                                        color=text_settings['text_color']
                                    )
                                    
                                    # Add invisible but searchable text
                                    search_text = f"{' '.join(names)} {id_num}"
                                    page.insert_text(
                                        (x0, y0),
                                        search_text,
                                        fontsize=0.1,
                                        color=(1, 1, 1)
                                    )
                            except ValueError:
                                continue
            
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

def main():
    st.title("PDF Name Overlay Tool")
    st.write("Upload your Excel file with IDs and names, and a PDF file to add searchable names to it.")

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

    # Text customization section
    st.subheader("Text Customization")
    col1, col2 = st.columns(2)
    
    with col1:
        font_size = st.slider("Font Size", 6, 20, 8)
        text_color = st.color_picker("Text Color", "#000000")
        x_offset = st.slider("X Offset", -50, 50, 0)
        
    with col2:
        bg_color = st.color_picker("Background Color", "#FFFFFF")
        bg_opacity = st.slider("Background Opacity", 0.0, 1.0, 0.7)
        y_offset = st.slider("Y Offset", -50, 50, -8)

    # Convert color from hex to RGB tuple
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

    text_settings = {
        'font_size': font_size,
        'text_color': hex_to_rgb(text_color),
        'bg_color': hex_to_rgb(bg_color),
        'bg_opacity': bg_opacity,
        'x_offset': x_offset,
        'y_offset': y_offset
    }

    # Preview section
    if excel_file:
        st.subheader("Preview")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Text Style Preview")
            preview = create_text_preview(
                "Sample Name\nSecond Name",
                text_settings['font_size'],
                text_settings['text_color'],
                text_settings['bg_color'],
                text_settings['bg_opacity']
            )
            st.image(preview, use_column_width=True)
        
        if pdf_file:
            with col2:
                st.write("PDF Preview (First occurrence)")
                # Create a preview of the PDF with overlay
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
                    tmp_pdf.write(pdf_file.getvalue())
                    pdf_doc = fitz.open(tmp_pdf.name)
                    page = pdf_doc[0]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_bytes = pix.tobytes()
                    st.image(img_bytes, use_column_width=True)
                    pdf_doc.close()
                    os.unlink(tmp_pdf.name)

    # Process button
    if excel_file and pdf_file:
        if st.button("Process PDF"):
            with st.spinner("Processing your files..."):
                try:
                    processed_pdf = process_files(excel_file, pdf_file, text_settings)
                    
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

if __name__ == "__main__":
    main() 
