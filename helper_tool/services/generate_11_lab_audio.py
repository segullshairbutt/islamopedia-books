import os
import tempfile
import zipfile
import asyncio
import websockets
import json
import base64
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from dotenv import load_dotenv

# Load environment variables (safe to call multiple times)
load_dotenv()

# Initialize ElevenLabs client
client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)


def get_user_credits():
    """
    Get user's current credit information from ElevenLabs.
    
    Returns:
        dict: Dictionary containing credit information or error
    """
    try:
        # Get user subscription info which includes credits
        user_info = client.user.get()
        subscription = user_info.subscription
        
        # Extract credit information
        credits_info = {
            "character_count": subscription.character_count,
            "character_limit": subscription.character_limit,
            "characters_remaining": subscription.character_limit - subscription.character_count,
            "next_character_count_reset_unix": subscription.next_character_count_reset_unix,
            "tier": subscription.tier,
            "status": subscription.status
        }
        
        return {"success": True, "credits": credits_info}
    except Exception as e:
        print(f"Error fetching user credits: {e}")
        return {"success": False, "error": str(e)}


def get_available_voices():
    """
    Get list of available voices from ElevenLabs API.
    
    Returns:
        list: List of voice dictionaries with id, name, and category
    """
    try:
        voices_response = client.voices.get_all()
        voices_list = []
        
        for voice in voices_response.voices:
            voice_info = {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": getattr(voice, 'category', 'Unknown'),
                "description": getattr(voice, 'description', ''),
                "accent": getattr(voice, 'accent', ''),
                "age": getattr(voice, 'age', ''),
                "gender": getattr(voice, 'gender', ''),
                "use_case": getattr(voice, 'use_case', ''),
                "language": getattr(voice, 'language', ''),
                "preview_url": getattr(voice, 'preview_url', ''),
                "available_for_tiers": getattr(voice, 'available_for_tiers', []),
                "high_quality_base_model_ids": getattr(voice, 'high_quality_base_model_ids', [])
            }
            voices_list.append(voice_info)
        
        # Sort voices by category and then by name for better organization
        voices_list.sort(key=lambda x: (x['category'], x['name']))
        
        print(f"Successfully fetched {len(voices_list)} voices from ElevenLabs API")
        return voices_list
        
    except Exception as e:
        print(f"Error fetching voices from ElevenLabs API: {e}")
        return []


def get_available_models():
    """
    Get list of available models from ElevenLabs API.
    
    Returns:
        list: List of model dictionaries with id, name, and description
    """
    try:
        models_response = client.models.list()
        models_list = []
        
        for model in models_response:
            model_info = {
                "model_id": model.model_id,
                "name": model.name,
                "description": getattr(model, 'description', ''),
                "can_be_finetuned": getattr(model, 'can_be_finetuned', False),
                "can_do_text_to_speech": getattr(model, 'can_do_text_to_speech', True),
                "can_do_voice_conversion": getattr(model, 'can_do_voice_conversion', False),
                "can_use_speaker_boost": getattr(model, 'can_use_speaker_boost', False),
                "can_use_style": getattr(model, 'can_use_style', False),
                "serves_pro_voices": getattr(model, 'serves_pro_voices', False),
                "token_cost_factor": getattr(model, 'token_cost_factor', 1.0),
                "requires_alpha_access": getattr(model, 'requires_alpha_access', False),
                "max_characters_request_free_user": getattr(model, 'max_characters_request_free_user', 0),
                "max_characters_request_subscribed_user": getattr(model, 'max_characters_request_subscribed_user', 0),
                "maximum_text_length_per_request": getattr(model, 'maximum_text_length_per_request', 0),
                "languages": getattr(model, 'languages', [])
            }
            
            # Only include models that can do text-to-speech
            if model_info["can_do_text_to_speech"]:
                models_list.append(model_info)
        
        # Sort models by preference: v3 first, then v2, then others
        def model_sort_key(model):
            model_id = model["model_id"]
            if "v3" in model_id:
                return (0, model_id)  # v3 models first
            elif "v2" in model_id:
                return (1, model_id)  # v2 models second
            else:
                return (2, model_id)  # other models last
        
        models_list.sort(key=model_sort_key)
        
        print(f"Successfully fetched {len(models_list)} TTS models from ElevenLabs API")
        for model in models_list:
            print(f"  - {model['model_id']}: {model['name']}")
        
        return models_list
        
    except Exception as e:
        print(f"Error fetching models from ElevenLabs API: {e}")
        return []


def split_text_into_chunks(text, max_chars=5000):
    """
    Split text into chunks for ElevenLabs API.
    ElevenLabs has a character limit per request.
    
    Args:
        text (str): Text to split
        max_chars (int): Maximum characters per chunk
        
    Returns:
        list: List of text chunks
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk_text = text[start:end]
        
        # Try to split at the last sentence ending
        if end < len(text):
            # Look for sentence endings (., !, ?, or Urdu/Arabic full stop ۔)
            last_period = max(
                chunk_text.rfind('.'),
                chunk_text.rfind('!'),
                chunk_text.rfind('?'),
                chunk_text.rfind('۔')
            )
            
            if last_period != -1 and last_period > start + max_chars * 0.5:
                chunk_text = chunk_text[:last_period + 1]
                end = start + len(chunk_text)
        
        chunks.append(chunk_text.strip())
        start = end
    
    return [c for c in chunks if c.strip()]


def get_best_model_for_multilingual():
    """
    Get the best available model for multilingual TTS, preferring v3 if available.
    
    Returns:
        str: Model ID of the best available model
    """
    try:
        models = get_available_models()
        
        # Prefer v3 models first
        for model in models:
            if "v3" in model["model_id"] and "multilingual" in model["model_id"]:
                print(f"Using best model: {model['model_id']} ({model['name']})")
                return model["model_id"]
        
        # Fall back to v2 multilingual
        for model in models:
            if "v2" in model["model_id"] and "multilingual" in model["model_id"]:
                print(f"Using fallback model: {model['model_id']} ({model['name']})")
                return model["model_id"]
        
        # If no multilingual models, use the first available TTS model
        if models:
            best_model = models[0]["model_id"]
            print(f"Using first available model: {best_model}")
            return best_model
        
        # Ultimate fallback
        print("No models available from API, using hardcoded fallback")
        return "eleven_multilingual_v2"
        
    except Exception as e:
        print(f"Error determining best model: {e}")
        return "eleven_multilingual_v2"


async def generate_elevenlabs_audio_websocket(text, voice_id, model=None, stability=0.5, similarity_boost=0.8, progress_callback=None):
    """
    Generate audio using ElevenLabs WebSocket streaming for real-time progress.
    
    Args:
        text (str): Text to convert to speech
        voice_id (str): ElevenLabs voice ID
        model (str): Model to use for generation (None = auto-select best)
        stability (float): Voice stability (0.0 to 1.0)
        similarity_boost (float): Voice similarity boost (0.0 to 1.0)
        progress_callback (function): Optional callback for progress updates
        
    Returns:
        str: Path to generated audio file
    """
    # Auto-select best model if not specified
    if model is None:
        model = get_best_model_for_multilingual()
    
    try:
        # WebSocket URL for ElevenLabs
        ws_url = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model}"
        
        # Headers for WebSocket connection
        headers = {
            "xi-api-key": os.getenv("ELEVENLABS_API_KEY")
        }
        
        # Create temporary file for audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        audio_chunks = []
        
        async with websockets.connect(ws_url, extra_headers=headers) as websocket:
            # Send initial configuration
            config_message = {
                "text": " ",  # Start with space to initialize
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost
                },
                "generation_config": {
                    "chunk_length_schedule": [120, 160, 250, 290]
                }
            }
            await websocket.send(json.dumps(config_message))
            
            # Send the actual text
            text_message = {
                "text": text,
                "try_trigger_generation": True
            }
            await websocket.send(json.dumps(text_message))
            
            # Send end of stream marker
            end_message = {"text": ""}
            await websocket.send(json.dumps(end_message))
            
            # Receive audio chunks
            received_chunks = 0
            
            async for message in websocket:
                data = json.loads(message)
                
                if "audio" in data:
                    # Decode base64 audio data
                    audio_chunk = base64.b64decode(data["audio"])
                    audio_chunks.append(audio_chunk)
                    received_chunks += 1
                    
                    if progress_callback:
                        # Estimate progress (since we don't know total chunks beforehand)
                        progress_callback(received_chunks, max(received_chunks + 1, 10))
                
                elif "isFinal" in data and data["isFinal"]:
                    break
                    
                elif "error" in data:
                    raise Exception(f"WebSocket error: {data['error']}")
        
        # Write all audio chunks to file
        for chunk in audio_chunks:
            temp_file.write(chunk)
        
        temp_file.close()
        
        if progress_callback:
            progress_callback(received_chunks, received_chunks)  # Mark as complete
        
        print(f"[ElevenLabs WebSocket] Audio generated: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        if 'temp_file' in locals():
            temp_file.close()
        raise Exception(f"ElevenLabs WebSocket generation failed: {str(e)}")


def generate_elevenlabs_audio_single(text, voice_id, model=None, stability=0.5, similarity_boost=0.8):
    """
    Generate a single audio file using ElevenLabs TTS with WebSocket streaming.
    
    Args:
        text (str): Text to convert to speech
        voice_id (str): ElevenLabs voice ID
        model (str): Model to use for generation (None = auto-select best)
        stability (float): Voice stability (0.0 to 1.0)
        similarity_boost (float): Voice similarity boost (0.0 to 1.0)
        
    Returns:
        str: Path to generated audio file
    """
    # Auto-select best model if not specified
    if model is None:
        model = get_best_model_for_multilingual()
    
    try:
        # Try WebSocket first, fall back to REST API if needed
        try:
            return asyncio.run(generate_elevenlabs_audio_websocket(
                text, voice_id, model, stability, similarity_boost
            ))
        except Exception as ws_error:
            print(f"WebSocket failed, falling back to REST API: {ws_error}")
            
            # If using v3 model and it fails, try v2 as fallback
            if "v3" in model:
                try:
                    print(f"{model} failed, trying v2 model as fallback...")
                    fallback_model = get_best_model_for_multilingual()
                    if "v2" in fallback_model:
                        audio = client.text_to_speech.convert(
                            voice_id=voice_id,
                            text=text,
                            model_id=fallback_model,
                            voice_settings=VoiceSettings(
                                stability=stability,
                                similarity_boost=similarity_boost
                            )
                        )
                    else:
                        # If no v2 model available, use the original model
                        audio = client.text_to_speech.convert(
                            voice_id=voice_id,
                            text=text,
                            model_id=model,
                            voice_settings=VoiceSettings(
                                stability=stability,
                                similarity_boost=similarity_boost
                            )
                        )
                except Exception:
                    # If v2 also fails, use the original model
                    audio = client.text_to_speech.convert(
                        voice_id=voice_id,
                        text=text,
                        model_id=model,
                        voice_settings=VoiceSettings(
                            stability=stability,
                            similarity_boost=similarity_boost
                        )
                    )
            else:
                # Fallback to REST API with original model
                audio = client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=text,
                    model_id=model,
                    voice_settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity_boost
                    )
                )
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            
            # ElevenLabs returns an iterator of audio chunks
            for chunk in audio:
                temp_file.write(chunk)
            
            temp_file.close()
            return temp_file.name
        
    except Exception as e:
        raise Exception(f"ElevenLabs generation failed: {str(e)}")


async def generate_elevenlabs_audio_chunks_websocket(text, voice_id, model=None, stability=0.5, similarity_boost=0.8, progress_callback=None):
    """
    Generate audio from text chunks using WebSocket streaming.
    
    Args:
        text (str): Text to convert to speech
        voice_id (str): ElevenLabs voice ID
        model (str): Model to use for generation (None = auto-select best)
        stability (float): Voice stability (0.0 to 1.0)
        similarity_boost (float): Voice similarity boost (0.0 to 1.0)
        progress_callback (function): Optional callback for progress updates
        
    Returns:
        tuple: (zip_path, permanent_chunk_paths)
    """
    # Auto-select best model if not specified
    if model is None:
        model = get_best_model_for_multilingual()
    chunks = split_text_into_chunks(text, max_chars=5000)
    total = len(chunks)
    print(f"[ElevenLabs WebSocket] Total chunks to generate: {total}")
    
    temp_dir = tempfile.TemporaryDirectory()
    audio_paths = []
    permanent_chunk_paths = []
    
    try:
        for idx, chunk in enumerate(chunks, start=1):
            print(f"[ElevenLabs WebSocket] Generating chunk {idx}/{total}...")
            
            # Generate audio for this chunk using WebSocket
            audio_path = await generate_elevenlabs_audio_websocket(
                chunk, voice_id, model, stability, similarity_boost
            )
            
            # Move to temp directory with proper naming
            chunk_path = os.path.join(temp_dir.name, f"chunk_{idx}.mp3")
            os.rename(audio_path, chunk_path)
            audio_paths.append(chunk_path)
            
            # Create permanent copy of chunk for individual access
            permanent_chunk = tempfile.NamedTemporaryFile(delete=False, suffix=f"_chunk_{idx}.mp3")
            with open(chunk_path, "rb") as src, open(permanent_chunk.name, "wb") as dst:
                dst.write(src.read())
            permanent_chunk_paths.append(permanent_chunk.name)
            
            print(f"[ElevenLabs WebSocket] Completed chunk {idx}/{total}: {chunk_path}")
            
            if progress_callback:
                progress_callback(idx, total, permanent_chunk_paths)
        
        # Create zip file
        zip_path = os.path.join(temp_dir.name, "elevenlabs_audio_chunks.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for audio_path in audio_paths:
                arcname = os.path.basename(audio_path)
                zipf.write(audio_path, arcname=arcname)
        
        # Move zip to permanent temp file
        zip_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        with open(zip_path, "rb") as src, open(zip_file.name, "wb") as dst:
            dst.write(src.read())
        
        print(f"[ElevenLabs WebSocket] All chunks completed. Zip created at: {zip_file.name}")
        return zip_file.name, permanent_chunk_paths
        
    except Exception as e:
        raise Exception(f"ElevenLabs WebSocket chunk generation failed: {str(e)}")


def generate_elevenlabs_audio_chunks(text, voice_id, model=None, stability=0.5, similarity_boost=0.8, progress_callback=None):
    """
    Generate audio from text by splitting into chunks and creating a zip file using WebSocket.
    
    Args:
        text (str): Text to convert to speech
        voice_id (str): ElevenLabs voice ID
        model (str): Model to use for generation (None = auto-select best)
        stability (float): Voice stability (0.0 to 1.0)
        similarity_boost (float): Voice similarity boost (0.0 to 1.0)
        progress_callback (function): Optional callback for progress updates
        
    Returns:
        str: Path to zip file containing all audio chunks
    """
    # Auto-select best model if not specified
    if model is None:
        model = get_best_model_for_multilingual()
    
    try:
        # Try WebSocket chunks first
        return asyncio.run(generate_elevenlabs_audio_chunks_websocket(
            text, voice_id, model, stability, similarity_boost, progress_callback
        ))
    except Exception as ws_error:
        print(f"WebSocket chunks failed, falling back to REST API: {ws_error}")
        
        # Fallback to REST API chunks
        chunks = split_text_into_chunks(text, max_chars=5000)
        total = len(chunks)
        print(f"[ElevenLabs REST] Total chunks to generate: {total}")
        
        temp_dir = tempfile.TemporaryDirectory()
        audio_paths = []
        permanent_chunk_paths = []
        
        try:
            for idx, chunk in enumerate(chunks, start=1):
                print(f"[ElevenLabs REST] Generating chunk {idx}/{total}...")
                
                audio = client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=chunk,
                    model_id=model,
                    voice_settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity_boost
                    )
                )
                
                audio_path = os.path.join(temp_dir.name, f"chunk_{idx}.mp3")
                
                with open(audio_path, "wb") as f:
                    for audio_chunk in audio:
                        f.write(audio_chunk)
                
                audio_paths.append(audio_path)
                
                # Create permanent copy of chunk for individual access
                permanent_chunk = tempfile.NamedTemporaryFile(delete=False, suffix=f"_chunk_{idx}.mp3")
                with open(audio_path, "rb") as src, open(permanent_chunk.name, "wb") as dst:
                    dst.write(src.read())
                permanent_chunk_paths.append(permanent_chunk.name)
                
                print(f"[ElevenLabs REST] Completed chunk {idx}/{total}: {audio_path}")
                
                if progress_callback:
                    progress_callback(idx, total, permanent_chunk_paths)
            
            # Create zip file
            zip_path = os.path.join(temp_dir.name, "elevenlabs_audio_chunks.zip")
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for audio_path in audio_paths:
                    arcname = os.path.basename(audio_path)
                    zipf.write(audio_path, arcname=arcname)
            
            # Move zip to permanent temp file
            zip_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
            with open(zip_path, "rb") as src, open(zip_file.name, "wb") as dst:
                dst.write(src.read())
            
            print(f"[ElevenLabs REST] All chunks completed. Zip created at: {zip_file.name}")
            return zip_file.name, permanent_chunk_paths
            
        except Exception as e:
            raise Exception(f"ElevenLabs REST chunk generation failed: {str(e)}")


def background_generate_elevenlabs_audio(
    progress_id, text, voice_id, model, stability, similarity_boost, is_file, audio_progress_data
):
    """
    Background function to generate ElevenLabs audio with WebSocket progress tracking.
    
    Args:
        progress_id: Unique identifier for tracking progress
        text: Text content to convert to audio
        voice_id: ElevenLabs voice ID
        model: ElevenLabs model to use
        stability: Voice stability setting
        similarity_boost: Voice similarity boost setting
        is_file: Boolean indicating if text comes from a file (affects output format)
        audio_progress_data: Shared dictionary for storing progress data
    """
    try:
        if is_file:
            # For file: zip of chunks with WebSocket
            def progress_callback(current, total, chunk_paths=None):
                audio_progress_data[progress_id] = {
                    "current": current,
                    "total": total,
                    "status": "processing",
                    "chunks": [{"index": i+1, "path": path} for i, path in enumerate(chunk_paths)] if chunk_paths else []
                }

            result = generate_elevenlabs_audio_chunks(
                text,
                voice_id,
                model,
                stability,
                similarity_boost,
                progress_callback=progress_callback,
            )
            
            # Handle both tuple (zip_path, chunk_paths) and single zip_path returns
            if isinstance(result, tuple):
                zip_path, chunk_paths = result
            else:
                zip_path = result
                chunk_paths = []
            
            audio_progress_data[progress_id] = {
                "current": len(chunk_paths) if chunk_paths else 1,
                "total": len(chunk_paths) if chunk_paths else 1,
                "status": "done",
                "file_type": "zip",
                "file_path": zip_path,
                "chunks": [{"index": i+1, "path": path} for i, path in enumerate(chunk_paths)] if chunk_paths else []
            }
        else:
            # For text: single mp3 with WebSocket
            audio_progress_data[progress_id] = {
                "current": 0,
                "total": 1,
                "status": "processing",
            }

            mp3_path = generate_elevenlabs_audio_single(
                text,
                voice_id,
                model,
                stability,
                similarity_boost
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
