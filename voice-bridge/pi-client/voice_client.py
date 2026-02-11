#!/usr/bin/env python3
"""
Voice Bridge Client - Raspberry Pi Zero with Codec Zero
Push-to-talk voice interface to Ren on Mac Mini.

Hardware:
- Raspberry Pi Zero (W/2W)
- Codec Zero I2S Audio HAT
- Wired earbuds with mic
- Push-to-talk button on GPIO

Wiring:
- PTT Button: GPIO17 to GND (internal pull-up, active low)
- LED (optional): GPIO27 for status indication
"""

import os
import sys
import time
import wave
import struct
import tempfile
import requests
from pathlib import Path

# Configuration
SERVER_URL = os.environ.get("VOICE_SERVER", "http://macmini.local:5555")
SAMPLE_RATE = 16000  # 16kHz for Whisper
CHANNELS = 1  # Mono
SAMPLE_WIDTH = 2  # 16-bit
PTT_GPIO = 17  # Push-to-talk button
LED_GPIO = 27  # Status LED (optional)
AUDIO_DEVICE = "default"  # ALSA device

# Check if we're on a Pi with GPIO
try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False
    print("Warning: RPi.GPIO not available, using keyboard input")

# Check for pyaudio
try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False
    print("Warning: pyaudio not available, using arecord/aplay")

class VoiceClient:
    def __init__(self, server_url=SERVER_URL):
        self.server_url = server_url
        self.recording = False
        self.audio_buffer = []
        
        if HAS_GPIO:
            self._setup_gpio()
        
        if HAS_PYAUDIO:
            self.audio = pyaudio.PyAudio()
    
    def _setup_gpio(self):
        """Setup GPIO for PTT button and LED"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PTT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(LED_GPIO, GPIO.OUT)
        GPIO.output(LED_GPIO, GPIO.LOW)
        
        # Add edge detection for button
        GPIO.add_event_detect(
            PTT_GPIO, 
            GPIO.BOTH, 
            callback=self._button_callback,
            bouncetime=50
        )
    
    def _button_callback(self, channel):
        """Handle PTT button press/release"""
        if GPIO.input(PTT_GPIO) == GPIO.LOW:
            # Button pressed
            self._start_recording()
        else:
            # Button released
            self._stop_recording()
    
    def _led_on(self):
        if HAS_GPIO:
            GPIO.output(LED_GPIO, GPIO.HIGH)
    
    def _led_off(self):
        if HAS_GPIO:
            GPIO.output(LED_GPIO, GPIO.LOW)
    
    def _start_recording(self):
        """Start recording audio"""
        if self.recording:
            return
        
        print("🎤 Recording...")
        self._led_on()
        self.recording = True
        self.audio_buffer = []
        
        if HAS_PYAUDIO:
            self._record_pyaudio()
    
    def _stop_recording(self):
        """Stop recording and process"""
        if not self.recording:
            return
        
        print("⏹️ Processing...")
        self.recording = False
        self._led_off()
    
    def _record_pyaudio(self):
        """Record using PyAudio (runs in thread)"""
        import threading
        
        def record_thread():
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=1024
            )
            
            while self.recording:
                data = stream.read(1024, exception_on_overflow=False)
                self.audio_buffer.append(data)
            
            stream.stop_stream()
            stream.close()
        
        thread = threading.Thread(target=record_thread)
        thread.start()
    
    def record_with_arecord(self, duration=None):
        """Record using arecord (ALSA) - blocking"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        
        cmd = [
            "arecord",
            "-D", AUDIO_DEVICE,
            "-f", "S16_LE",
            "-r", str(SAMPLE_RATE),
            "-c", str(CHANNELS),
            "-t", "wav",
        ]
        
        if duration:
            cmd.extend(["-d", str(duration)])
        
        cmd.append(temp_path)
        
        import subprocess
        subprocess.run(cmd, check=True)
        
        return temp_path
    
    def play_audio(self, audio_path):
        """Play audio file through earbuds"""
        if HAS_PYAUDIO:
            self._play_pyaudio(audio_path)
        else:
            self._play_aplay(audio_path)
    
    def _play_pyaudio(self, audio_path):
        """Play using PyAudio"""
        wf = wave.open(audio_path, 'rb')
        
        stream = self.audio.open(
            format=self.audio.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        
        chunk = 1024
        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)
        
        stream.stop_stream()
        stream.close()
        wf.close()
    
    def _play_aplay(self, audio_path):
        """Play using aplay (ALSA)"""
        import subprocess
        subprocess.run(["aplay", "-D", AUDIO_DEVICE, audio_path], check=True)
    
    def save_buffer_to_wav(self):
        """Save recorded buffer to WAV file"""
        if not self.audio_buffer:
            return None
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        
        with wave.open(temp_path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(self.audio_buffer))
        
        return temp_path
    
    def send_to_server(self, audio_path):
        """Send audio to server, get response audio"""
        print(f"📤 Sending to {self.server_url}...")
        
        try:
            with open(audio_path, 'rb') as f:
                response = requests.post(
                    f"{self.server_url}/voice",
                    files={"audio": ("recording.wav", f, "audio/wav")},
                    timeout=30
                )
            
            if response.status_code == 200:
                # Save response audio
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(response.content)
                    return f.name
            else:
                print(f"Server error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
    
    def voice_interaction(self, audio_path):
        """Full voice interaction cycle"""
        response_audio = self.send_to_server(audio_path)
        
        if response_audio:
            print("🔊 Playing response...")
            self.play_audio(response_audio)
            os.unlink(response_audio)
        else:
            print("❌ No response received")
    
    def run_ptt_loop(self):
        """Main PTT loop - GPIO button based"""
        print(f"🎙️ Voice Client Ready")
        print(f"   Server: {self.server_url}")
        print(f"   Press PTT button (GPIO{PTT_GPIO}) to talk")
        print(f"   Ctrl+C to exit")
        
        try:
            while True:
                # Wait for button release after recording
                if not self.recording and self.audio_buffer:
                    audio_path = self.save_buffer_to_wav()
                    if audio_path:
                        self.voice_interaction(audio_path)
                        os.unlink(audio_path)
                    self.audio_buffer = []
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            if HAS_GPIO:
                GPIO.cleanup()
            if HAS_PYAUDIO:
                self.audio.terminate()
    
    def run_keyboard_loop(self):
        """Fallback loop using Enter key as PTT"""
        print(f"🎙️ Voice Client Ready (Keyboard Mode)")
        print(f"   Server: {self.server_url}")
        print(f"   Press Enter to start recording, Enter again to stop")
        print(f"   Type 'quit' to exit")
        
        try:
            while True:
                input("Press Enter to record...")
                
                # Record for up to 10 seconds or until Enter
                print("🎤 Recording... (press Enter to stop)")
                audio_path = self.record_with_arecord(duration=10)
                
                if audio_path and os.path.exists(audio_path):
                    self.voice_interaction(audio_path)
                    os.unlink(audio_path)
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    
    def run(self):
        """Start the voice client"""
        # Check server health
        try:
            resp = requests.get(f"{self.server_url}/health", timeout=5)
            if resp.status_code == 200:
                print(f"✅ Server connected: {resp.json()}")
            else:
                print(f"⚠️ Server returned: {resp.status_code}")
        except:
            print(f"⚠️ Could not reach server at {self.server_url}")
        
        if HAS_GPIO:
            self.run_ptt_loop()
        else:
            self.run_keyboard_loop()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ren Voice Client")
    parser.add_argument("--server", default=SERVER_URL, help="Voice server URL")
    parser.add_argument("--test", action="store_true", help="Test mode: record and play locally")
    args = parser.parse_args()
    
    if args.test:
        # Test mode: just record and play back
        print("Test mode: Recording for 3 seconds...")
        client = VoiceClient(args.server)
        audio_path = client.record_with_arecord(duration=3)
        print(f"Recorded to {audio_path}")
        print("Playing back...")
        client.play_audio(audio_path)
        os.unlink(audio_path)
        print("Done!")
    else:
        client = VoiceClient(args.server)
        client.run()

if __name__ == "__main__":
    main()
