"""
Ren Robot Body - FreeCAD Parametric Model
==========================================
Open in FreeCAD: Macro > Macros > run this file
Or paste into Python console.

All dimensions in mm.
"""

import FreeCAD as App
import Part
from FreeCAD import Vector

# =============================================================================
# PARAMETERS - Adjust these to modify the design
# =============================================================================

# Overall dimensions
ARM_SHOULDER_HEIGHT = 864      # 34 inches from ground
HEAD_HEIGHT = 1067             # 42 inches from ground
TABLE_HEIGHT = 762             # 30 inches - target work surface

# Base (tracked platform)
BASE_LENGTH = 350              # Front to back
BASE_WIDTH = 300               # Side to side
BASE_HEIGHT = 80               # Track + chassis height

# Torso/spine
TORSO_WIDTH = 200              # Shoulder span for arms
TORSO_DEPTH = 100              # Front to back
SPINE_HEIGHT = ARM_SHOULDER_HEIGHT - BASE_HEIGHT  # Calculated

# Arm mounting
ARM_MOUNT_SPACING = 280        # Distance between arm centers (shoulder width)
ARM_MOUNT_WIDTH = 70           # Width of each arm mount plate
ARM_MOUNT_DEPTH = 70           # Depth of arm mount
ARM_MOUNT_THICKNESS = 8        # Plate thickness

# Head
HEAD_WIDTH = 100
HEAD_DEPTH = 80
HEAD_HEIGHT_SIZE = 70          # Size of head unit itself
NECK_HEIGHT = HEAD_HEIGHT - ARM_SHOULDER_HEIGHT - HEAD_HEIGHT_SIZE / 2

# Display cutout (face)
DISPLAY_WIDTH = 60
DISPLAY_HEIGHT = 40

# Extrusion profile (2020 aluminum)
EXTRUSION_SIZE = 20

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def make_box(name, length, width, height, pos=(0, 0, 0)):
    """Create a box shape at position."""
    box = Part.makeBox(length, width, height, Vector(*pos))
    return box

def make_rounded_box(name, length, width, height, radius, pos=(0, 0, 0)):
    """Create a box with rounded vertical edges."""
    # Simple approximation - actual rounded box would use fillet
    box = Part.makeBox(length, width, height, Vector(*pos))
    return box

def make_extrusion(length, pos=(0, 0, 0), vertical=True):
    """Create a 2020 extrusion profile."""
    if vertical:
        box = Part.makeBox(EXTRUSION_SIZE, EXTRUSION_SIZE, length, Vector(*pos))
    else:
        box = Part.makeBox(length, EXTRUSION_SIZE, EXTRUSION_SIZE, Vector(*pos))
    return box

# =============================================================================
# BUILD THE MODEL
# =============================================================================

def build_robot():
    # Create new document
    if App.ActiveDocument:
        doc = App.ActiveDocument
    else:
        doc = App.newDocument("RenBody")
    
    parts = []
    
    # -------------------------------------------------------------------------
    # 1. BASE PLATFORM
    # -------------------------------------------------------------------------
    
    # Main base plate
    base_x = -BASE_LENGTH / 2
    base_y = -BASE_WIDTH / 2
    base = make_box("Base", BASE_LENGTH, BASE_WIDTH, BASE_HEIGHT, 
                    (base_x, base_y, 0))
    
    # Track representations (left and right)
    track_width = 60
    track_height = 40
    
    left_track = make_box("LeftTrack", BASE_LENGTH + 20, track_width, track_height,
                          (base_x - 10, -BASE_WIDTH/2 - track_width, 20))
    
    right_track = make_box("RightTrack", BASE_LENGTH + 20, track_width, track_height,
                           (base_x - 10, BASE_WIDTH/2, 20))
    
    # Combine base
    base_assembly = base.fuse(left_track).fuse(right_track)
    parts.append(("Base_Assembly", base_assembly))
    
    # -------------------------------------------------------------------------
    # 2. TORSO / SPINE
    # -------------------------------------------------------------------------
    
    # Vertical extrusions (4 corners of torso)
    spine_z_start = BASE_HEIGHT
    
    # Four corner uprights
    offset = TORSO_WIDTH / 2 - EXTRUSION_SIZE
    
    spine_fl = make_extrusion(SPINE_HEIGHT, 
                               (-TORSO_DEPTH/2, -offset, spine_z_start))
    spine_fr = make_extrusion(SPINE_HEIGHT,
                               (-TORSO_DEPTH/2, offset, spine_z_start))
    spine_bl = make_extrusion(SPINE_HEIGHT,
                               (TORSO_DEPTH/2 - EXTRUSION_SIZE, -offset, spine_z_start))
    spine_br = make_extrusion(SPINE_HEIGHT,
                               (TORSO_DEPTH/2 - EXTRUSION_SIZE, offset, spine_z_start))
    
    spine_assembly = spine_fl.fuse(spine_fr).fuse(spine_bl).fuse(spine_br)
    
    # Cross beams at shoulder level
    shoulder_z = ARM_SHOULDER_HEIGHT - EXTRUSION_SIZE
    
    # Front and back horizontal beams
    front_beam = Part.makeBox(EXTRUSION_SIZE, TORSO_WIDTH - EXTRUSION_SIZE * 2, 
                              EXTRUSION_SIZE,
                              Vector(-TORSO_DEPTH/2, -TORSO_WIDTH/2 + EXTRUSION_SIZE, shoulder_z))
    
    back_beam = Part.makeBox(EXTRUSION_SIZE, TORSO_WIDTH - EXTRUSION_SIZE * 2,
                             EXTRUSION_SIZE,
                             Vector(TORSO_DEPTH/2 - EXTRUSION_SIZE, -TORSO_WIDTH/2 + EXTRUSION_SIZE, shoulder_z))
    
    # Side beams (for arm mounting)
    left_beam = Part.makeBox(TORSO_DEPTH - EXTRUSION_SIZE * 2, EXTRUSION_SIZE,
                             EXTRUSION_SIZE,
                             Vector(-TORSO_DEPTH/2 + EXTRUSION_SIZE, -TORSO_WIDTH/2, shoulder_z))
    
    right_beam = Part.makeBox(TORSO_DEPTH - EXTRUSION_SIZE * 2, EXTRUSION_SIZE,
                              EXTRUSION_SIZE,
                              Vector(-TORSO_DEPTH/2 + EXTRUSION_SIZE, TORSO_WIDTH/2 - EXTRUSION_SIZE, shoulder_z))
    
    spine_assembly = spine_assembly.fuse(front_beam).fuse(back_beam)
    spine_assembly = spine_assembly.fuse(left_beam).fuse(right_beam)
    
    # Add mid-height cross bracing
    mid_z = BASE_HEIGHT + SPINE_HEIGHT / 2
    
    mid_front = Part.makeBox(EXTRUSION_SIZE, TORSO_WIDTH - EXTRUSION_SIZE * 2,
                             EXTRUSION_SIZE,
                             Vector(-TORSO_DEPTH/2, -TORSO_WIDTH/2 + EXTRUSION_SIZE, mid_z))
    mid_back = Part.makeBox(EXTRUSION_SIZE, TORSO_WIDTH - EXTRUSION_SIZE * 2,
                            EXTRUSION_SIZE,
                            Vector(TORSO_DEPTH/2 - EXTRUSION_SIZE, -TORSO_WIDTH/2 + EXTRUSION_SIZE, mid_z))
    
    spine_assembly = spine_assembly.fuse(mid_front).fuse(mid_back)
    parts.append(("Torso_Frame", spine_assembly))
    
    # -------------------------------------------------------------------------
    # 3. ARM MOUNTS
    # -------------------------------------------------------------------------
    
    arm_mount_z = ARM_SHOULDER_HEIGHT
    
    # Left arm mount plate
    left_arm_mount = make_box("LeftArmMount", 
                              ARM_MOUNT_DEPTH, ARM_MOUNT_WIDTH, ARM_MOUNT_THICKNESS,
                              (-ARM_MOUNT_DEPTH/2, -ARM_MOUNT_SPACING/2 - ARM_MOUNT_WIDTH/2, arm_mount_z))
    
    # Right arm mount plate
    right_arm_mount = make_box("RightArmMount",
                               ARM_MOUNT_DEPTH, ARM_MOUNT_WIDTH, ARM_MOUNT_THICKNESS,
                               (-ARM_MOUNT_DEPTH/2, ARM_MOUNT_SPACING/2 - ARM_MOUNT_WIDTH/2, arm_mount_z))
    
    arm_mounts = left_arm_mount.fuse(right_arm_mount)
    parts.append(("Arm_Mounts", arm_mounts))
    
    # -------------------------------------------------------------------------
    # 4. ARM PLACEHOLDERS (SO-101 rough shape)
    # -------------------------------------------------------------------------
    
    # Simplified arm representation (cylinder + boxes)
    arm_length = 300  # Approximate SO-101 reach
    arm_width = 50
    
    # Left arm (pointing outward initially for visibility)
    left_arm_base = Part.makeCylinder(30, 40, 
                                       Vector(-ARM_MOUNT_DEPTH/4, -ARM_MOUNT_SPACING/2, arm_mount_z + ARM_MOUNT_THICKNESS))
    left_arm_segment = Part.makeBox(arm_width, arm_width, arm_length,
                                     Vector(-arm_width/2, -ARM_MOUNT_SPACING/2 - arm_width/2, 
                                           arm_mount_z + ARM_MOUNT_THICKNESS + 30))
    left_arm = left_arm_base.fuse(left_arm_segment)
    
    # Right arm
    right_arm_base = Part.makeCylinder(30, 40,
                                        Vector(-ARM_MOUNT_DEPTH/4, ARM_MOUNT_SPACING/2, arm_mount_z + ARM_MOUNT_THICKNESS))
    right_arm_segment = Part.makeBox(arm_width, arm_width, arm_length,
                                      Vector(-arm_width/2, ARM_MOUNT_SPACING/2 - arm_width/2,
                                            arm_mount_z + ARM_MOUNT_THICKNESS + 30))
    right_arm = right_arm_base.fuse(right_arm_segment)
    
    arms = left_arm.fuse(right_arm)
    parts.append(("Arms_Placeholder", arms))
    
    # -------------------------------------------------------------------------
    # 5. HEAD / SENSOR UNIT
    # -------------------------------------------------------------------------
    
    # Neck (vertical post from shoulders to head)
    neck = Part.makeCylinder(15, NECK_HEIGHT,
                             Vector(0, 0, ARM_SHOULDER_HEIGHT))
    parts.append(("Neck", neck))
    
    # Head body
    head_z = HEAD_HEIGHT - HEAD_HEIGHT_SIZE
    head = make_box("Head", HEAD_DEPTH, HEAD_WIDTH, HEAD_HEIGHT_SIZE,
                    (-HEAD_DEPTH/2, -HEAD_WIDTH/2, head_z))
    
    # Face display cutout (front face)
    display_cutout = make_box("DisplayCutout", 10, DISPLAY_WIDTH, DISPLAY_HEIGHT,
                              (-HEAD_DEPTH/2 - 1, -DISPLAY_WIDTH/2, head_z + 15))
    
    head = head.cut(display_cutout)
    
    # Camera "eyes" (two cylinders)
    eye_spacing = 50
    eye_radius = 12
    left_eye = Part.makeCylinder(eye_radius, 15,
                                  Vector(-HEAD_DEPTH/2, -eye_spacing/2, head_z + HEAD_HEIGHT_SIZE - 20),
                                  Vector(-1, 0, 0))
    right_eye = Part.makeCylinder(eye_radius, 15,
                                   Vector(-HEAD_DEPTH/2, eye_spacing/2, head_z + HEAD_HEIGHT_SIZE - 20),
                                   Vector(-1, 0, 0))
    
    head = head.fuse(left_eye).fuse(right_eye)
    parts.append(("Head", head))
    
    # -------------------------------------------------------------------------
    # 6. ELECTRONICS BAY INDICATOR (inside base)
    # -------------------------------------------------------------------------
    
    # Mac Mini placeholder (actual size: 197 x 197 x 35.8 mm)
    mac_mini = make_box("MacMini", 197, 197, 36,
                        (-197/2, -197/2, 5))
    parts.append(("MacMini_Placeholder", mac_mini))
    
    # -------------------------------------------------------------------------
    # CREATE FREECAD OBJECTS
    # -------------------------------------------------------------------------
    
    colors = {
        "Base_Assembly": (0.3, 0.3, 0.3),      # Dark gray
        "Torso_Frame": (0.7, 0.7, 0.7),         # Silver (aluminum)
        "Arm_Mounts": (0.2, 0.2, 0.8),          # Blue
        "Arms_Placeholder": (0.8, 0.4, 0.0),    # Orange
        "Neck": (0.5, 0.5, 0.5),                # Gray
        "Head": (0.9, 0.9, 0.9),                # Light gray
        "MacMini_Placeholder": (0.8, 0.8, 0.8), # Silver
    }
    
    for name, shape in parts:
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        if name in colors:
            obj.ViewObject.ShapeColor = colors[name]
    
    doc.recompute()
    
    # Set view
    if App.GuiUp:
        import FreeCADGui
        FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
        FreeCADGui.SendMsgToActiveView("ViewFit")
    
    print("=" * 60)
    print("REN ROBOT BODY MODEL GENERATED")
    print("=" * 60)
    print(f"Total height: {HEAD_HEIGHT}mm ({HEAD_HEIGHT/25.4:.1f} inches)")
    print(f"Shoulder height: {ARM_SHOULDER_HEIGHT}mm ({ARM_SHOULDER_HEIGHT/25.4:.1f} inches)")
    print(f"Base footprint: {BASE_LENGTH}x{BASE_WIDTH}mm")
    print(f"Arm spacing: {ARM_MOUNT_SPACING}mm")
    print("=" * 60)
    
    return doc

# Run if executed directly
if __name__ == "__main__" or App.ActiveDocument is not None:
    build_robot()
