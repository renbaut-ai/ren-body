#!/usr/bin/env python3
"""
Voice Bridge Server - Mac Mini
Receives audio from Pi, transcribes, sends to OpenClaw, returns TTS response.
Optimized for low latency.
"""

import os
import io
import time
import tempfile
import subprocess
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn

app = FastAPI(title="Ren Voice Bridge")

# Configuration
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")  # tiny, base, small
OPENCLAW_API = os.environ.get("OPENCLAW_API", "http://localhost:5001")
TTS_VOICE = os.environ.get("TTS_VOICE", "alloy")  # OpenAI TTS voice

# Pre-warm whisper on startup
whisper_model = None

def get_whisper():
    """Lazy-load whisper model"""
    global whisper_model
    if whisper_model is None:
        import whisper
        print(f"Loading Whisper model: {WHISPER_MODEL}")
        whisper_model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded!")
    return whisper_model

@app.on_event("startup")
async def startup():
    """Pre-warm the whisper model"""
    print("Pre-warming Whisper model...")
    get_whisper()
    print("Server ready!")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "model": WHISPER_MODEL}

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """
    Transcribe audio to text using Whisper.
    Accepts WAV, returns text.
    """
    start = time.time()
    
    # Save to temp file (whisper needs file path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        content = await audio.read()
        f.write(content)
        temp_path = f.name
    
    try:
        model = get_whisper()
        result = model.transcribe(temp_path, language="en", fp16=False)
        text = result["text"].strip()
        
        elapsed = time.time() - start
        print(f"Transcribed in {elapsed:.2f}s: {text[:50]}...")
        
        return {"text": text, "time": elapsed}
    finally:
        os.unlink(temp_path)

@app.post("/voice")
async def voice_pipeline(audio: UploadFile = File(...)):
    """
    Full voice pipeline:
    1. Transcribe audio
    2. Send to OpenClaw
    3. Get response
    4. TTS response
    5. Return audio
    """
    total_start = time.time()
    timings = {}
    
    # Step 1: Transcribe
    t0 = time.time()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        content = await audio.read()
        f.write(content)
        temp_path = f.name
    
    try:
        model = get_whisper()
        result = model.transcribe(temp_path, language="en", fp16=False)
        user_text = result["text"].strip()
        timings["transcribe"] = time.time() - t0
        print(f"[{timings['transcribe']:.2f}s] User: {user_text}")
        
        if not user_text:
            return JSONResponse({"error": "No speech detected"}, status_code=400)
        
        # Step 2: Send to OpenClaw and get response
        t0 = time.time()
        response_text = await query_openclaw(user_text)
        timings["openclaw"] = time.time() - t0
        print(f"[{timings['openclaw']:.2f}s] Ren: {response_text[:50]}...")
        
        # Step 3: TTS
        t0 = time.time()
        audio_bytes = await text_to_speech(response_text)
        timings["tts"] = time.time() - t0
        print(f"[{timings['tts']:.2f}s] TTS complete")
        
        timings["total"] = time.time() - total_start
        print(f"[{timings['total']:.2f}s] Total pipeline time")
        
        # Return audio with timing headers
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "X-Transcription": user_text[:100],
                "X-Response": response_text[:100],
                "X-Time-Total": str(timings["total"]),
            }
        )
    finally:
        os.unlink(temp_path)

async def query_openclaw(text: str) -> str:
    """Send text to OpenClaw and get response"""
    import aiohttp
    
    # Try the OpenClaw gateway API
    # This sends a message to the main session and gets a response
    async with aiohttp.ClientSession() as session:
        try:
            # Use the wake endpoint to send a message
            async with session.post(
                f"{OPENCLAW_API}/api/chat",
                json={"message": text},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "I couldn't process that.")
                else:
                    print(f"OpenClaw API error: {resp.status}")
                    return "Sorry, I had trouble processing that."
        except Exception as e:
            print(f"OpenClaw API error: {e}")
            # Fallback: try direct CLI
            return await query_openclaw_cli(text)

async def query_openclaw_cli(text: str) -> str:
    """Fallback: query OpenClaw via CLI"""
    try:
        result = subprocess.run(
            ["openclaw", "chat", "--message", text],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "Sorry, I couldn't process that request."
    except Exception as e:
        print(f"CLI fallback error: {e}")
        return "Sorry, something went wrong."

async def text_to_speech(text: str) -> bytes:
    """Convert text to speech, return WAV bytes"""
    # Try OpenAI TTS first
    try:
        return await tts_openai(text)
    except Exception as e:
        print(f"OpenAI TTS failed: {e}, trying local")
        return await tts_local(text)

async def tts_openai(text: str) -> bytes:
    """Use OpenAI TTS API"""
    from openai import OpenAI
    client = OpenAI()
    
    response = client.audio.speech.create(
        model="tts-1",  # or tts-1-hd for higher quality
        voice=TTS_VOICE,
        input=text,
        response_format="wav"
    )
    
    return response.content

async def tts_local(text: str) -> bytes:
    """Fallback to local TTS (say command on macOS)"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name
    
    try:
        # Use macOS say command with AIFF output, convert to WAV
        aiff_path = temp_path.replace(".wav", ".aiff")
        subprocess.run(
            ["say", "-o", aiff_path, text],
            check=True,
            timeout=10
        )
        # Convert to WAV with sox
        subprocess.run(
            ["sox", aiff_path, temp_path],
            check=True,
            timeout=10
        )
        os.unlink(aiff_path)
        
        with open(temp_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@app.post("/tts")
async def tts_endpoint(text: str):
    """Standalone TTS endpoint"""
    audio_bytes = await text_to_speech(text)
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/wav"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5555)
