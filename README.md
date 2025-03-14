# 📄 PDF Name Overlay Tool
A web-based tool to overlay and index names from Excel files onto PDF documents, enhancing searchability and readability.

Deployed on streamlit: https://pdf-overlay-dewiypvjjeu85ja4xbsjqf.streamlit.app/

## Features
- **Excel Integration**: Supports `.xlsx` and `.xls` files with multiple names per ID.
- **PDF Annotation**: Adds customizable, searchable text overlays to PDFs.
- **Customization**: Adjust font size, text color, background color, opacity, and positioning.
- **Real-time Preview**: Instant visual feedback for text placement and styling.
- **Downloadable Output**: Generates annotated PDFs ready for download.

## Technical Stack
- **Frontend**: Streamlit
- **Data Handling**: pandas, numpy
- **PDF Processing**: PyMuPDF (fitz)
- **Temporary File Management**: Secure handling and automatic cleanup

## Performance
- Handles PDFs up to 50MB and Excel files with up to 1000 entries.
- Processes documents efficiently within 60 seconds.

