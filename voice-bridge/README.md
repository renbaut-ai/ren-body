# Ren Voice Bridge

Real-time voice communication between a Raspberry Pi (with earbuds) and Ren on the Mac Mini.

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐
│   Raspberry Pi      │         │     Mac Mini        │
│   (Codec Zero)      │         │                     │
├─────────────────────┤         ├─────────────────────┤
│ • Wired earbuds     │  HTTP   │ • Voice Server      │
│ • PTT button        │ ◄─────► │ • Whisper (STT)     │
│ • Record/Playback   │  :5555  │ • OpenClaw (Ren)    │
│                     │         │ • OpenAI TTS        │
└─────────────────────┘         └─────────────────────┘
```

## Flow

1. User presses PTT button
2. Pi records audio from mic
3. User releases button
4. Pi sends WAV to Mac Mini
5. Mac Mini transcribes with Whisper
6. Mac Mini sends text to OpenClaw (Ren)
7. Ren responds with text
8. Mac Mini converts to speech (OpenAI TTS)
9. Mac Mini sends audio back to Pi
10. Pi plays through earbuds

## Setup - Mac Mini (Server)

```bash
cd server

# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install deps
pip install -r requirements.txt

# Set OpenAI API key (for TTS)
export OPENAI_API_KEY="your-key"

# Run server
python voice_server.py
```

Server runs on port 5555 by default.

### Environment Variables

- `WHISPER_MODEL` - Whisper model size (tiny/base/small/medium) - default: base
- `OPENCLAW_API` - OpenClaw API endpoint - default: http://localhost:5001
- `TTS_VOICE` - OpenAI TTS voice (alloy/echo/fable/onyx/nova/shimmer) - default: alloy

## Setup - Raspberry Pi Zero

### Hardware

- Raspberry Pi Zero (W or 2W)
- Codec Zero I2S Audio HAT
- Wired earbuds with microphone
- Momentary push button for PTT

### Wiring

| Component | Pi GPIO |
|-----------|---------|
| PTT Button | GPIO17 → GND |
| Status LED (optional) | GPIO27 |

The button uses internal pull-up, so wire between GPIO17 and GND.

### Software Setup

```bash
# Install system deps
sudo apt update
sudo apt install -y python3-pip python3-venv portaudio19-dev

# Clone/copy the pi-client directory
cd pi-client

# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install deps
pip install -r requirements.txt

# Configure server address
export VOICE_SERVER="http://macmini.local:5555"

# Test audio (record 3 sec and playback)
python voice_client.py --test

# Run client
python voice_client.py
```

### Codec Zero Setup

The Codec Zero HAT should be automatically detected. Configure ALSA:

```bash
# Check if detected
aplay -l
arecord -l

# Test recording
arecord -D default -f S16_LE -r 16000 -c 1 -d 3 test.wav
aplay test.wav
```

### Autostart on Boot

Create `/etc/systemd/system/voice-client.service`:

```ini
[Unit]
Description=Ren Voice Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/voice-bridge/pi-client
Environment=VOICE_SERVER=http://macmini.local:5555
ExecStart=/home/pi/voice-bridge/pi-client/.venv/bin/python voice_client.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable voice-client
sudo systemctl start voice-client
```

## Optimizations for Speed

1. **Whisper model**: Use `tiny` or `base` for fastest transcription
2. **TTS**: OpenAI's `tts-1` is faster than `tts-1-hd`
3. **Network**: Keep Pi and Mac on same LAN, use wired if possible
4. **Audio format**: 16kHz mono WAV is optimal for Whisper

## Troubleshooting

### No audio on Pi
```bash
# Check ALSA devices
aplay -l
arecord -l

# Test with specific device
arecord -D plughw:0,0 -f S16_LE -r 16000 -c 1 -d 3 test.wav
```

### Server not responding
```bash
# Check server health
curl http://macmini.local:5555/health
```

### Slow responses
- Try `WHISPER_MODEL=tiny` for faster transcription
- Check network latency: `ping macmini.local`
- Ensure OpenClaw is running and responsive
