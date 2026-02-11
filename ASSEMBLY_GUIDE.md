# Ren Robot Body - Assembly Guide (3D Printed Version)

A step-by-step guide to printing and assembling the Ren robot body.

---

## Table of Contents
1. [Tools & Supplies Required](#tools--supplies-required)
2. [Printing Overview](#printing-overview)
3. [Phase 1: Print All Parts](#phase-1-print-all-parts)
4. [Phase 2: Post-Processing](#phase-2-post-processing)
5. [Phase 3: Base Assembly](#phase-3-base-assembly)
6. [Phase 4: Spine Assembly](#phase-4-spine-assembly)
7. [Phase 5: Shoulder & Arm Installation](#phase-5-shoulder--arm-installation)
8. [Phase 6: Head Assembly](#phase-6-head-assembly)
9. [Phase 7: Electronics & Wiring](#phase-7-electronics--wiring)
10. [Phase 8: Software Setup](#phase-8-software-setup)
11. [Testing & Calibration](#testing--calibration)
12. [Troubleshooting](#troubleshooting)

---

## Tools & Supplies Required

### Printing
- [ ] Bambu A1 (or similar, 256mm+ build volume)
- [ ] Filament: Grey PETG (~2kg), Blue PETG (~0.7kg), White PETG (~0.4kg), Red PLA (~0.1kg)
- [ ] Painter's tape or glue stick (bed adhesion)
- [ ] Flush cutters (support removal)

### Assembly Tools
- [ ] Metric hex key set (2mm, 2.5mm, 3mm, 4mm)
- [ ] Phillips screwdrivers (#0, #1, #2)
- [ ] Soldering iron (for heat-set inserts AND electronics)
- [ ] Heat-set insert tips (M3, M4)
- [ ] Wire strippers
- [ ] Multimeter
- [ ] Calipers

### Finishing Tools
- [ ] Sandpaper (120, 220, 400 grit)
- [ ] Files (flat, round)
- [ ] Deburring tool
- [ ] Heat gun (optional, for minor warping fixes)

### Safety
- [ ] Safety glasses
- [ ] Work gloves
- [ ] Ventilation (soldering/printing)
- [ ] ESD wrist strap (electronics)

### Consumables
- [ ] Heat-set inserts: M3 × 50, M4 × 20
- [ ] Bolts: M3×8, M3×12, M3×20, M4×12, M4×20 (assorted)
- [ ] Locknuts: M3, M4
- [ ] CA glue (super glue)
- [ ] Epoxy (structural bonding)
- [ ] Thread locker (blue Loctite)

---

## Printing Overview

### Print Settings by Material

| Material | Nozzle | Bed | Speed | Notes |
|----------|--------|-----|-------|-------|
| PETG (structural) | 240-250°C | 80°C | 50-60mm/s | Enclosure helps |
| PLA (accents) | 200-210°C | 60°C | 60-80mm/s | Easy, fast |

### General Settings (All Parts)
- **Layer height:** 0.2mm (0.16mm for fine detail)
- **Walls:** 4 perimeters
- **Infill:** 40% (structural), 20% (covers/cosmetic)
- **Infill pattern:** Gyroid or Grid
- **Supports:** As needed (avoid where possible through orientation)
- **Brim:** Recommended for large flat parts

### Part Orientation Guidelines
- Print large flat faces DOWN
- Orient for minimal supports
- Holes/threads should be vertical where possible
- Long parts print standing up if they fit

---

## Phase 1: Print All Parts

**Total estimated print time: 75-110 hours**

Print in the order below — earlier batches can be post-processed while later ones print.

### Batch 1: Base Frame (Grey PETG) — ~20-25 hours

| Part | Qty | Est. Time | Orientation | Notes |
|------|-----|-----------|-------------|-------|
| Base_Section_1 | 1 | 5h | Flat | Add heat-set insert holes |
| Base_Section_2 | 1 | 5h | Flat | Mirror of section 1 |
| Base_Section_3 | 1 | 5h | Flat | |
| Base_Section_4 | 1 | 5h | Flat | |
| Ballast_Mount | 1 | 1h | Flat | Optional |

**Check before printing:**
- [ ] Motor mount holes sized correctly
- [ ] Bolt pattern matches between sections
- [ ] Battery tray fits your battery

### Batch 2: Drive System (Grey PETG) — ~8-10 hours

| Part | Qty | Est. Time | Orientation | Notes |
|------|-----|-----------|-------------|-------|
| Sprocket_Left_Front | 1 | 1.5h | Flat (axle vertical) | |
| Sprocket_Left_Rear | 1 | 1.5h | Flat | |
| Sprocket_Right_Front | 1 | 1.5h | Flat | |
| Sprocket_Right_Rear | 1 | 1.5h | Flat | |
| Motor_Mount_Left | 1 | 1h | Flat | |
| Motor_Mount_Right | 1 | 1h | Flat | |
| Idler_Tensioner × 2 | 2 | 1h | Flat | Track tension adjustment |

**Important:** Measure your purchased rubber tracks FIRST! Sprocket diameter must match track pitch.

### Batch 3: Spine Sections (Grey PETG) — ~25-30 hours

| Part | Qty | Est. Time | Orientation | Notes |
|------|-----|-----------|-------------|-------|
| Spine_Section_1 | 1 | 6h | Standing | Rod channels must align |
| Spine_Section_2 | 1 | 6h | Standing | |
| Spine_Section_3 | 1 | 6h | Standing | |
| Spine_Section_4 | 1 | 6h | Standing | Top section |
| Spine_Connector × 3 | 3 | 2h | Flat | Joins spine sections |
| Cross_Brace_Lower | 1 | 1.5h | Flat | |
| Cross_Brace_Mid | 1 | 1.5h | Flat | |
| Cross_Brace_Upper | 1 | 1.5h | Flat | |

### Batch 4: Shoulders (Blue PETG) — ~6-8 hours

| Part | Qty | Est. Time | Orientation | Notes |
|------|-----|-----------|-------------|-------|
| Shoulder_Plate_Left | 1 | 2h | Flat | |
| Shoulder_Plate_Right | 1 | 2h | Flat | |
| Arm_Mount_Left | 1 | 1.5h | Flat | SO-101 specific fit |
| Arm_Mount_Right | 1 | 1.5h | Flat | Test fit before full print |

**Test fit:** Print a small test piece with the SO-101 mounting pattern first!

### Batch 5: Head - White Parts (White PETG) — ~4-5 hours

| Part | Qty | Est. Time | Orientation | Notes |
|------|-----|-----------|-------------|-------|
| Head_Front_Shell | 1 | 3h | Face down | Display cutout |
| Display_Bezel | 1 | 1h | Flat | Frames LED matrix |

### Batch 6: Head - Grey Parts (Grey PETG) — ~5-7 hours

| Part | Qty | Est. Time | Orientation | Notes |
|------|-----|-----------|-------------|-------|
| Head_Rear_Shell | 1 | 3h | Flat | Camera mount holes |
| Neck_Tube | 1 | 2h | Standing | Consider aluminum tube instead |
| Pan_Tilt_Base | 1 | 1h | Flat | Servo mount |
| Pan_Tilt_Arm | 1 | 0.5h | Flat | |

### Batch 7: Accents (Red PLA) — ~2 hours

| Part | Qty | Est. Time | Orientation | Notes |
|------|-----|-----------|-------------|-------|
| Eye_Ring_Left | 1 | 0.5h | Flat | |
| Eye_Ring_Right | 1 | 0.5h | Flat | |
| Status_Indicator | 1 | 0.25h | Flat | Chest light |
| Cable_Clips × 20 | 20 | 1h | Flat (batch) | Snap-fit |

### Batch 8: Miscellaneous (Grey PLA/PETG) — ~5 hours

| Part | Qty | Est. Time | Orientation | Notes |
|------|-----|-----------|-------------|-------|
| Cable_Channels × 6 | 6 | 2h | Flat | Wire routing |
| Electronics_Tray | 1 | 2h | Flat | Arduino/driver mount |
| Battery_Strap_Mounts × 2 | 2 | 0.5h | Flat | Velcro strap anchors |
| Misc covers/panels | - | 1h | Flat | As needed |

---

## Phase 2: Post-Processing

### For All Printed Parts

1. **Remove supports** carefully with flush cutters
2. **Clean up stringing** with heat gun (quick pass) or blade
3. **Sand mating surfaces** with 220 grit for better fit
4. **Test fit** parts together before installing inserts
5. **Check hole sizes** with calipers — drill out if undersized

### Installing Heat-Set Inserts

**Tools needed:** Soldering iron with heat-set tip, or plain iron (slower)

**Temperature:** ~220-250°C for PETG

**Technique:**
1. Place insert on hole (don't force)
2. Apply gentle pressure with hot iron
3. Let insert sink in slowly (5-10 seconds)
4. Stop when insert is ~0.5mm below surface
5. Let cool completely before use

**Insert locations:**

| Part | Insert Size | Qty | Purpose |
|------|-------------|-----|---------|
| Base sections | M4 | 16 | Join sections together |
| Base sections | M3 | 8 | Motor mount |
| Spine sections | M3 | 24 | Connectors + braces |
| Shoulder plates | M4 | 8 | Attach to spine |
| Arm mounts | M3 | 8 | SO-101 attachment |
| Head shells | M3 | 12 | Head assembly |

### Installing Reinforcement Rods

The spine requires 4 steel/aluminum rods (8mm × ~800mm) for rigidity.

1. **Dry fit** all spine sections to check alignment
2. **Insert rods** through bottom section first
3. **Add sections** one at a time, threading onto rods
4. Rods should extend into shoulder platform
5. **Secure** with set screws or epoxy at top/bottom

---

## Phase 3: Base Assembly

**Time estimate:** 2-3 hours

### Step 3.1: Prepare Base Sections

1. Install all heat-set inserts in base sections
2. Dry fit sections together to check alignment
3. Sand mating edges if needed

### Step 3.2: Assemble Base Frame

1. Place sections on flat surface
2. Align bolt holes carefully
3. Insert M4 bolts through sections
4. Tighten gradually in cross pattern (don't overtighten!)
5. Check frame is flat (no rocking)

### Step 3.3: Install Motor Mounts

1. Position motor mounts inside base
2. Align with sprocket positions
3. Bolt down with M3 hardware
4. **Do not install motors yet** — easier to wire first

### Step 3.4: Install Sprockets & Idlers

1. Mount rear idler wheels on tensioner assemblies
2. Install tensioners in base (adjustable position)
3. Mount front drive sprockets (connect to motor shafts later)
4. Verify wheels spin freely

### Step 3.5: Track Installation

1. Loop rubber track around sprockets
2. Adjust idler position until track is snug
3. Track should deflect ~10mm when pressed
4. Lock idler position
5. Repeat for second track

### Step 3.6: Install Motors

1. Slide motors into mounts
2. Align motor shaft with drive sprocket
3. Secure with set screw or coupling
4. Wire motor leads (label L+, L-, R+, R-)
5. Test spin direction (both should drive forward)

**⚠️ CHECKPOINT:** 
- [ ] Tracks move smoothly
- [ ] No binding or rubbing
- [ ] Motors spin correct direction

---

## Phase 4: Spine Assembly

**Time estimate:** 2-3 hours

### Step 4.1: Prepare Spine Sections

1. Install heat-set inserts
2. Check rod holes are clear (drill if needed)
3. Dry fit all sections to verify alignment

### Step 4.2: Pre-Install Wiring Channels

Before assembling spine, install internal cable routing:

1. Position cable channels inside spine sections
2. Fish pull-strings through for later wiring
3. Leave strings accessible at top and bottom

### Step 4.3: Assemble Spine

1. Start with bottom spine section
2. Insert reinforcement rods from bottom
3. Add spine connector
4. Stack next section, threading onto rods
5. Repeat for all sections
6. Tighten connector bolts progressively

### Step 4.4: Attach Cross Braces

1. Install lower brace (~50mm above base)
2. Install mid brace (middle of spine)
3. Install upper brace (just below shoulders)
4. Verify spine is straight and square

### Step 4.5: Mount Spine to Base

1. Position spine on base center
2. Align mounting holes
3. Bolt down with M4 hardware
4. Check spine is vertical (use level)
5. Apply thread locker to base bolts

**⚠️ CHECKPOINT:**
- [ ] Spine is vertical
- [ ] No wobble or flex
- [ ] Cable routing accessible

---

## Phase 5: Shoulder & Arm Installation

**Time estimate:** 1.5-2 hours

### Step 5.1: Attach Shoulder Plates

1. Position shoulder plates on top of spine
2. Align with reinforcement rod holes
3. Rod ends should seat into shoulder pockets
4. Bolt down shoulders to upper spine section
5. Verify shoulders are level

### Step 5.2: Install Arm Mounts

1. Attach arm mount brackets to shoulder plates
2. Position for correct arm spacing (280mm center-to-center)
3. Tighten bolts but leave slightly loose for adjustment

### Step 5.3: Mount SO-101 Arms

⚠️ **Power off arms before handling**

1. Position left arm on left mount
2. Align mounting holes
3. Secure with M3 bolts (don't overtighten - plastic threads!)
4. Repeat for right arm
5. Verify both arms are level and parallel

### Step 5.4: Route Arm Cables

1. Bundle each arm's cables together
2. Route down through spine interior
3. Use cable clips on cross braces
4. Leave service loop at arm base
5. Label cables: ARM_L, ARM_R

### Step 5.5: Final Arm Mount Adjustment

1. Power on arms briefly
2. Home both arms
3. Check for collision with body/shoulders
4. Adjust mount position if needed
5. Final tighten all bolts

**⚠️ CHECKPOINT:**
- [ ] Arms securely mounted
- [ ] Arms home without collision
- [ ] Cables routed cleanly

---

## Phase 6: Head Assembly

**Time estimate:** 2-3 hours

### Step 6.1: Pan-Tilt Mechanism

1. Assemble pan servo into base mount
2. Attach tilt bracket to pan servo horn
3. Install tilt servo
4. Test movement by hand (no power)
5. Mount assembly to top of neck

### Step 6.2: Mount Neck to Shoulders

1. Position neck tube on shoulder center
2. Bolt down with M3 hardware
3. Route servo wires down through neck
4. Verify neck is vertical

### Step 6.3: Install Cameras

**OAK-D Lite (front):**
1. Mount camera to head front shell interior
2. Position lenses to align with eye holes
3. Secure with M2/M2.5 screws
4. Route USB-C down

**Rear Camera:**
1. Mount to head rear shell
2. Angle slightly down (~15°)
3. Route USB cable

### Step 6.4: Install Face Display

1. Position LED matrix behind display cutout
2. Attach with small dabs of hot glue or mounting tape
3. Connect data + power wires
4. Install display bezel over matrix

### Step 6.5: Install Audio (Speaker + Mic)

1. Mount speaker inside head (facing forward or down)
2. Connect to amplifier board
3. Mount mic array (position for best pickup)
4. Route all audio wires down through neck

### Step 6.6: Install Eye Rings

1. Press-fit or glue red eye rings around camera lenses
2. Should frame the cameras visually

### Step 6.7: Assemble Head Shells

1. Connect front and rear head shells
2. Secure with M3 bolts
3. Verify all cameras and display visible
4. Check no wires pinched

### Step 6.8: Mount Head to Pan-Tilt

1. Attach head assembly to tilt mechanism
2. Balance head (should not droop when unpowered)
3. Test pan-tilt movement range
4. Adjust stops if needed to prevent wire strain

**⚠️ CHECKPOINT:**
- [ ] Pan-tilt moves smoothly
- [ ] All cameras have clear view
- [ ] Display visible
- [ ] No wires pinched

---

## Phase 7: Electronics & Wiring

**Time estimate:** 3-4 hours

### Step 7.1: System Wiring Diagram

```
MAIN BATTERY (12V LiPo)
    │
    ├─► Main Switch
    │       │
    │       ├─► Motor Driver ───► Left Motor
    │       │                 ───► Right Motor
    │       │
    │       └─► 5V Buck Converter (10A)
    │               │
    │               ├─► Arduino/ESP32
    │               ├─► Servo Power (pan-tilt)
    │               ├─► LED Matrix
    │               └─► Audio Amp
    │
    └─► Voltage Monitor (display)

MAC MINI (separate power, USB-C)
    │
    └─► USB Hub
            ├─► Left Arm (USB)
            ├─► Right Arm (USB)
            ├─► OAK-D Lite (USB 3.0)
            ├─► Rear Camera (USB 2.0)
            ├─► USB Mic Array
            └─► Arduino/ESP32 (serial)
```

### Step 7.2: Mount Electronics in Base

1. Install electronics tray in base
2. Mount motor driver (with standoffs for cooling)
3. Mount buck converters
4. Mount Arduino/ESP32
5. Position Mac Mini in designated bay

### Step 7.3: Power Wiring

1. **Main battery leads** → Switch → Distribution
2. **Motor driver power** (12V from switch)
3. **Buck converter input** (12V from switch)
4. **5V distribution** to all logic components
5. **Add fuses:** 20A on motors, 10A on 5V rail

### Step 7.4: Motor Wiring

1. Motor leads to driver outputs
   - Left motor → M1A, M1B
   - Right motor → M2A, M2B
2. Driver control pins to Arduino PWM outputs
3. Encoder wires (if equipped) to Arduino interrupt pins

### Step 7.5: Servo Wiring

1. Pan servo signal → Arduino PWM pin (or PCA9685)
2. Tilt servo signal → Arduino PWM pin
3. Servo power from 5V rail (shared ground!)

### Step 7.6: Display Wiring

1. LED matrix data → Arduino digital pin
2. LED matrix power → 5V rail (check current draw!)
3. May need separate 5V supply if >2A draw

### Step 7.7: Audio Wiring

1. Amplifier input from Mac Mini audio jack (or USB DAC)
2. Amplifier power from 5V rail
3. Speaker to amplifier output
4. USB mic to USB hub

### Step 7.8: USB Connections

1. Connect powered USB hub to Mac Mini
2. Plug in all USB devices:
   - Both arm controllers
   - OAK-D Lite (use USB 3.0 port!)
   - Rear camera
   - Mic array
   - Arduino (serial)

### Step 7.9: Wire Management

1. Label every wire at both ends
2. Bundle related wires together
3. Route cleanly through spine
4. Secure with clips and velcro
5. Leave service loops for maintenance
6. Verify no pinch points

### Step 7.10: Final Electrical Check

Use multimeter to verify:
- [ ] No shorts between power and ground
- [ ] 12V present at motor driver input
- [ ] 5V present at buck converter output (within 5%)
- [ ] All grounds connected
- [ ] Correct polarity everywhere

---

## Phase 8: Software Setup

**Time estimate:** 2-4 hours

### Step 8.1: Mac Mini Setup

1. Complete macOS initial setup
2. Install Homebrew:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Install essentials:
   ```bash
   xcode-select --install
   brew install python git node
   ```

### Step 8.2: Install OpenClaw

Follow OpenClaw docs for installation. Verify:
```bash
openclaw status
```

### Step 8.3: Arduino/ESP32 Firmware

**Motor control firmware features:**
- Serial command protocol (from Mac Mini)
- PWM motor speed control
- Encoder feedback (if equipped)
- Servo control for pan-tilt
- LED matrix driver
- Battery voltage reporting
- Emergency stop input

Flash firmware using Arduino IDE or PlatformIO.

**Test serial communication:**
```python
import serial
ser = serial.Serial('/dev/tty.usbmodemXXXX', 115200)
ser.write(b'PING\n')
print(ser.readline())  # Should return "PONG"
```

### Step 8.4: Camera Setup

**OAK-D Lite:**
```bash
pip install depthai
python -c "import depthai; print(depthai.__version__)"
```

Test:
```bash
python -m depthai_viewer
```

**USB Cameras:**
```bash
# List available cameras
ffmpeg -f avfoundation -list_devices true -i ""
```

### Step 8.5: Arm Setup

Verify LeRobot sees both arms:
```bash
python3 ~/.openclaw/skills/lerobot/scripts/arm.py ports
```

Home both arms:
```bash
python3 ~/.openclaw/skills/lerobot/scripts/arm.py home --type follower --port /dev/tty.usbmodemXXXX
```

### Step 8.6: Audio Setup

Test speaker:
```bash
say "Hello, I am Ren"
```

Test microphone (record and playback):
```bash
# Record
ffmpeg -f avfoundation -i ":0" -t 5 test_mic.wav
# Play
afplay test_mic.wav
```

### Step 8.7: Create System Test Script

```python
#!/usr/bin/env python3
"""Ren System Test - Run after assembly"""

import subprocess
import time

def test_motors():
    print("Testing motors...")
    # Send test commands via serial
    # Motors should spin briefly
    pass

def test_arms():
    print("Testing arms...")
    # Home each arm, do small movement
    pass

def test_cameras():
    print("Testing cameras...")
    # Capture frame from each camera
    pass

def test_head():
    print("Testing head pan-tilt...")
    # Sweep pan, then tilt
    pass

def test_display():
    print("Testing face display...")
    # Show test pattern
    pass

def test_audio():
    print("Testing audio...")
    subprocess.run(["say", "Audio test complete"])

def test_all():
    tests = [
        ("Motors", test_motors),
        ("Arms", test_arms),
        ("Cameras", test_cameras),
        ("Head", test_head),
        ("Display", test_display),
        ("Audio", test_audio),
    ]
    
    results = []
    for name, func in tests:
        try:
            func()
            results.append((name, "PASS"))
        except Exception as e:
            results.append((name, f"FAIL: {e}"))
    
    print("\n" + "="*40)
    print("TEST RESULTS")
    print("="*40)
    for name, result in results:
        print(f"  {name}: {result}")

if __name__ == "__main__":
    test_all()
```

---

## Testing & Calibration

### Motor Calibration

1. **Prop robot up** so tracks don't touch ground
2. **Test each motor:**
   - Forward command → wheel spins forward?
   - Speed control smooth?
3. **Test both together:**
   - Forward: both same direction/speed
   - Turn: differential speed
4. **On ground test:**
   - Straight line drive
   - Adjust trim if veering

### Arm Calibration

1. Run LeRobot calibration for each arm
2. Set joint limits to avoid body collision
3. Test workspace coverage

### Camera Calibration

1. OAK-D depth calibration (if needed)
2. Verify stereo alignment
3. Test depth at known distances

### Head Calibration

1. Find pan/tilt center positions
2. Set software limits
3. Tune acceleration for smooth movement

### Balance Check

1. Place robot on floor
2. Check for tipping tendency
3. Add ballast if unstable (mount in base)

---

## Troubleshooting

### Printing Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Warping | Bed adhesion | Use brim, increase bed temp |
| Layer separation | Temp too low | Increase nozzle temp 5-10°C |
| Stringing | Retraction | Tune retraction settings |
| Parts don't fit | Shrinkage | Scale up 0.5-1% or sand |
| Holes too small | Horizontal expansion | Drill out or adjust in slicer |

### Assembly Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Sections don't align | Warping/tolerance | Sand mating surfaces, use clamps |
| Inserts pull out | Not seated | Re-seat with more heat |
| Spine wobbles | Loose joints | Tighten connectors, check rods |
| Arms don't fit | Mount tolerance | Test print mount first |

### Motor Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| No spin | No power | Check battery, fuses, wiring |
| Wrong direction | Wiring | Swap motor leads |
| Jerky motion | PWM | Check driver, tune PWM frequency |
| Tracks slip | Tension | Adjust idler position |

### Electronics Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| No 5V | Buck converter | Check input, adjust pot |
| USB not detected | Power/cable | Try different port/cable |
| Servos jitter | Noise/power | Add capacitor, separate power |
| Interference | Grounding | Verify common ground |

---

## Maintenance Schedule

### Weekly
- [ ] Check track tension
- [ ] Inspect cable routing for wear
- [ ] Clean camera lenses
- [ ] Verify battery health

### Monthly
- [ ] Check all bolts for tightness
- [ ] Inspect printed parts for cracks
- [ ] Clean dust from electronics
- [ ] Backup configuration files

### As Needed
- [ ] Replace worn tracks
- [ ] Reprint damaged parts
- [ ] Update firmware/software
- [ ] Recalibrate if accuracy drifts

---

## Quick Reference

### Bolt Torque (approximate, for plastic)
- M3: Finger tight + 1/4 turn
- M4: Finger tight + 1/2 turn
- Don't overtighten! Plastic strips easily.

### Wire Colors (suggested standard)
- **Red:** +12V
- **Orange:** +5V
- **Black:** Ground
- **Blue:** Motor/servo signals
- **Green:** Sensor signals
- **White:** Data (I2C, serial)

### Emergency Stop
Always have a way to cut power quickly:
- Main switch accessible
- Consider adding E-stop button
- Know how to kill software

---

*Assembly guide version 2.0 (3D Printed) — 2026-02-04*
*Print well, build carefully, have fun!*
