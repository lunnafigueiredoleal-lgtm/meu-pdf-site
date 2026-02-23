from flask import Flask, request, send_file
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
from pdf2docx import Converter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
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

if __name__ == "__main__":
    app.run()
