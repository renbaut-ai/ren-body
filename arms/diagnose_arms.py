#!/usr/bin/env python3
"""
Diagnose SO-101 Robot Arms
--------------------------
Check which arms are connected and responding.

Usage:
    python3 diagnose_arms.py
"""

import subprocess
import scservo_sdk as sdk

# Known ports from config
PORTS = {
    "follower": "/dev/cu.usbmodem5AAF2638141",  # RED arm with camera
    "leader": "/dev/cu.usbmodem5AAF2634991",    # WHITE arm
}

ADDR_PRESENT_POSITION = 56
JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]

def check_usb_devices():
    """List connected USB serial devices."""
    print("🔌 USB Serial Devices:")
    result = subprocess.run(
        ["ls", "-la", "/dev/cu.usbmodem*"],
        capture_output=True, text=True, shell=False
    )
    # Use shell for glob
    result = subprocess.run(
        "ls -la /dev/cu.usbmodem* 2>/dev/null || echo '   None found'",
        shell=True, capture_output=True, text=True
    )
    for line in result.stdout.strip().split('\n'):
        print(f"   {line}")
    print()

def check_arm(name, port):
    """Check if an arm is responding on a port."""
    print(f"🦾 Checking {name.upper()} arm at {port}...")
    
    try:
        port_handler = sdk.PortHandler(port)
        packet_handler = sdk.PacketHandler(0)
        
        if not port_handler.openPort():
            print(f"   ❌ Cannot open port (device may be disconnected)")
            return False
        
        port_handler.setBaudRate(1000000)
        
        responding = []
        not_responding = []
        
        for servo_id in range(1, 7):
            pos, result, error = packet_handler.read2ByteTxRx(
                port_handler, servo_id, ADDR_PRESENT_POSITION
            )
            if result == sdk.COMM_SUCCESS:
                responding.append((servo_id, JOINT_NAMES[servo_id-1], pos))
            else:
                not_responding.append((servo_id, JOINT_NAMES[servo_id-1], result))
        
        port_handler.closePort()
        
        if responding:
            print(f"   ✅ Responding servos:")
            for sid, name, pos in responding:
                print(f"      [{sid}] {name}: position {pos}")
        
        if not_responding:
            print(f"   ⚠️  Not responding:")
            for sid, name, err in not_responding:
                print(f"      [{sid}] {name}: error code {err}")
        
        if len(responding) == 6:
            print(f"   🎉 All 6 servos OK!")
            return True
        elif len(responding) > 0:
            print(f"   ⚠️  Partial response ({len(responding)}/6 servos)")
            return True
        else:
            print(f"   ❌ No servos responding")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_cameras():
    """Check available cameras."""
    print("📷 Cameras:")
    result = subprocess.run(
        ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        capture_output=True, text=True
    )
    
    in_video = False
    for line in result.stderr.split('\n'):
        if 'video devices' in line.lower():
            in_video = True
            continue
        if 'audio devices' in line.lower():
            in_video = False
            continue
        if in_video and '[AVFoundation' in line:
            # Extract device info
            if ']' in line:
                device_part = line.split('] ')[-1] if '] ' in line else line
                print(f"   {device_part.strip()}")
    print()

def main():
    print("="*60)
    print("🔧 SO-101 ARM DIAGNOSTICS")
    print("="*60)
    print()
    
    check_usb_devices()
    check_cameras()
    
    results = {}
    for name, port in PORTS.items():
        results[name] = check_arm(name, port)
        print()
    
    print("="*60)
    print("📋 SUMMARY")
    print("="*60)
    for name, ok in results.items():
        status = "✅ OK" if ok else "❌ ISSUE"
        print(f"   {name.upper()}: {status}")
    
    if not results["follower"]:
        print()
        print("💡 TROUBLESHOOTING (follower arm not responding):")
        print("   1. Check power cable to follower arm")
        print("   2. Check USB cable connection")
        print("   3. Try unplugging and replugging USB")
        print("   4. Check if servo bus cable is loose inside arm base")
    
    if results["follower"] and results["leader"]:
        print()
        print("🎉 Both arms responding! Ready for careful_grab.py")

if __name__ == "__main__":
    main()
