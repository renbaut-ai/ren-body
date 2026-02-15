#!/usr/bin/env python3
"""
Careful Grab Script for SO-101 Follower Arm
-------------------------------------------
Moves VERY SLOWLY because there's a $300 camera attached.
Takes photos before each move for visual feedback.

Usage:
    python3 careful_grab.py status              # Check arm and camera
    python3 careful_grab.py home                # Go to home position
    python3 careful_grab.py look                # Take a photo
    python3 careful_grab.py grab                # Run grab sequence (interactive)
    python3 careful_grab.py grab --arm=leader   # Use leader arm instead
"""

import sys
import os
import time
import subprocess
import json

# Add motion module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motion import SmoothMotion, JOINTS, JOINT_IDS

# ==================== CONFIGURATION ====================

# Arm ports
ARM_PORTS = {
    "follower": "/dev/cu.usbmodem5AAF2638141",  # RED arm with $300 camera
    "leader": "/dev/cu.usbmodem5AAF2634991",    # WHITE arm
}

# Default to follower, but can override with --arm=leader
FOLLOWER_PORT = ARM_PORTS["follower"]

# SLOW speed for safety (normal is 250, lower = slower)
CAREFUL_SPEED = 80
VERY_SLOW_SPEED = 50

# Photo output directory
PHOTO_DIR = "/tmp/grab_photos"

# Key positions (in servo units 0-4095, center is ~2048)
POSITIONS = {
    "home": {
        "shoulder_pan": 2048,     # centered
        "shoulder_lift": 1500,    # raised up (safe)
        "elbow_flex": 2048,       # neutral
        "wrist_flex": 2048,       # neutral
        "wrist_roll": 2048,       # neutral
        "gripper": 2500,          # open
    },
    "ready": {
        "shoulder_pan": 2048,
        "shoulder_lift": 1700,    # slightly lowered
        "elbow_flex": 2300,       # slightly bent
        "wrist_flex": 1600,       # angled down
        "wrist_roll": 2048,
        "gripper": 2500,          # open
    },
    "table_level": {
        "shoulder_pan": 2048,
        "shoulder_lift": 2200,    # lowered to table
        "elbow_flex": 2800,       # extended
        "wrist_flex": 1200,       # pointing down
        "wrist_roll": 2048,
        "gripper": 2500,          # open
    },
}

# ==================== CAMERA FUNCTIONS ====================

def find_usb_camera():
    """Find the USB 2.0 Camera device index."""
    result = subprocess.run(
        ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        capture_output=True, text=True
    )
    output = result.stderr
    
    for line in output.split('\n'):
        if 'USB 2.0 Camera' in line:
            # Extract device index like "[1]"
            import re
            match = re.search(r'\[(\d+)\]', line)
            if match:
                return match.group(1)
    return None

def take_photo(label="snapshot"):
    """Capture a photo from the USB camera."""
    os.makedirs(PHOTO_DIR, exist_ok=True)
    
    camera_idx = find_usb_camera()
    if not camera_idx:
        print("⚠️  USB camera not found")
        return None
    
    timestamp = time.strftime("%H%M%S")
    filename = f"{PHOTO_DIR}/{label}_{timestamp}.jpg"
    
    result = subprocess.run([
        "ffmpeg", "-f", "avfoundation",
        "-framerate", "30", "-video_size", "1280x720",
        "-i", camera_idx,
        "-frames:v", "1", "-update", "1",
        "-y", filename
    ], capture_output=True, timeout=10)
    
    if os.path.exists(filename):
        print(f"📸 Photo saved: {filename}")
        return filename
    else:
        print("⚠️  Failed to capture photo")
        return None

# ==================== ARM FUNCTIONS ====================

def connect_arm():
    """Connect to the follower arm."""
    arm = SmoothMotion(FOLLOWER_PORT)
    if not arm.connect():
        print(f"❌ Failed to connect to {FOLLOWER_PORT}")
        return None
    return arm

def check_status(arm):
    """Read and display arm status."""
    state = arm.read_state()
    print("\n📊 Current arm positions:")
    for joint, pos in state.positions.items():
        print(f"   {joint}: {pos}")
    return state.positions

def move_carefully(arm, target_positions, speed=CAREFUL_SPEED, description=""):
    """Move arm carefully with confirmation."""
    if description:
        print(f"\n🦾 {description}")
    
    # Show planned movement
    current = arm.read_state().positions
    print("   Moving:")
    for joint, target in target_positions.items():
        current_pos = current.get(joint, "?")
        delta = target - current_pos if isinstance(current_pos, int) else "?"
        print(f"     {joint}: {current_pos} → {target} (Δ{delta})")
    
    print(f"   Speed: {speed} (careful)")
    
    # Execute movement
    arm.set_torque(True)
    arm.move_to(target_positions, speed=speed)
    
    # Brief pause to let servo settle
    time.sleep(0.5)
    
    print("   ✅ Done")

def go_home(arm):
    """Move to safe home position."""
    print("\n🏠 Going to home position...")
    take_photo("before_home")
    move_carefully(arm, POSITIONS["home"], speed=CAREFUL_SPEED, description="Moving to home")
    take_photo("at_home")

def interactive_grab(arm):
    """Interactive grab sequence with photos at each step."""
    print("\n" + "="*50)
    print("🎯 INTERACTIVE GRAB SEQUENCE")
    print("="*50)
    print("This will move the arm step-by-step.")
    print("Press Enter to continue each step, or 'q' to quit.")
    print("="*50)
    
    steps = [
        ("home", "Move to safe home position", POSITIONS["home"]),
        ("ready", "Lower to ready position", POSITIONS["ready"]),
        ("table", "Lower to table level", POSITIONS["table_level"]),
        ("close", "Close gripper", {"gripper": 1500}),  # Closed
        ("lift", "Lift up", {"shoulder_lift": 1700, "elbow_flex": 2300}),
        ("home", "Return home", POSITIONS["home"]),
    ]
    
    for step_name, description, positions in steps:
        take_photo(f"before_{step_name}")
        
        print(f"\n📍 Next: {description}")
        response = input("   Press Enter to continue (q to quit): ").strip().lower()
        if response == 'q':
            print("   Stopping sequence.")
            break
        
        move_carefully(arm, positions, speed=CAREFUL_SPEED, description=description)
        take_photo(f"after_{step_name}")
    
    print("\n✅ Sequence complete!")
    print(f"📁 Photos saved to: {PHOTO_DIR}")

# ==================== MAIN ====================

def main():
    global FOLLOWER_PORT
    
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    # Check for --arm=leader or --arm=follower flag
    for arg in sys.argv:
        if arg.startswith("--arm="):
            arm_name = arg.split("=")[1].lower()
            if arm_name in ARM_PORTS:
                FOLLOWER_PORT = ARM_PORTS[arm_name]
                print(f"🦾 Using {arm_name.upper()} arm: {FOLLOWER_PORT}")
            else:
                print(f"Unknown arm: {arm_name}. Use 'follower' or 'leader'")
                return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        arm = connect_arm()
        if arm:
            check_status(arm)
            arm.disconnect()
        
        # Also check camera
        print("\n📷 Camera check:")
        camera_idx = find_usb_camera()
        if camera_idx:
            print(f"   USB 2.0 Camera found at index [{camera_idx}]")
        else:
            print("   ⚠️  USB 2.0 Camera not found")
    
    elif command == "home":
        arm = connect_arm()
        if arm:
            go_home(arm)
            arm.set_torque(False)
            arm.disconnect()
    
    elif command == "look":
        photo = take_photo("manual")
        if photo:
            print(f"View: open {photo}")
    
    elif command == "grab":
        arm = connect_arm()
        if arm:
            interactive_grab(arm)
            arm.set_torque(False)
            arm.disconnect()
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
