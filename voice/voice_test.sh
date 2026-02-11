#!/bin/bash
#
# Ren Voice Test - Simple voice loop using command line tools
# Tests: microphone → whisper → response → sag/say
#
# Usage: ./voice_test.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Settings
RECORD_DURATION=5
WHISPER_MODEL="base"
TTS_VOICE="Brian"

# Temp files
AUDIO_FILE="/tmp/ren_voice_input.wav"
TRANSCRIPT_FILE="/tmp/ren_voice_transcript.txt"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}   REN VOICE TEST${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check dependencies
check_deps() {
    local missing=()
    
    command -v whisper >/dev/null 2>&1 || missing+=("whisper")
    command -v sox >/dev/null 2>&1 || command -v rec >/dev/null 2>&1 || missing+=("sox (for recording)")
    command -v sag >/dev/null 2>&1 || command -v say >/dev/null 2>&1 || missing+=("sag or say (for TTS)")
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}Missing dependencies:${NC}"
        for dep in "${missing[@]}"; do
            echo "  - $dep"
        done
        echo ""
        echo "Install with:"
        echo "  brew install openai-whisper sox"
        echo "  brew install steipete/tap/sag  # optional, for better TTS"
        exit 1
    fi
    
    echo -e "${GREEN}✓ All dependencies found${NC}"
}

# Record audio
record_audio() {
    echo -e "\n${YELLOW}🎤 Recording for ${RECORD_DURATION} seconds...${NC}"
    echo "   Speak now!"
    
    # Try sox first, fall back to rec
    if command -v sox >/dev/null 2>&1; then
        sox -d -r 16000 -c 1 "$AUDIO_FILE" trim 0 "$RECORD_DURATION" 2>/dev/null
    elif command -v rec >/dev/null 2>&1; then
        rec -r 16000 -c 1 "$AUDIO_FILE" trim 0 "$RECORD_DURATION" 2>/dev/null
    else
        # macOS fallback using afrecord (if available)
        echo -e "${RED}No recording tool found${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Recording complete${NC}"
}

# Transcribe with Whisper
transcribe() {
    echo -e "\n${YELLOW}📝 Transcribing...${NC}"
    
    # Run whisper
    whisper "$AUDIO_FILE" \
        --model "$WHISPER_MODEL" \
        --output_format txt \
        --output_dir /tmp \
        --language en \
        2>/dev/null
    
    # Get transcript
    TRANSCRIPT=$(cat "/tmp/$(basename "$AUDIO_FILE" .wav).txt" 2>/dev/null | tr -d '\n')
    
    if [ -z "$TRANSCRIPT" ]; then
        echo -e "${RED}✗ No speech detected${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ You said: ${NC}$TRANSCRIPT"
    echo "$TRANSCRIPT"
}

# Generate response (placeholder - in production this calls OpenClaw)
generate_response() {
    local input="$1"
    
    echo -e "\n${YELLOW}💭 Thinking...${NC}"
    
    # Simple placeholder responses
    # In the real version, this would call the OpenClaw API
    case "$input" in
        *hello*|*hi*|*hey*)
            echo "Hello! It's great to hear your voice. I'm Ren, and I'm ready to help."
            ;;
        *how*are*you*|*how*you*doing*)
            echo "I'm doing well, thank you for asking! I'm excited to be practicing voice interaction."
            ;;
        *name*)
            echo "My name is Ren. I'm an AI assistant, and soon I'll have a robot body!"
            ;;
        *test*)
            echo "Voice test successful! I can hear you clearly and respond. The system is working."
            ;;
        *weather*)
            echo "I don't have real-time weather data in this test mode, but I'll be able to check that once fully integrated."
            ;;
        *bye*|*goodbye*|*quit*|*exit*)
            echo "Goodbye! It was nice talking with you."
            ;;
        *)
            echo "I heard you say: $input. In the full version, I'll give a much more thoughtful response!"
            ;;
    esac
}

# Speak response
speak() {
    local text="$1"
    
    echo -e "\n${YELLOW}🔊 Speaking...${NC}"
    
    # Try sag first (ElevenLabs), fall back to say
    if command -v sag >/dev/null 2>&1; then
        sag -v "$TTS_VOICE" "$text" 2>/dev/null
    else
        say "$text"
    fi
    
    echo -e "${GREEN}✓ Response spoken${NC}"
}

# Main loop
main() {
    check_deps
    
    echo ""
    echo "Press ENTER to start recording, Ctrl+C to quit."
    echo ""
    
    while true; do
        read -p "$(echo -e ${BLUE}[Press ENTER to talk]${NC} )"
        
        # Record
        if ! record_audio; then
            continue
        fi
        
        # Transcribe
        TRANSCRIPT=$(transcribe)
        if [ -z "$TRANSCRIPT" ]; then
            continue
        fi
        
        # Check for exit
        if [[ "$TRANSCRIPT" =~ (bye|goodbye|quit|exit) ]]; then
            speak "Goodbye! It was nice talking with you."
            echo -e "\n${BLUE}👋 Exiting...${NC}"
            break
        fi
        
        # Generate and speak response
        RESPONSE=$(generate_response "$TRANSCRIPT")
        echo -e "${GREEN}💬 Response: ${NC}$RESPONSE"
        speak "$RESPONSE"
        
        echo ""
    done
    
    # Cleanup
    rm -f "$AUDIO_FILE" "/tmp/$(basename "$AUDIO_FILE" .wav).txt"
}

# Run
main
