from flask import Flask, request, send_file
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
    <h2>Meu PDF Tool</h2>

    <h3>Juntar PDFs</h3>
    <form method="POST" action="/merge" enctype="multipart/form-data">
        <input type="file" name="pdfs" multiple required>
        <button type="submit">Juntar</button>
    </form>

    <h3>Proteger PDF</h3>
    <form method="POST" action="/protect" enctype="multipart/form-data">
        <input type="file" name="file" required><br><br>
        <input type="password" name="password" placeholder="Senha" required><br><br>
        <button type="submit">Proteger</button>
    </form>

    <h3>Word → PDF</h3>
    <form method="POST" action="/word_to_pdf" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Converter</button>
    </form>

    <h3>PDF → Word</h3>
    <form method="POST" action="/pdf_to_word" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Converter</button>
    </form>

    <h3>Imagem → PDF</h3>
    <form method="POST" action="/image_to_pdf" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Converter</button>
    </form>

    <h3>PDF → Imagem</h3>
    <form method="POST" action="/pdf_to_image" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Converter</button>
    </form>
    '''

@app.route("/merge", methods=["POST"])
def merge():
    files = request.files.getlist("pdfs")
    merger = PdfMerger()
    for file in files:
        merger.append(file)
    output = "merged.pdf"
    merger.write(output)
    merger.close()
    return send_file(output, as_attachment=True)

@app.route("/protect", methods=["POST"])
def protect():
    file = request.files["file"]
    password = request.form["password"]
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    output = "protected.pdf"
    with open(output, "wb") as f:
        writer.write(f)
    return send_file(output, as_attachment=True)

@app.route("/word_to_pdf", methods=["POST"])
def word_to_pdf():
    file = request.files["file"]
    doc = Document(file)
    output = "converted.pdf"
    pdf = SimpleDocTemplate(output)
    styles = getSampleStyleSheet()
    elements = []
    for para in doc.paragraphs:
        elements.append(Paragraph(para.text, styles["Normal"]))
    pdf.build(elements)
    return send_file(output, as_attachment=True)

@app.route("/pdf_to_word", methods=["POST"])
def pdf_to_word():
    file = request.files["file"]
    input_path = "temp.pdf"
    output_path = "converted.docx"
    file.save(input_path)
    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()
    return send_file(output_path, as_attachment=True)

@app.route("/image_to_pdf", methods=["POST"])
def image_to_pdf():
    file = request.files["file"]
    image = Image.open(file).convert("RGB")
    output = "converted.pdf"
    image.save(output)
    return send_file(output, as_attachment=True)

@app.route("/pdf_to_image", methods=["POST"])
def pdf_to_image():
    file = request.files["file"]
    input_path = "temp.pdf"
    file.save(input_path)
    images = convert_from_path(input_path)
    output = "converted.jpg"
    images[0].save(output, "JPEG")
    return send_file(output, as_attachment=True)

if __name__ == "__main__":
    app.run()
