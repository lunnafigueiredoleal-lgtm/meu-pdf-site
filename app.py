from flask import Flask, request, send_file, after_this_request
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
from pdf2docx import Converter
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from pdf2image import convert_from_path
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Meu PDF Tool</title>
    <style>
        body {
            background-color: #0f172a;
            font-family: Arial, sans-serif;
            color: white;
            text-align: center;
            padding: 40px;
        }

        h2 {
            font-size: 32px;
            margin-bottom: 30px;
        }

        .card {
            background-color: #1e293b;
            padding: 20px;
            margin: 20px auto;
            border-radius: 12px;
            width: 400px;
            box-shadow: 0 0 15px rgba(0,0,0,0.4);
        }

        button {
            background-color: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }

        button:hover {
            background-color: #2563eb;
        }

        input[type="file"],
        input[type="password"] {
            margin-top: 10px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>

<h2>🌑 Meu PDF Tool</h2>

<div class="card">
    <h3>Juntar PDFs</h3>
    <form method="POST" action="/merge" enctype="multipart/form-data">
        <input type="file" name="pdfs" multiple required><br>
        <button type="submit">Juntar</button>
    </form>
</div>

<div class="card">
    <h3>Proteger PDF</h3>
    <form method="POST" action="/protect" enctype="multipart/form-data">
        <input type="file" name="file" required><br>
        <input type="password" name="password" placeholder="Senha" required><br>
        <button type="submit">Proteger</button>
    </form>
</div>

<div class="card">
    <h3>Word → PDF</h3>
    <form method="POST" action="/word_to_pdf" enctype="multipart/form-data">
        <input type="file" name="file" required><br>
        <button type="submit">Converter</button>
    </form>
</div>

<div class="card">
    <h3>PDF → Word</h3>
    <form method="POST" action="/pdf_to_word" enctype="multipart/form-data">
        <input type="file" name="file" required><br>
        <button type="submit">Converter</button>
    </form>
</div>

<div class="card">
    <h3>Imagem → PDF</h3>
    <form method="POST" action="/image_to_pdf" enctype="multipart/form-data">
        <input type="file" name="file" required><br>
        <button type="submit">Converter</button>
    </form>
</div>

<div class="card">
    <h3>PDF → Imagem</h3>
    <form method="POST" action="/pdf_to_image" enctype="multipart/form-data">
        <input type="file" name="file" required><br>
        <button type="submit">Converter</button>
    </form>
</div>

</body>
</html>
'''

# ---------------- MERGE ----------------
@app.route("/merge", methods=["POST"])
def merge():
    files = request.files.getlist("pdfs")
    merger = PdfMerger()

    for file in files:
        merger.append(file)

    output = f"{uuid.uuid4()}.pdf"
    merger.write(output)
    merger.close()

    @after_this_request
    def remove_file(response):
        try:
            os.remove(output)
        except:
            pass
        return response

    return send_file(output, as_attachment=True)

# ---------------- PROTECT ----------------
@app.route("/protect", methods=["POST"])
def protect():
    file = request.files["file"]
    password = request.form["password"]

    reader = PdfReader(file)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    output = f"{uuid.uuid4()}.pdf"
    with open(output, "wb") as f:
        writer.write(f)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(output)
        except:
            pass
        return response

    return send_file(output, as_attachment=True)

# ---------------- WORD → PDF ----------------
@app.route("/word_to_pdf", methods=["POST"])
def word_to_pdf():
    file = request.files["file"]
    doc = Document(file)

    output = f"{uuid.uuid4()}.pdf"
    pdf = SimpleDocTemplate(output)
    styles = getSampleStyleSheet()
    elements = []

    for para in doc.paragraphs:
        elements.append(Paragraph(para.text, styles["Normal"]))

    pdf.build(elements)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(output)
        except:
            pass
        return response

    return send_file(output, as_attachment=True)

# ---------------- PDF → WORD ----------------
@app.route("/pdf_to_word", methods=["POST"])
def pdf_to_word():
    file = request.files["file"]

    input_path = f"{uuid.uuid4()}.pdf"
    output_path = f"{uuid.uuid4()}.docx"

    file.save(input_path)

    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()

    @after_this_request
    def remove_file(response):
        try:
            os.remove(input_path)
            os.remove(output_path)
        except:
            pass
        return response

    return send_file(output_path, as_attachment=True)

# ---------------- IMAGE → PDF ----------------
@app.route("/image_to_pdf", methods=["POST"])
def image_to_pdf():
    file = request.files["file"]

    image = Image.open(file).convert("RGB")
    output = f"{uuid.uuid4()}.pdf"
    image.save(output)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(output)
        except:
            pass
        return response

    return send_file(output, as_attachment=True)

# ---------------- PDF → IMAGE ----------------
@app.route("/pdf_to_image", methods=["POST"])
def pdf_to_image():
    file = request.files["file"]

    input_path = f"{uuid.uuid4()}.pdf"
    output = f"{uuid.uuid4()}.jpg"

    file.save(input_path)

    images = convert_from_path(input_path)
    images[0].save(output, "JPEG")

    @after_this_request
    def remove_file(response):
        try:
            os.remove(input_path)
            os.remove(output)
        except:
            pass
        return response

    return send_file(output, as_attachment=True)

if __name__ == "__main__":
    app.run()
