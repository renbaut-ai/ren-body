# Ren Robot Body - Parts List (3D Printed Version)

## Overview
Maximizing 3D printed parts, minimizing purchased components.

**Design specs:**
- Arm shoulder height: 34" (864mm) from ground
- Head height: 42" (1067mm) from ground
- Compute: Mac Mini (M-series)
- **Build volume constraint:** Bambu A1 = 256 × 256 × 256 mm

---

## 1. 3D Printed Structure

All printed parts designed modular to fit 256mm build volume.

### Base Chassis
| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Base frame sections | 4-6 | PETG (grey) | Bolt together, ~350×300mm assembled |
| Motor mounts | 2 | PETG (grey) | Integrated into base |
| Battery tray | 1 | PETG (grey) | Removable for charging |
| Electronics bay | 1 | PETG (grey) | Mac Mini mount + wiring space |
| Base cover panels | 3-4 | PLA (grey/blue) | Top/sides, cosmetic |
| Ballast mounting plate | 1 | PETG (grey) | Optional, bolt-in weights |

### Drive System (Printed + Purchased)
| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Track sprockets/drive wheels | 4-6 | PETG (grey) | Sized to match purchased tracks |
| Sprocket hubs | 2 | PETG (grey) | Motor shaft adapters |
| Idler wheel mounts | 2 | PETG (grey) | Adjustable for track tension |

**Tracks purchased separately** — rubber tank tracks (see Hardware section)

### Torso Frame
| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Spine sections | 4 | PETG (grey) | Stack vertically, ~200mm each |
| Spine connectors | 3 | PETG (grey) | Join spine sections |
| Reinforcement rods | 4 | Steel/aluminum rod | 8mm × 800mm, internal to spine |
| Cross braces | 3 | PETG (grey) | Front/rear at different heights |
| Shoulder platform | 2 | PETG (blue) | Left/right halves, accent color |

### Arm Mounts
| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Arm mount brackets | 2 | PETG (blue) | SO-101 specific fit |
| Shoulder accent panels | 2 | PLA (blue) | Cosmetic covers |

### Head
| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Head shell (front) | 1 | PETG (white) | Face with display cutout |
| Head shell (rear) | 1 | PETG (grey) | Camera mount integrated |
| Display bezel | 1 | PLA (white) | Frame for LED matrix |
| Eye surrounds | 2 | PLA (red) | Camera accent rings |
| Neck tube | 1 | PETG (grey) | Or aluminum tube |
| Pan-tilt mount | 1 | PETG (grey) | Servo bracket |

### Cable Management
| Part | Qty | Material | Notes |
|------|-----|----------|-------|
| Cable clips | 20+ | PLA (grey) | Snap-fit to frame |
| Wire channels | 6 | PLA (grey) | Route through spine |

---

## 2. Filament & Color Scheme

**Available:** Grey (full), Blue (full), White (~7/8), Red (~7/8)

| Color | Use | Est. Amount |
|-------|-----|-------------|
| **Grey** | Base frame, spine, motor mounts, structural | ~1.5-2 kg |
| **Blue** | Arm mounts, shoulder plates, accent panels | ~0.5-0.7 kg |
| **White** | Head shell, face area, display bezel | ~0.3-0.4 kg |
| **Red** | Status indicators, small accents, highlights | ~0.1 kg |
| **Total** | | **~2.5-3.2 kg** |

**Color vibe:** Industrial grey chassis, blue accents on upper body, white face for contrast, red pops for personality.

*No new filament purchase needed if current spools have enough.*

---

## 3. Hardware (Must Buy)

### Drive System
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| DC gear motors (12V, 100-200 RPM, encoder) | 2 | $25-40 | 25mm gearbox style |
| Motor driver (L298N or BTS7960) | 1 | $10-20 | |
| Rubber tank tracks | 2 | $20-40 | Match to sprocket size (e.g., 60mm-80mm width) |

### Reinforcement
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| Steel/aluminum rods (8mm × 1m) | 4 | $15-20 | Cut to length |
| Threaded inserts (M3) | 50 | $8 | Heat-set brass inserts |
| Threaded inserts (M4) | 20 | $5 | For larger bolts |
| Bolts/nuts assortment (M3, M4) | 1 kit | $15 | |

### Head/Sensors
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| OAK-D Lite (stereo depth) | 1 | $150 | Primary vision |
| Wide-angle USB camera | 1 | $20-30 | Rear awareness |
| MG996R servos (pan-tilt) | 2 | $15-20 | |
| 8×8 or 16×16 LED matrix | 1 | $15-20 | Face display |

### Audio
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| Speaker (3W+) | 1 | $10-15 | |
| Amplifier board | 1 | $5-10 | |
| USB mic array | 1 | $30-60 | Or PS Eye $5-10 |

### Electronics
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| Arduino Mega or ESP32 | 1 | $15-25 | Low-level control |
| PCA9685 servo driver | 1 | $8-12 | |
| USB hub (powered) | 1 | $30 | |
| Level shifters | 2 | $5 | |

### Power
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| 12V LiPo (5000mAh+) | 1-2 | $40-60 | Drive + logic |
| 5V buck converter (10A) | 1 | $12-15 | |
| XT60 connectors | 6 | $8 | |
| Power switch | 1 | $5 | |
| Voltage monitor | 1 | $5 | |

### Wiring
| Part | Qty | Est. Cost | Notes |
|------|-----|-----------|-------|
| Silicone wire (14-22 AWG) | - | $15 | Assorted |
| Connectors (JST, Dupont) | - | $10 | |
| Heat shrink | - | $5 | |

---

## 4. Existing Parts (Already Have)

| Part | Notes |
|------|-------|
| SO-101 arms (×2) | Left + Right arms |
| Bambu A1 printer | For all printed parts |
| Mac Mini (planned) | Main compute |

---

## 5. Cost Summary (Printed Version)

| Category | Estimated Cost |
|----------|----------------|
| 3D Printing (filament) | $0* |
| Drive system (motors + tracks) | $55-100 |
| Reinforcement hardware | $45-50 |
| Head/Sensors | $200-280 |
| Audio | $45-85 |
| Electronics | $60-75 |
| Power system | $70-95 |
| Wiring | $30 |
| **Total (excluding Mac Mini)** | **$505-715** |

*\*Using existing filament supply*

**Savings vs aluminum frame version:** ~$250-450

---

## 6. Print Time Estimate

| Category | Est. Print Time |
|----------|-----------------|
| Base sections | 20-30 hours |
| Torso/spine | 25-35 hours |
| Head | 8-12 hours |
| Mounts & brackets | 10-15 hours |
| Covers & cosmetic | 10-15 hours |
| **Total** | **~75-110 hours** |

(Split across multiple prints over 1-2 weeks)

---

## 7. Design Priorities for Printability

1. **Modular sections** — nothing larger than 250mm in any dimension
2. **Minimal supports** — orient parts to print flat where possible
3. **Bolt-together assembly** — heat-set inserts for repeated disassembly
4. **Rod reinforcement** — vertical spine needs internal metal rods
5. **Parametric design** — easy to adjust if fit is off

---

## 8. Design Notes

**Ballast:** Optional mounting points included in base design. Mac Mini (~1.2kg) + motors (~0.5kg) + battery (~0.5-1kg) = ~2.5-3.5kg low in the chassis should provide decent stability. Can add lead weights or steel plates later if tippy.

**Resolved:**
- ✅ Tracks: Rubber (purchased), not printed
- ✅ Colors: Grey primary, blue accent, white face, red highlights
- ✅ Ballast: Mount points included, probably not needed initially

---

*Last updated: 2026-02-04*
