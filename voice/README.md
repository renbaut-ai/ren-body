# Ren Voice Interaction

Voice-to-voice conversation system for the Ren robot.

**This is the real deal** — speaks to the actual Ren AI, not placeholder responses!

## Components

1. **Speech-to-Text (STT)**: OpenAI Whisper (local)
2. **Language Model**: OpenClaw Gateway → Ren (Claude)
3. **Text-to-Speech (TTS)**: ElevenLabs via `sag` (Brian voice)

## Setup

### Install Dependencies

```bash
# Audio recording
brew install sox

# Whisper (if not already installed)
brew install openai-whisper

# ElevenLabs TTS (optional but recommended)
brew install steipete/tap/sag

# Python packages (for advanced script)
pip install sounddevice numpy
```

### ElevenLabs Setup

Set your API key:
```bash
export ELEVENLABS_API_KEY="your-key-here"
```

Or add to `~/.zshrc` / `~/.bashrc`.

## Usage

### Main Voice Interface (Recommended)

```bash
cd ~/Projects/ren-body/voice
./ren_voice.sh --loop
```

This connects to the **real Ren** via OpenClaw's API!

Options:
- `--loop` / `-l` — Continuous conversation mode
- `--duration N` / `-d N` — Recording length in seconds (default: 5)
- `--model MODEL` / `-m MODEL` — Whisper model (tiny/base/small/medium)
- `--voice VOICE` / `-v VOICE` — ElevenLabs voice name

### Test Script (Placeholder Responses)

For testing audio pipeline without API:
```bash
./voice_test.sh
```

### Python Version (Advanced)

```bash
python voice_chat.py              # Push-to-talk
python voice_chat.py --continuous # Always listening
python voice_chat.py --wake-word "hey ren"
```

## Files

| File | Description |
|------|-------------|
| `ren_voice.sh` | **Main script** — real Ren integration |
| `voice_test.sh` | Test script (placeholder responses) |
| `voice_chat.py` | Python version (advanced) |
| `README.md` | This file |

## How the API Works

The `ren_voice.sh` script uses OpenClaw's OpenAI-compatible API:

```bash
curl http://127.0.0.1:18789/v1/chat/completions \
  -H "Authorization: Bearer <token>" \
  -H "x-openclaw-no-tts: true" \
  -d '{"model":"openclaw:main", "messages":[...]}'
```

Key headers:
- `Authorization: Bearer <token>` — Gateway auth
- `x-openclaw-no-tts: true` — Returns text (we do our own TTS)
- `x-openclaw-agent-id: main` — Target Ren agent

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    VOICE LOOP                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────┐    ┌──────────┐    ┌─────────────────┐   │
│   │   Mic   │───▶│ Whisper  │───▶│ OpenClaw (Ren)  │   │
│   │ (sox)   │    │  (STT)   │    │   thinking...   │   │
│   └─────────┘    └──────────┘    └────────┬────────┘   │
│                                           │             │
│                                           ▼             │
│   ┌─────────┐    ┌──────────┐    ┌─────────────────┐   │
│   │ Speaker │◀───│   sag    │◀───│  Text Response  │   │
│   │         │    │  (TTS)   │    │                 │   │
│   └─────────┘    └──────────┘    └─────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Latency Considerations

For real-time conversation, latency matters:

| Component | Typical Latency | Notes |
|-----------|-----------------|-------|
| Recording | Real-time | - |
| Whisper (base) | 1-3s | Use `tiny` for faster |
| Whisper (turbo) | 0.5-1s | Best balance |
| OpenClaw/Claude | 1-5s | Depends on response length |
| ElevenLabs TTS | 0.5-2s | Streaming available |
| **Total** | **3-10s** | Acceptable for conversation |

### Optimization Tips

1. **Use smaller Whisper model** for faster transcription:
   - `tiny`: Fastest, less accurate
   - `base`: Good balance
   - `turbo`: Best quality/speed ratio

2. **Use ElevenLabs Flash model** for faster TTS:
   ```bash
   sag -m eleven_flash_v2_5 "text"
   ```

3. **Consider streaming** for both STT and TTS (advanced)

## Robot Integration

For the physical robot body:

1. USB microphone array (directional/beamforming)
2. Speaker connected via audio amp
3. This voice loop running continuously
4. Wake word or push-button activation

### Recommended Hardware

- **Mic**: ReSpeaker USB Mic Array ($50-60)
- **Speaker**: 3W+ full range speaker
- **Amp**: MAX98357A or PAM8403

## Troubleshooting

### No audio input
- Check mic is selected: `sox -d -d` (should play back)
- macOS: System Preferences → Security → Microphone

### Whisper errors
- Check model downloaded: `ls ~/.cache/whisper/`
- Try smaller model: `--model tiny`

### sag/TTS issues
- Verify API key: `echo $ELEVENLABS_API_KEY`
- Test directly: `sag "hello"`
- Fallback to `say`: `say "hello"`

---

*Part of the Ren Robot Body project*
