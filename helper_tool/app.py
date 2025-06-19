from flask import Flask, jsonify, render_template, request, send_file

from services.pdf_text_extractor import extract_pdf_text_to_zipfile

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.route("/extract-text", methods=["GET", "POST"])
def extract_text():
    if request.method == "POST":
        if "pdf_file" not in request.files:
            return jsonify({"error": "No PDF file uploaded"}), 400
        pdf_file = request.files["pdf_file"]
        if pdf_file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        # Call the helper to process and get zip file path
        zip_path = extract_pdf_text_to_zipfile(pdf_file)
        # Return the zip file as a download
        return send_file(
            zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name="pages.zip",
        )
    # Render the extract_text.html template for GET
    return render_template("extract_text.html")


@app.route("/generate-audio", methods=["GET", "POST"])
def generate_audio():
    if request.method == "POST":
        # Placeholder for audio generation logic
        return jsonify({"message": "Audio generation endpoint"})
    # Render the generate_audio.html template for GET
    return render_template("generate_audio.html")


@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Forbidden", "message": str(e)}), 403


if __name__ == "__main__":
    app.run(debug=True)
