import os
import tempfile
import zipfile

import openai
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")


def split_text_by_tokens(text, max_tokens=1900, encoding_name="cl100k_base"):
    enc = tiktoken.get_encoding(encoding_name)
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        # Decode the chunk and try to split at the last period before the limit
        chunk_text = enc.decode(tokens[start:end])
        if end < len(tokens):
            last_period = chunk_text.rfind(".")
            if last_period != -1:
                chunk_text = chunk_text[: last_period + 1]
                end = start + len(enc.encode(chunk_text))
        chunks.append(chunk_text.strip())
        start = end
    return [c for c in chunks if c]


def generate_openai_tts(
    text, model, voice, speed, instructions, progress_callback=None
):
    """
    Calls OpenAI TTS API and returns the path to a zip file containing all mp3 chunks.
    Splits text into chunks of ≤1900 tokens, splitting at the last period.
    """
    chunks = split_text_by_tokens(text, max_tokens=1900)
    temp_dir = tempfile.TemporaryDirectory()
    mp3_paths = []
    total = len(chunks)
    for idx, chunk in enumerate(chunks, start=1):
        response = openai.audio.speech.create(
            model=model,
            voice=voice,
            input=chunk,
            speed=float(speed),
            response_format="mp3",
            instructions=instructions,
        )
        mp3_path = os.path.join(temp_dir.name, f"chunk_{idx}.mp3")
        with open(mp3_path, "wb") as f:
            f.write(response.content)
        mp3_paths.append(mp3_path)
        if progress_callback:
            progress_callback(idx, total)

    zip_path = os.path.join(temp_dir.name, "audio_chunks.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for mp3_path in mp3_paths:
            arcname = os.path.basename(mp3_path)
            zipf.write(mp3_path, arcname=arcname)
    # Keep temp_dir alive by attaching it to the zip_path
    # so the file is not deleted before Flask sends it
    zip_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with open(zip_path, "rb") as src, open(zip_file.name, "wb") as dst:
        dst.write(src.read())
    return zip_file.name


def generate_single_openai_tts(
    text, model, voice, speed, instructions, progress_callback=None
):
    """
    Generate a single mp3 file from the provided text using OpenAI TTS.
    """
    response = openai.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        speed=float(speed),
        response_format="mp3",
        instructions=instructions,
    )
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp.write(response.content)
    temp.close()
    if progress_callback:
        progress_callback(1, 1)
    return temp.name
