# Ren Robot Body - Parts List

## Overview
Mobile robot platform with tracked base, articulated torso, dual SO-101 arms, and sensor head.

**Design specs:**
- Arm shoulder height: 34" (864mm) from ground
- Head height: 42" (1067mm) from ground  
- Work surface target: 30" (762mm) tables
- Compute: Mac Mini (M-series)

---

## 1. Mobile Base (Tracked)

### Drive System
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| Tracked chassis kit (ROB-14093 or similar) | 1 | $60-100 | ~300mm wide base, tank-style |
| DC gear motors (12V, 100-200 RPM, encoder) | 2 | $30-50 | Built into some kits |
| Motor driver (L298N or BTS7960) | 1 | $15-25 | Dual H-bridge, 20A+ |
| 12V LiPo battery (5000mAh+) | 1-2 | $40-80 | For drive system |
| Battery voltage monitor/cutoff | 1 | $10 | Protect LiPos |

### Base Structure
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| Aluminum sheet (2-3mm) for base plate | 1 | $20-30 | Or 3D print sections |
| Standoffs, screws, hardware | - | $15 | M3/M4 assortment |

**Base footprint target:** ~350mm L × 300mm W × 100mm H

---

## 2. Torso/Spine Assembly

### Structural
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| 2020 aluminum extrusion (500mm) | 2-3 | $15-25 | Vertical spine structure |
| 2020 corner brackets | 8 | $10 | 90° connections |
| 2020 T-nuts and bolts | Pack | $10 | M5 hardware |
| Shoulder cross-beam (2020 or plate) | 1 | $10 | Mount point for both arms |

**Alternative:** 3D printed spine with internal aluminum rod reinforcement

### Arm Mounting
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| SO-101 arm mounting brackets | 2 | $0 (print) | Custom fit to arm bases |
| Shoulder rotation servos (optional V2) | 2 | $40-60 | Add shoulder yaw DOF |

**Note:** SO-101 arms already owned - base is ~60mm mounting pattern

---

## 3. Head/Sensor Unit

### Pan-Tilt Mount
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| Pan-tilt bracket kit | 1 | $10-20 | SG90/MG90 style |
| MG996R servos (or similar) | 2 | $15-20 | Metal gear, higher torque |

### Cameras
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| OAK-D Lite (stereo depth) | 1 | $150 | Primary vision, depth sensing |
| Wide-angle USB camera (rear) | 1 | $20-30 | 170° FOV situational awareness |

**Alternative primary:** Intel RealSense D435i ($300) or Luxonis OAK-D Pro ($250)

### Face Display
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| 8×8 or 16×16 LED matrix (WS2812/NeoPixel) | 1-2 | $15-25 | Expression display |
| Small OLED (1.3" SSD1306) | 1 | $8-12 | Text/status display |

### Audio
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| Speaker (3W+ full range) | 1 | $10-15 | Voice output |
| Audio amplifier (PAM8403 or MAX98357A) | 1 | $5-10 | I2S or analog |
| USB microphone array (ReSpeaker or similar) | 1 | $30-60 | Directional/beamforming |

**Alternative mic option:** PlayStation Eye camera ($5-10 used) has decent 4-mic array

---

## 4. Compute & Electronics

### Main Computer
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| Mac Mini (already planned) | 1 | - | M2/M3/M4, 16GB+ RAM ideal |
| USB-C hub (powered) | 1 | $30-50 | Expand ports |

### Microcontroller (Low-level control)
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| Arduino Mega or ESP32 | 1 | $15-25 | Motor/servo coordination |
| PCA9685 servo driver | 1 | $8-12 | 16-channel PWM |
| Level shifters | 2 | $5 | 3.3V ↔ 5V |

### Power Distribution
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| 5V regulator (10A+ buck) | 1 | $15 | Servos, logic |
| 12V regulator (if needed) | 1 | $15 | From main battery |
| Power distribution board | 1 | $10 | Clean wiring |
| Main battery (14.8V 4S LiPo, 10000mAh) | 1 | $80-120 | Or 2× smaller in parallel |
| UPS/battery for Mac Mini | 1 | $50-80 | Clean shutdown capability |

---

## 5. Wiring & Connectors

| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| XT60 connectors | 10 | $10 | Main power |
| JST-XH connectors (servo) | 20 | $10 | |
| 14-18 AWG silicone wire (red/black) | 5m ea | $15 | Power |
| 22-26 AWG wire (assorted) | 10m | $10 | Signal |
| USB cables (various) | 5 | $20 | Cameras, hub, etc. |
| Heat shrink, cable ties, sleeving | - | $15 | Cable management |

---

## 6. 3D Printed Parts (Filament Cost)

| Part | Est. Filament | Notes |
|------|---------------|-------|
| Base covers/panels | 200g | PLA/PETG |
| Torso covers/cable routing | 150g | |
| Head housing | 100g | |
| Arm mounting brackets | 80g | PETG for strength |
| Camera mounts | 50g | |
| Display bezels | 30g | |
| **Total estimate** | ~600-800g | ~$15-20 in filament |

---

## 7. Existing Parts (Already Have)

| Part | Notes |
|------|-------|
| SO-101 Follower arm | marcus_agrippa_follower |
| SO-101 Leader arm (becomes 2nd follower) | marcus_agrippa_leader - may need recalibration |
| Bambu A1 3D printer | For printing body parts |

---

## Cost Summary

| Category | Estimated Cost |
|----------|----------------|
| Mobile Base | $150-250 |
| Torso/Spine | $50-75 |
| Head/Sensors | $200-300 |
| Audio | $45-85 |
| Compute & Electronics | $100-150 |
| Power System | $150-200 |
| Wiring & Misc | $50-80 |
| 3D Printing | $15-20 |
| **Total (excluding Mac Mini)** | **$760-1160** |

---

## Recommended Order of Acquisition

### Phase 1: Core Structure
1. Tracked chassis kit with motors
2. Aluminum extrusion + hardware
3. Motor driver
4. Basic battery for testing

### Phase 2: Sensing
1. OAK-D Lite or depth camera
2. Pan-tilt servos + bracket
3. LED matrix for face

### Phase 3: Integration
1. Power distribution
2. Arduino/ESP32 for low-level control
3. Wiring components
4. Print all structural parts

### Phase 4: Polish
1. Rear camera
2. UPS for Mac Mini
3. Final cable management

---

## Open Questions

- [ ] Exact tracked chassis selection (need stable platform ~15kg capacity)

## Design Decisions (Resolved)

- **Shoulder rotation:** Optional for V1 — SO-101 arms may have enough DOF. Revisit if needed.
- **Audio:** Yes — speaker + mic array for voice interaction
- **Tool holders:** None for V1 — grippers only

---

*Last updated: 2026-02-04*
