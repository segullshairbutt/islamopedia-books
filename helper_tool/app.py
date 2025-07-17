import os
import tempfile
import threading
import uuid

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_file,
    send_from_directory,
)

# Load environment variables from .env file
load_dotenv()

from services.pdf_text_extractor import extract_pdf_text_to_zipfile
from services.generate_audio_service import background_generate_audio
from services.generate_11_lab_audio import background_generate_elevenlabs_audio, get_available_voices, get_available_models, get_user_credits

app = Flask(__name__, static_folder="static", template_folder="templates")


# In-memory progress store for audio generation
audio_progress_data = {}


@app.route("/")
def index():
    return render_template("index.html")


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
                    audio_progress_data,
                ),
            )
            thread.start()
            return jsonify({"progress_id": progress_id, "file_type": "zip"})
        elif text and text.strip():
            thread = threading.Thread(
                target=background_generate_audio,
                args=(progress_id, text, model, voice, speed, instructions, False, audio_progress_data),
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


@app.route("/generate-audio-play/<progress_id>")
def generate_audio_play(progress_id):
    """Serve OpenAI audio file for inline playback"""
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
        )
    return jsonify({"error": "Only MP3 files can be played inline"}), 400


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


@app.route("/generate-11-labs-audio", methods=["GET", "POST"])
def generate_elevenlabs_audio():
    if request.method == "POST":
        text = request.form.get("input_text")
        voice_id = request.form.get("voice_id")
        model = request.form.get("model")
        # If no model specified, let the service auto-select the best one
        if not model:
            model = None
        stability = float(request.form.get("stability", 0.5))
        similarity_boost = float(request.form.get("similarity_boost", 0.8))
        file = request.files.get("text_file")

        if not voice_id:
            return jsonify({"error": "Please select a voice."}), 400

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
                target=background_generate_elevenlabs_audio,
                args=(
                    progress_id,
                    file_content,
                    voice_id,
                    model,
                    stability,
                    similarity_boost,
                    True,
                    audio_progress_data,
                ),
            )
            thread.start()
            return jsonify({"progress_id": progress_id, "file_type": "zip"})
        elif text and text.strip():
            thread = threading.Thread(
                target=background_generate_elevenlabs_audio,
                args=(progress_id, text, voice_id, model, stability, similarity_boost, False, audio_progress_data),
            )
            thread.start()
            return jsonify({"progress_id": progress_id, "file_type": "mp3"})
        else:
            return jsonify({"error": "Please provide text or upload a file."}), 400
    
    # For GET request, fetch available voices, models, and credits, then render template
    voices = get_available_voices()
    models = get_available_models()
    credits_info = get_user_credits()
    return render_template("generate_elevenlabs_audio.html", voices=voices, models=models, credits_info=credits_info)


@app.route("/generate-11-labs-audio-credits")
def get_elevenlabs_credits():
    """Get current ElevenLabs credits via AJAX"""
    credits_info = get_user_credits()
    return jsonify(credits_info)


@app.route("/generate-11-labs-audio-progress/<progress_id>")
def generate_elevenlabs_audio_progress(progress_id):
    data = audio_progress_data.get(progress_id)
    if not data:
        return jsonify({"error": "Invalid progress ID"}), 404
    return jsonify(data)


@app.route("/generate-11-labs-audio-download/<progress_id>")
def generate_elevenlabs_audio_download(progress_id):
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
            download_name="elevenlabs_speech.mp3",
        )
    elif file_type == "zip":
        return send_file(
            file_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name="elevenlabs_audio_chunks.zip",
        )
    return jsonify({"error": "Unknown file type"}), 400


@app.route("/generate-11-labs-audio-play/<progress_id>")
def generate_elevenlabs_audio_play(progress_id):
    """Serve audio file for inline playback"""
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
        )
    return jsonify({"error": "Only MP3 files can be played inline"}), 400


@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Forbidden", "message": str(e)}), 403


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=5001, debug=debug_mode)
