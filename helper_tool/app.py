import os
import tempfile
import threading
import uuid

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_file,
    send_from_directory,
)

from services.pdf_text_extractor import extract_pdf_text_to_zipfile

app = Flask(__name__, static_folder="static", template_folder="templates")


# In-memory progress store for audio generation
audio_progress_data = {}


def background_generate_audio(
    progress_id, text, model, voice, speed, instructions, is_file
):
    from services.generate_audio_service import (
        generate_openai_tts,
        generate_single_openai_tts,
    )

    try:
        if is_file:
            # For file: zip of chunks
            def progress_callback(current, total):
                audio_progress_data[progress_id] = {
                    "current": current,
                    "total": total,
                    "status": "processing",
                }

            zip_path = generate_openai_tts(
                text,
                model,
                voice,
                speed,
                instructions,
                progress_callback=progress_callback,
            )
            audio_progress_data[progress_id] = {
                "current": audio_progress_data[progress_id]["total"],
                "total": audio_progress_data[progress_id]["total"],
                "status": "done",
                "file_type": "zip",
                "file_path": zip_path,
            }
        else:
            # For text: single mp3
            def progress_callback(current, total):
                audio_progress_data[progress_id] = {
                    "current": current,
                    "total": total,
                    "status": "processing",
                }

            mp3_path = generate_single_openai_tts(
                text,
                model,
                voice,
                speed,
                instructions,
                progress_callback=progress_callback,
            )
            audio_progress_data[progress_id] = {
                "current": 1,
                "total": 1,
                "status": "done",
                "file_type": "mp3",
                "file_path": mp3_path,
            }
    except Exception as e:
        audio_progress_data[progress_id] = {"status": "error", "error": str(e)}


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
        text = request.form.get("input_text")
        model = request.form.get("model")
        voice = request.form.get("voice")
        speed = request.form.get("speed")
        instructions = request.form.get("instructions")
        file = request.files.get("text_file")

        progress_id = str(uuid.uuid4())
        audio_progress_data[progress_id] = {
            "current": 0,
            "total": 1,
            "status": "processing",
        }

        if file and file.filename != "":
            file_content = file.read().decode("utf-8")
            if not file_content.strip():
                return jsonify({"error": "Uploaded file is empty."}), 400
            thread = threading.Thread(
                target=background_generate_audio,
                args=(
                    progress_id,
                    file_content,
                    model,
                    voice,
                    speed,
                    instructions,
                    True,
                ),
            )
            thread.start()
            return jsonify({"progress_id": progress_id, "file_type": "zip"})
        elif text and text.strip():
            thread = threading.Thread(
                target=background_generate_audio,
                args=(progress_id, text, model, voice, speed, instructions, False),
            )
            thread.start()
            return jsonify({"progress_id": progress_id, "file_type": "mp3"})
        else:
            return jsonify({"error": "Please provide text or upload a file."}), 400
    return render_template("generate_audio.html")


@app.route("/generate-audio-progress/<progress_id>")
def generate_audio_progress(progress_id):
    data = audio_progress_data.get(progress_id)
    if not data:
        return jsonify({"error": "Invalid progress ID"}), 404
    return jsonify(data)


@app.route("/generate-audio-download/<progress_id>")
def generate_audio_download(progress_id):
    data = audio_progress_data.get(progress_id)
    if not data or data.get("status") != "done":
        return jsonify({"error": "Not ready"}), 400
    file_path = data.get("file_path")
    file_type = data.get("file_type")
    if file_type == "mp3":
        return send_file(
            file_path,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="speech.mp3",
        )
    elif file_type == "zip":
        return send_file(
            file_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name="audio_chunks.zip",
        )
    return jsonify({"error": "Unknown file type"}), 400


@app.route("/combine-texts", methods=["GET", "POST"])
def combine_texts():
    combined_text = ""
    download_ready = False
    download_id = None
    summary = []

    if request.method == "POST":
        # If user clicked "Download Updated Text File"
        if "download_updated" in request.form:
            combined_text = request.form.get("combined_text", "")
            temp = tempfile.NamedTemporaryFile(
                delete=False, suffix=".txt", mode="w", encoding="utf-8"
            )
            temp.write(combined_text)
            temp.close()
            download_id = os.path.basename(temp.name)
            download_ready = True
            return render_template(
                "combine_texts.html",
                combined_text=combined_text,
                download_ready=download_ready,
                download_id=download_id,
                error=None,
                summary=None,
            )
        # Otherwise, handle file upload
        files = request.files.getlist("text_files")
        if not files or not any(f.filename for f in files):
            return render_template(
                "combine_texts.html",
                combined_text="",
                download_ready=False,
                download_id=None,
                error="No files uploaded.",
                summary=None,
            )
        texts = []
        summary = []
        for file in files:
            if file and file.filename:
                content = file.read().decode("utf-8")
                texts.append(content)
                line_count = len(content.splitlines())
                summary.append((file.filename, line_count))
        combined_text = "\n\n".join(texts)
        return render_template(
            "combine_texts.html",
            combined_text=combined_text,
            download_ready=False,
            download_id=None,
            error=None,
            summary=summary,
        )
    return render_template(
        "combine_texts.html",
        combined_text="",
        download_ready=False,
        download_id=None,
        error=None,
        summary=None,
    )


@app.route("/download-combined/<download_id>")
def download_combined(download_id):
    temp_dir = tempfile.gettempdir()
    return send_from_directory(
        temp_dir, download_id, as_attachment=True, download_name="combined.txt"
    )


@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Forbidden", "message": str(e)}), 403


if __name__ == "__main__":
    app.run(debug=True)
