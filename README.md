# Ren Robot Body

Physical robot body design for the Ren AI assistant.

## Design Philosophy

- **Tracked mobile base** for stability and terrain handling (wheels/legs as future upgrade)
- **Articulated upper body** with dual SO-101 arms
- **Sensor head** with stereo depth camera and expression display
- **Mac Mini compute** for running the AI locally

## Quick Start (Blender)

1. Open Blender
2. Go to **Scripting** tab (top menu bar)
3. Click **Open** and select `ren_body_blender.py`
4. Click **Run Script** (▶ button)
5. Switch to **Layout** tab to view model
6. Set viewport shading to **Material Preview** for colors

## Quick Start (FreeCAD)

1. Open FreeCAD
2. Go to **Macro → Macros → Browse** and select `ren_body.py`
3. Run the macro to generate the parametric model
4. Adjust parameters at the top of the script to modify dimensions

## Files

| File | Description |
|------|-------------|
| `README.md` | This file |
| `PARTS_LIST.md` | Bill of materials with costs |
| `ASSEMBLY_GUIDE.md` | Step-by-step build instructions |
| `ren_body.py` | FreeCAD Python macro for parametric model |
| `ren_body_blender.py` | Blender Python script for 3D model |

## Key Dimensions

| Measurement | Value |
|-------------|-------|
| Total height | 42" (1067mm) |
| Arm shoulder height | 34" (864mm) |
| Base footprint | 350mm × 300mm |
| Shoulder width | 280mm |

## Status

- [x] Initial design concept
- [x] Parts list draft
- [x] Basic FreeCAD model
- [ ] Detailed arm mounts (SO-101 specific)
- [ ] Track system selection
- [ ] Wiring routing
- [ ] Detailed head assembly
- [ ] Printable STL export

## Existing Hardware

- 2× SO-101 arms (marcus_agrippa_follower, marcus_agrippa_leader)
- Bambu A1 for 3D printing
- Mac Mini (planned compute)

---

*Project started: 2026-02-04*
