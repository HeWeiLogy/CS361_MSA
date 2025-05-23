from flask import Flask, request, jsonify
from docx import Document
import fitz  # PyMuPDF

app = Flask(__name__)

SUPPORTED_EXTENSIONS = {'txt', 'docx', 'pdf'}

def is_supported(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in SUPPORTED_EXTENSIONS

def txt_handler(file):
    return file.read().decode('utf-8', errors='ignore').strip()

def docx_handler(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

def pdf_handler(file):
    try:
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
        return text.strip()
    except Exception as e:
        raise ValueError(f"PDF processing error: {str(e)}")

def clean_up(text):
    lines = text.splitlines()
    cleaned_lines = [' '.join(line.strip().split()) for line in lines if line.strip()]
    return '\n'.join(cleaned_lines)

def validate_file():
    if 'file' not in request.files:
        return None, jsonify({"error": "No file part"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return None, jsonify({"error": "No selected file"}), 400
    
    if not is_supported(file.filename.lower()):
        return None, jsonify({
            "error": "Unsupported file type. Only .txt, .docx, and .pdf are allowed."
        }), 415
    
    return file, None, None

def extract_text(file):
    filename = file.filename.lower()

    if filename.endswith('.txt'):
        return txt_handler(file)
    
    elif filename.endswith('.docx'):
        return docx_handler(file)
    
    elif filename.endswith('.pdf'):
        return pdf_handler(file)

@app.route('/upload', methods=['POST'])
def text_extractor():
    file, err_msg, status = validate_file()

    if err_msg:
        return err_msg, status
    
    try:
        text = extract_text(file)

        return jsonify({"extracted_text": clean_up(text)})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=8000, debug=True)
