import io
import fitz  # PyMuPDF
import docx
import pandas as pd

def parse_file(uploaded_file):
    """
    Parses an uploaded file based on its extension and returns the extracted text.
    uploaded_file is a streamlit UploadedFile object.
    """
    file_extension = uploaded_file.name.split('.')[-1].lower()
    file_bytes = uploaded_file.read()
    
    text_content = f"Filename: {uploaded_file.name}\n"
    
    if file_extension == 'pdf':
        try:
            doc = fitz.open("pdf", file_bytes)
            for page in doc:
                text_content += page.get_text() + "\n"
        except Exception as e:
            text_content += f"[Error parsing PDF: {e}]\n"
            
    elif file_extension == 'docx':
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                text_content += para.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    text_content += " | ".join([cell.text for cell in row.cells]) + "\n"
        except Exception as e:
            text_content += f"[Error parsing DOCX: {e}]\n"
            
    elif file_extension == 'xlsx':
        try:
            # Read all sheets
            excel_data = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
            for sheet_name, df in excel_data.items():
                text_content += f"--- Sheet: {sheet_name} ---\n"
                text_content += df.to_string(index=False) + "\n"
        except Exception as e:
            text_content += f"[Error parsing XLSX: {e}]\n"
            
    else:
        text_content += "[Unsupported file format]"
        
    # Reset file pointer if needed by other components, though we just read it fully
    uploaded_file.seek(0)
    
    return text_content
