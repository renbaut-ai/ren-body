#!/bin/bash
#
# Ren Voice - Real voice-to-voice conversation with Ren
# ======================================================
# Records audio → Whisper transcription → OpenClaw API → TTS
#
# Usage:
#   ./ren_voice.sh              # Single turn
#   ./ren_voice.sh --loop       # Continuous conversation
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Settings
WHISPER_MODEL="base"  # tiny|base|small|medium|turbo
LOOP_MODE=false
MAX_RECORD_SECONDS=30  # Safety limit
DISCORD_ECHO=false     # Send transcripts to Discord

# OpenClaw Gateway settings
GATEWAY_URL="http://127.0.0.1:18789"
GATEWAY_TOKEN="056ce3b77a2ec9be60521bb1cca7cd05abf0692980078152"
AGENT_ID="main"
USER_ID="voice-hunter"

# Temp files
AUDIO_FILE="/tmp/ren_voice_input.wav"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --loop|-l)
            LOOP_MODE=true
            shift
            ;;
        --model|-m)
            WHISPER_MODEL="$2"
            shift 2
            ;;
        --discord|-d)
            DISCORD_ECHO=true
            shift
            ;;
        --help|-h)
            echo "Ren Voice - Talk to Ren"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --loop, -l          Continuous conversation mode"
            echo "  --discord, -d       Echo transcript & response to Discord"
            echo "  --model, -m MODEL   Whisper model: tiny|base|small|medium|turbo"
            echo "  --help, -h          Show this help"
            echo ""
            echo "Recording: Speak normally. Recording stops after ~1.5s of silence."
            echo "           Say 'goodbye' or 'stop' to exit in loop mode."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Banner
show_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════╗"
    echo "║         ${BOLD}REN VOICE INTERFACE${NC}${CYAN}           ║"
    echo "║   Speak naturally, I'm listening...   ║"
    echo "╚═══════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check dependencies
check_deps() {
    local missing=()
    
    command -v sox >/dev/null 2>&1 || missing+=("sox")
    command -v whisper >/dev/null 2>&1 || missing+=("whisper")
    command -v curl >/dev/null 2>&1 || missing+=("curl")
    command -v jq >/dev/null 2>&1 || missing+=("jq")
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}Missing dependencies:${NC}"
        for dep in "${missing[@]}"; do
            echo "  - $dep"
        done
        exit 1
    fi
    
    # Check TTS - try sag first, fall back to say
    TTS_CMD="say"  # Default to macOS say
    if command -v sag >/dev/null 2>&1; then
        # Quick test if sag works
        if sag --help >/dev/null 2>&1; then
            TTS_CMD="sag"
        fi
    fi
    
    # Verify gateway is running
    if ! curl -s "${GATEWAY_URL}/" >/dev/null 2>&1; then
        echo -e "${RED}OpenClaw gateway not running at ${GATEWAY_URL}${NC}"
        echo "Start it with: openclaw gateway"
        exit 1
    fi
    
    echo -e "${GREEN}✓ All dependencies ready${NC}"
    echo -e "   TTS: ${CYAN}${TTS_CMD}${NC}"
}

# Record audio with voice activity detection (stops on silence)
record_audio_vad() {
    echo -e "\n${YELLOW}🎤 Listening...${NC} ${BOLD}Speak now!${NC} (stops after silence)"
    
    # sox silence parameters:
    # 1 0.1 1% = start recording after 0.1s of sound above 1% threshold
    # 1 1.5 1% = stop after 1.5s of silence below 1% threshold
    # The trim at the end is a safety limit
    
    # Record with voice activity detection
    sox -d -r 16000 -c 1 -b 16 "$AUDIO_FILE" \
        silence 1 0.1 1% \
        1 1.5 1% \
        trim 0 $MAX_RECORD_SECONDS \
        2>/dev/null
    
    # Check if we got any audio
    local filesize=$(stat -f%z "$AUDIO_FILE" 2>/dev/null || stat -c%s "$AUDIO_FILE" 2>/dev/null || echo "0")
    if [ "$filesize" -lt 10000 ]; then
        echo -e "${RED}✗ No speech detected (file too small)${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Recording complete${NC}"
    return 0
}

# Transcribe with Whisper
transcribe() {
    echo -e "${YELLOW}📝 Transcribing...${NC}"
    
    local output_dir="/tmp/ren_whisper_$$"
    mkdir -p "$output_dir"
    
    whisper "$AUDIO_FILE" \
        --model "$WHISPER_MODEL" \
        --output_format txt \
        --output_dir "$output_dir" \
        --language en \
        --fp16 False \
        2>/dev/null
    
    local txt_file="$output_dir/$(basename "$AUDIO_FILE" .wav).txt"
    if [ -f "$txt_file" ]; then
        TRANSCRIPT=$(cat "$txt_file" | tr -d '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        rm -rf "$output_dir"
        
        if [ -z "$TRANSCRIPT" ] || [ "$TRANSCRIPT" = "[BLANK_AUDIO]" ]; then
            echo -e "${RED}✗ No speech detected${NC}"
            return 1
        fi
        
        echo -e "${GREEN}✓ You said:${NC} ${BOLD}$TRANSCRIPT${NC}"
        return 0
    else
        rm -rf "$output_dir"
        echo -e "${RED}✗ Transcription failed${NC}"
        return 1
    fi
}

# Send to OpenClaw via HTTP API and get response
ask_ren() {
    local message="$1"
    
    echo -e "${YELLOW}💭 Thinking...${NC}"
    
    # Call OpenClaw's OpenAI-compatible API
    # x-openclaw-no-tts: true returns text instead of audio file
    local api_response
    api_response=$(curl -sS "${GATEWAY_URL}/v1/chat/completions" \
        -H "Authorization: Bearer ${GATEWAY_TOKEN}" \
        -H "Content-Type: application/json" \
        -H "x-openclaw-agent-id: ${AGENT_ID}" \
        -H "x-openclaw-no-tts: true" \
        -d "{
            \"model\": \"openclaw:main\",
            \"user\": \"${USER_ID}\",
            \"messages\": [
                {
                    \"role\": \"user\",
                    \"content\": \"[Voice from Hunter]: ${message}\"
                }
            ],
            \"max_tokens\": 500
        }" 2>&1)
    
    # Extract response content
    RESPONSE=$(echo "$api_response" | jq -r '.choices[0].message.content // empty' 2>/dev/null)
    
    if [ -z "$RESPONSE" ]; then
        local error_msg=$(echo "$api_response" | jq -r '.error.message // empty' 2>/dev/null)
        if [ -n "$error_msg" ]; then
            echo -e "${RED}API Error: $error_msg${NC}"
            RESPONSE="I had trouble processing that. Could you try again?"
        else
            echo -e "${RED}Empty response from API${NC}"
            RESPONSE="I heard you, but something went wrong with my response."
        fi
    fi
    
    # Clean up response for voice (remove markdown, limit length)
    RESPONSE=$(echo "$RESPONSE" | sed 's/\*\*//g; s/\*//g; s/`//g; s/#//g' | head -c 800)
    
    echo -e "${GREEN}💬 Ren:${NC} $RESPONSE"
}

# Send to Discord (if enabled)
send_to_discord() {
    local transcript="$1"
    local response="$2"
    
    if [ "$DISCORD_ECHO" = true ]; then
        echo -e "${YELLOW}📤 Sending to Discord...${NC}"
        
        # Format message
        local message="🎤 **Voice:** ${transcript}

💬 **Ren:** ${response}"
        
        # Send via openclaw message
        openclaw message send \
            --channel discord \
            --target "vinny6688" \
            --message "$message" \
            2>/dev/null || echo -e "${RED}   (Discord send failed)${NC}"
    fi
}

# Speak the response
speak() {
    local text="$1"
    
    echo -e "${YELLOW}🔊 Speaking...${NC}"
    
    if [ "$TTS_CMD" = "sag" ]; then
        # Try sag, fall back to say if it fails (e.g., rate limited)
        if ! sag -v Brian "$text" 2>/dev/null; then
            echo -e "${YELLOW}   (sag failed, using macOS voice)${NC}"
            say -v "Samantha" "$text"
        fi
    else
        # Use macOS say with a decent voice
        say -v "Samantha" "$text"
    fi
}

# Single conversation turn
do_turn() {
    # Record with VAD
    if ! record_audio_vad; then
        return 1
    fi
    
    # Transcribe
    if ! transcribe; then
        return 1
    fi
    
    # Check for exit commands (compatible with bash 3.x)
    local transcript_lower=$(echo "$TRANSCRIPT" | tr '[:upper:]' '[:lower:]')
    if [[ "$transcript_lower" =~ ^(goodbye|bye|exit|quit|stop)[.!]?$ ]]; then
        RESPONSE="Goodbye Hunter! It was great talking with you."
        echo -e "${GREEN}💬 Ren:${NC} $RESPONSE"
        speak "$RESPONSE"
        return 2  # Signal to exit
    fi
    
    # Get response from Ren
    ask_ren "$TRANSCRIPT"
    
    # Send to Discord (if enabled)
    send_to_discord "$TRANSCRIPT" "$RESPONSE"
    
    # Speak response
    speak "$RESPONSE"
    
    return 0
}

# Main
main() {
    show_banner
    check_deps
    
    echo -e "Whisper model: ${CYAN}${WHISPER_MODEL}${NC}"
    if [ "$DISCORD_ECHO" = true ]; then
        echo -e "Discord echo: ${CYAN}enabled${NC}"
    fi
    echo -e "Recording stops automatically after ~1.5s of silence"
    echo ""
    
    if [ "$LOOP_MODE" = true ]; then
        echo -e "${BOLD}Continuous mode.${NC} Say 'goodbye' to exit, or press Ctrl+C."
        echo ""
        
        while true; do
            read -p $'\e[34m[Press ENTER when ready to speak]\e[0m '
            
            result=0
            do_turn || result=$?
            
            if [ $result -eq 2 ]; then
                echo -e "\n${CYAN}👋 Session ended.${NC}"
                break
            fi
            
            echo ""
        done
    else
        echo -e "${BOLD}Single turn mode.${NC} Use --loop for conversation."
        echo ""
        read -p $'\e[34m[Press ENTER when ready to speak]\e[0m '
        do_turn
    fi
    
    # Cleanup
    rm -f "$AUDIO_FILE"
}

# Run
main
