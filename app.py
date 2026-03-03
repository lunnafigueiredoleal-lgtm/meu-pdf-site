from flask import Flask, render_template_string, request, send_file, after_this_request
import os
import uuid
from PyPDF2 import PdfMerger

app = Flask(__name__)

# 🔥 Força o navegador a usar o favicon correto
@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')

# Criar pasta uploads se não existir
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Meu PDF Tool</title>
    <link rel="icon" href="/static/favicon.ico">

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6fb;
            text-align: center;
            padding: 40px;
        }

        .container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: auto;
        }

        h1 {
            margin-bottom: 20px;
        }

        input[type=file] {
            margin: 15px 0;
        }

        button {
            background: #4f46e5;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
        }

        button:hover {
            background: #4338ca;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Juntar PDFs</h1>

        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="pdfs" multiple required>
            <br>
            <button type="submit">Unir PDFs</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("pdfs")

        merger = PdfMerger()
        filenames = []

        for file in files:
            filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".pdf")
            file.save(filename)
            merger.append(filename)
            filenames.append(filename)

        output = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".pdf")
        merger.write(output)
        merger.close()

        @after_this_request
        def remove_files(response):
            try:
                os.remove(output)
                for f in filenames:
                    os.remove(f)
            except:
                pass
            return response

        return send_file(output, as_attachment=True)

    return render_template_string(HTML_TEMPLATE)


if __name__ == "__main__":
    app.run(debug=True)
