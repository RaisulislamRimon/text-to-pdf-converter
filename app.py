from flask import Flask, request, send_file, render_template, redirect, url_for
from fpdf import FPDF
import os
import chardet

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure upload and output directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']


def convert_to_pdf(input_path, output_path):
    """Convert a .txt file to a .pdf file."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Detect the file encoding
    encoding = detect_encoding(input_path)

    # Read the .txt file with utf-8 encoding and add its content to the PDF
    with open(input_path, 'r', encoding=encoding) as file:
        for line in file:
            pdf.multi_cell(0, 10, txt=line.strip())

    # Save the PDF
    pdf.output(output_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Home page with file upload form."""
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return "No file uploaded", 400

        file = request.files['file']

        # Check if the file is valid
        if file.filename == '':
            return "No file selected", 400

        if file and allowed_file(file.filename):
            # Save the uploaded file
            txt_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(txt_file_path)

            # Convert the .txt file to .pdf
            pdf_file_name = file.filename.replace('.txt', '.pdf')
            pdf_file_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_file_name)
            convert_to_pdf(txt_file_path, pdf_file_path)

            # Redirect to the download page
            return redirect(url_for('download_file', filename=pdf_file_name))

        return "Invalid file format. Only .txt files are allowed.", 400

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    """Serve the generated PDF for download."""
    pdf_file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(pdf_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)