# PDF Name Overlay Tool - Product Requirements Document

## Overview
The PDF Name Overlay Tool is a web application that adds searchable name labels to a PDF containing numbered locations. It's specifically designed to work with cemetery maps where numbers on the map need to be associated with names from an Excel file.

## Core Features

### 1. File Input
- **Excel File Upload**
  - Supports .xlsx and .xls formats
  - Required columns: 'Sorszam' (ID number) and 'Nev' (Name)
  - Handles multiple names per ID (comma-separated)
  - Validates data format and provides feedback

- **PDF File Upload**
  - Supports .pdf format
  - Must contain readable numbers that correspond to Excel IDs
  - Preserves original PDF quality and content

### 2. Text Customization
- **Font Settings**
  - Adjustable font size (6-20pt)
  - Color picker for text color
  - Default: 8pt black text

- **Background Settings**
  - Color picker for background color
  - Adjustable opacity (0-100%)
  - Default: 70% opaque white background

- **Position Settings**
  - X-offset adjustment (-50 to +50 pixels)
  - Y-offset adjustment (-50 to +50 pixels)
  - Default: 0px X-offset, -8px Y-offset

### 3. Preview Features
- **Text Style Preview**
  - Live preview of text appearance
  - Shows sample text with current settings
  - Updates in real-time as settings change

- **PDF Preview**
  - Shows first page of PDF
  - 2x zoom for better visibility
  - Helps users position text correctly

### 4. Processing Features
- **Name Processing**
  - Groups multiple names by ID
  - Handles comma-separated names in Excel
  - Maintains name order from Excel

- **PDF Processing**
  - Adds visible text labels above numbers
  - Creates semi-transparent background boxes
  - Adds invisible searchable text layer
  - Preserves original PDF content

### 5. Output
- **Generated PDF**
  - Maintains original PDF quality
  - Includes visible name labels
  - Supports Ctrl+F search functionality
  - Downloadable result

## Technical Requirements

### 1. Performance
- Handle PDFs up to 50MB
- Process Excel files with up to 1000 entries
- Complete processing within 60 seconds
- Support concurrent users in cloud deployment

### 2. Compatibility
- Works with PDF versions 1.4 and newer
- Supports Excel 97-2003 (.xls) and newer (.xlsx)
- Functions in modern web browsers
- Deployable to Streamlit Cloud

### 3. Dependencies
```
streamlit>=1.24.0
PyMuPDF>=1.22.5
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.2
```

## User Interface Requirements

### 1. Layout
- Wide layout for better visibility
- Two-column design for controls
- Clear section separation
- Responsive design

### 2. User Feedback
- Upload success messages
- Processing progress bar
- Error messages for invalid files
- Success message with download button

### 3. Help Text
- Clear instructions for file requirements
- Tool tips for customization options
- Visual feedback for interactive elements

## Security Requirements

### 1. File Handling
- Secure temporary file creation
- Automatic cleanup of temporary files
- No permanent storage of uploaded files

### 2. Input Validation
- File type verification
- Data format validation
- Error handling for invalid inputs

## Deployment Requirements

### 1. Cloud Deployment
- Deployable to Streamlit Cloud
- Minimal setup requirements
- Environment variable support

### 2. Resource Usage
- Efficient memory management
- Temporary file cleanup
- Resource limit enforcement

## Future Considerations

### 1. Potential Enhancements
- Support for additional file formats
- Batch processing capabilities
- Custom font support
- Save/load configuration presets
- Multiple language support

### 2. Maintenance
- Version control
- Dependency updates
- Bug tracking and fixes
- Performance monitoring 