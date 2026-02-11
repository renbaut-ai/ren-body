#!/usr/bin/env python3
"""
Ren Voice Chat - Real-time voice conversation prototype
========================================================
Press SPACE to talk, release to send.
Or use --continuous for always-listening mode (with silence detection).

Requirements:
    pip install pyaudio numpy openai-whisper sounddevice

Usage:
    python voice_chat.py                    # Push-to-talk (SPACE)
    python voice_chat.py --continuous       # Always listening
    python voice_chat.py --wake-word "hey ren"  # Wake word activation
"""

import argparse
import subprocess
import tempfile
import os
import sys
import time
import wave
import threading
import queue
from pathlib import Path

# Optional imports with graceful fallback
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'

# Voice activity detection
SILENCE_THRESHOLD = 500  # Adjust based on mic sensitivity
SILENCE_DURATION = 1.5   # Seconds of silence to end recording

# Paths
WHISPER_CMD = "whisper"
SAG_CMD = "sag"
SAY_CMD = "say"  # Fallback to macOS say

# TTS voice (ElevenLabs)
TTS_VOICE = "Brian"  # Or use voice ID: nPczCjzI2devNBz1zQrb

class VoiceChat:
    def __init__(self, mode='ptt', wake_word=None, use_sag=True):
        self.mode = mode  # 'ptt' (push-to-talk), 'continuous', 'wake'
        self.wake_word = wake_word.lower() if wake_word else None
        self.use_sag = use_sag
        self.recording = False
        self.audio_queue = queue.Queue()
        self.running = True
        
        # Check dependencies
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Verify required tools are available."""
        missing = []
        
        if not HAS_NUMPY:
            missing.append("numpy (pip install numpy)")
        if not HAS_SOUNDDEVICE:
            missing.append("sounddevice (pip install sounddevice)")
        
        # Check whisper
        result = subprocess.run([WHISPER_CMD, "--help"], capture_output=True)
        if result.returncode != 0:
            missing.append("whisper (brew install openai-whisper)")
        
        if missing:
            print("❌ Missing dependencies:")
            for m in missing:
                print(f"   - {m}")
            sys.exit(1)
        
        # Check TTS
        if self.use_sag:
            result = subprocess.run([SAG_CMD, "--help"], capture_output=True)
            if result.returncode != 0:
                print("⚠️  sag not found, falling back to macOS say")
                self.use_sag = False
    
    def record_audio_ptt(self):
        """Record audio while key is held (push-to-talk)."""
        print("\n🎤 Recording... (release SPACE to stop)")
        
        frames = []
        
        def callback(indata, frame_count, time_info, status):
            if self.recording:
                frames.append(indata.copy())
        
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, 
                           dtype=DTYPE, callback=callback):
            self.recording = True
            # Wait for key release (simplified - needs proper key handling)
            while self.recording:
                time.sleep(0.05)
        
        if frames:
            audio_data = np.concatenate(frames, axis=0)
            return audio_data
        return None
    
    def record_audio_vad(self, max_duration=30):
        """Record audio with voice activity detection."""
        print("\n🎤 Listening... (speak now)")
        
        frames = []
        silent_frames = 0
        has_speech = False
        frames_per_second = SAMPLE_RATE // 1024
        silence_frames_threshold = int(SILENCE_DURATION * frames_per_second)
        
        def callback(indata, frame_count, time_info, status):
            nonlocal silent_frames, has_speech
            
            frames.append(indata.copy())
            
            # Simple VAD based on amplitude
            amplitude = np.abs(indata).mean()
            
            if amplitude > SILENCE_THRESHOLD:
                silent_frames = 0
                has_speech = True
            else:
                silent_frames += 1
        
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                           dtype=DTYPE, callback=callback, blocksize=1024):
            start_time = time.time()
            
            while self.running:
                time.sleep(0.05)
                
                # Stop conditions
                if has_speech and silent_frames > silence_frames_threshold:
                    print("   (silence detected)")
                    break
                if time.time() - start_time > max_duration:
                    print("   (max duration reached)")
                    break
        
        if frames and has_speech:
            audio_data = np.concatenate(frames, axis=0)
            return audio_data
        return None
    
    def save_audio(self, audio_data, filepath):
        """Save audio data to WAV file."""
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
    
    def transcribe(self, audio_path):
        """Transcribe audio using Whisper."""
        print("📝 Transcribing...")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run([
                WHISPER_CMD, audio_path,
                "--model", "base",  # Use 'small' or 'medium' for better accuracy
                "--output_format", "txt",
                "--output_dir", tmpdir,
                "--language", "en",
            ], capture_output=True, text=True)
            
            # Read transcription
            txt_file = Path(tmpdir) / (Path(audio_path).stem + ".txt")
            if txt_file.exists():
                text = txt_file.read_text().strip()
                return text
        
        return None
    
    def speak(self, text):
        """Convert text to speech and play."""
        if not text:
            return
        
        print(f"🔊 Speaking: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        if self.use_sag:
            # Use ElevenLabs via sag
            subprocess.run([
                SAG_CMD, 
                "-v", TTS_VOICE,
                text
            ], capture_output=True)
        else:
            # Fallback to macOS say
            subprocess.run([SAY_CMD, text], capture_output=True)
    
    def process_with_openclaw(self, text):
        """Send text to OpenClaw and get response."""
        print(f"💭 Thinking about: {text}")
        
        # For now, use a simple echo/response
        # In production, this would call the OpenClaw API
        # or use the sessions_send tool
        
        # Placeholder response
        response = f"I heard you say: {text}. This is a test response. In the full version, I'll actually think about what you said!"
        
        return response
    
    def run_ptt_mode(self):
        """Run in push-to-talk mode."""
        print("\n" + "="*50)
        print("REN VOICE CHAT - Push-to-Talk Mode")
        print("="*50)
        print("Press ENTER to start recording, ENTER again to stop.")
        print("Type 'quit' to exit.")
        print("="*50)
        
        while self.running:
            user_input = input("\n[Press ENTER to talk, 'quit' to exit]: ").strip()
            
            if user_input.lower() == 'quit':
                break
            
            # Record
            print("🎤 Recording... (press ENTER to stop)")
            
            frames = []
            recording = True
            
            def record_thread():
                nonlocal frames
                with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                                   dtype=DTYPE, blocksize=1024) as stream:
                    while recording:
                        data, _ = stream.read(1024)
                        frames.append(data)
            
            thread = threading.Thread(target=record_thread)
            thread.start()
            
            input()  # Wait for ENTER
            recording = False
            thread.join()
            
            if frames:
                audio_data = np.concatenate(frames, axis=0)
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    self.save_audio(audio_data, f.name)
                    audio_path = f.name
                
                # Transcribe
                text = self.transcribe(audio_path)
                os.unlink(audio_path)
                
                if text:
                    print(f"📝 You said: {text}")
                    
                    # Get response
                    response = self.process_with_openclaw(text)
                    
                    # Speak response
                    self.speak(response)
                else:
                    print("❌ Couldn't transcribe audio")
    
    def run_continuous_mode(self):
        """Run in continuous listening mode."""
        print("\n" + "="*50)
        print("REN VOICE CHAT - Continuous Mode")
        print("="*50)
        print("Listening continuously. Speak naturally.")
        print("Press Ctrl+C to exit.")
        print("="*50)
        
        while self.running:
            try:
                # Record with VAD
                audio_data = self.record_audio_vad()
                
                if audio_data is not None and len(audio_data) > SAMPLE_RATE:  # At least 1 second
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        self.save_audio(audio_data, f.name)
                        audio_path = f.name
                    
                    # Transcribe
                    text = self.transcribe(audio_path)
                    os.unlink(audio_path)
                    
                    if text and len(text.strip()) > 0:
                        print(f"\n📝 You said: {text}")
                        
                        # Check for wake word if enabled
                        if self.wake_word and self.wake_word not in text.lower():
                            print("   (wake word not detected, ignoring)")
                            continue
                        
                        # Get response
                        response = self.process_with_openclaw(text)
                        
                        # Speak response
                        self.speak(response)
                
                # Small delay before next listen
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                self.running = False
                break
    
    def run(self):
        """Run the voice chat in selected mode."""
        try:
            if self.mode == 'continuous' or self.mode == 'wake':
                self.run_continuous_mode()
            else:
                self.run_ptt_mode()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")


def main():
    parser = argparse.ArgumentParser(description="Ren Voice Chat")
    parser.add_argument('--continuous', '-c', action='store_true',
                       help="Continuous listening mode")
    parser.add_argument('--wake-word', '-w', type=str,
                       help="Wake word to activate (e.g., 'hey ren')")
    parser.add_argument('--no-sag', action='store_true',
                       help="Use macOS say instead of ElevenLabs")
    
    args = parser.parse_args()
    
    mode = 'continuous' if args.continuous else 'ptt'
    if args.wake_word:
        mode = 'wake'
    
    chat = VoiceChat(
        mode=mode,
        wake_word=args.wake_word,
        use_sag=not args.no_sag
    )
    
    chat.run()


if __name__ == "__main__":
    main()
