"""
Ren Robot Body - Blender Parametric Model (Printable Version)
==============================================================
Open Blender, go to Scripting tab, open this file, and click Run Script.

All parts designed for 256mm x 256mm x 256mm print volume (Bambu A1).
Parts organized into collections by print batch.

Color Scheme:
- Grey: Structural (base, spine, mounts)
- Blue: Accents (shoulders, arm mounts)
- White: Face/head front
- Red: Highlights (eye rings)
"""

import bpy
import math
from mathutils import Vector

# =============================================================================
# PARAMETERS (in mm, converted to meters for Blender)
# =============================================================================

def mm(val):
    """Convert mm to meters."""
    return val / 1000

# Print volume constraint
MAX_PRINT_DIM = mm(250)  # Slightly under 256 for safety margin

# Overall dimensions
ARM_SHOULDER_HEIGHT = mm(864)    # 34 inches
HEAD_HEIGHT = mm(1067)           # 42 inches
TABLE_HEIGHT = mm(762)           # 30 inches

# Base
BASE_LENGTH = mm(350)
BASE_WIDTH = mm(300)
BASE_HEIGHT = mm(80)

# Torso
TORSO_WIDTH = mm(200)
TORSO_DEPTH = mm(100)
SPINE_SECTION_HEIGHT = mm(200)   # Each printable section
NUM_SPINE_SECTIONS = 4
SPINE_HEIGHT = SPINE_SECTION_HEIGHT * NUM_SPINE_SECTIONS

# Arms
ARM_MOUNT_SPACING = mm(280)
ARM_MOUNT_WIDTH = mm(70)
ARM_MOUNT_DEPTH = mm(70)
ARM_MOUNT_THICKNESS = mm(10)

# Head
HEAD_WIDTH = mm(100)
HEAD_DEPTH = mm(80)
HEAD_HEIGHT_SIZE = mm(70)
NECK_HEIGHT = HEAD_HEIGHT - ARM_SHOULDER_HEIGHT - HEAD_HEIGHT_SIZE / 2
NECK_RADIUS = mm(20)
NECK_WALL = mm(4)

# Display
DISPLAY_WIDTH = mm(64)   # 8x8 LED matrix ~64mm
DISPLAY_HEIGHT = mm(64)

# Cameras
EYE_RADIUS = mm(15)
EYE_DEPTH = mm(20)
EYE_SPACING = mm(50)
EYE_RING_THICKNESS = mm(3)

# Tracks
TRACK_WIDTH = mm(60)
SPROCKET_RADIUS = mm(40)
SPROCKET_THICKNESS = mm(15)

# Reinforcement
ROD_DIAMETER = mm(8)
ROD_HOLE_DIAMETER = mm(8.5)  # Slightly larger for fit

# Wall thickness for printed parts
WALL_THICKNESS = mm(4)

# =============================================================================
# COLORS (RGBA)
# =============================================================================

COLOR_GREY = (0.35, 0.35, 0.38, 1.0)       # Structural grey
COLOR_BLUE = (0.2, 0.4, 0.8, 1.0)          # Accent blue
COLOR_WHITE = (0.92, 0.92, 0.92, 1.0)      # Face white
COLOR_RED = (0.85, 0.15, 0.15, 1.0)        # Highlight red
COLOR_DARK = (0.1, 0.1, 0.1, 1.0)          # Black (displays, cameras)
COLOR_ORANGE = (0.9, 0.45, 0.1, 1.0)       # SO-101 arms
COLOR_SILVER = (0.75, 0.75, 0.78, 1.0)     # Metal parts

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def clear_scene():
    """Remove all mesh objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

def create_collection(name):
    """Create and link a new collection."""
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def move_to_collection(obj, collection):
    """Move object to collection."""
    for col in obj.users_collection:
        col.objects.unlink(obj)
    collection.objects.link(obj)

def set_material(obj, color, name=None):
    """Apply a simple material with color."""
    mat_name = name or f"{obj.name}_mat"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.5
    obj.data.materials.append(mat)

def create_box(name, size, location, color):
    """Create a box with material."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    set_material(obj, color)
    return obj

def create_cylinder(name, radius, depth, location, color, rotation=(0,0,0)):
    """Create a cylinder with material."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, 
        location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    set_material(obj, color)
    return obj

def create_hollow_cylinder(name, outer_r, inner_r, depth, location, color, rotation=(0,0,0)):
    """Create a hollow cylinder (tube)."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=outer_r, depth=depth,
        location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    
    # Add inner cut using boolean (simplified - just visual)
    # For actual printing, would need proper boolean
    set_material(obj, color)
    return obj

# =============================================================================
# PRINTABLE PART GENERATORS
# =============================================================================

def create_base_section(name, index, total, collection):
    """Create one section of the base frame."""
    section_length = BASE_LENGTH / 2  # 2 sections front-to-back
    section_width = BASE_WIDTH / 2    # 2 sections left-to-right
    
    # Calculate position
    x_offset = (index % 2 - 0.5) * section_length
    y_offset = (index // 2 - 0.5) * section_width
    
    # Main section body
    obj = create_box(
        f"{name}_{index+1}",
        (section_length - mm(2), section_width - mm(2), BASE_HEIGHT),
        (x_offset, y_offset, BASE_HEIGHT/2),
        COLOR_GREY
    )
    move_to_collection(obj, collection)
    
    return obj

def create_spine_section(name, index, collection):
    """Create one section of the spine."""
    z_pos = BASE_HEIGHT + SPINE_SECTION_HEIGHT * index + SPINE_SECTION_HEIGHT/2
    
    # Hollow rectangular tube
    outer_w = TORSO_DEPTH
    outer_d = mm(60)
    inner_w = outer_w - WALL_THICKNESS * 2
    inner_d = outer_d - WALL_THICKNESS * 2
    
    obj = create_box(
        f"{name}_{index+1}",
        (outer_w, outer_d, SPINE_SECTION_HEIGHT),
        (0, 0, z_pos),
        COLOR_GREY
    )
    move_to_collection(obj, collection)
    
    # Add rod channel indicators (small cylinders at corners)
    rod_offset = mm(20)
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        rod = create_cylinder(
            f"{name}_{index+1}_rod_{dx}_{dy}",
            ROD_HOLE_DIAMETER/2,
            SPINE_SECTION_HEIGHT + mm(2),
            (dx * rod_offset, dy * rod_offset, z_pos),
            COLOR_DARK
        )
        move_to_collection(rod, collection)
    
    return obj

def create_cross_brace(name, z_height, collection):
    """Create a cross brace at specified height."""
    brace = create_box(
        name,
        (TORSO_DEPTH + mm(40), TORSO_WIDTH, mm(20)),
        (0, 0, z_height),
        COLOR_GREY
    )
    move_to_collection(brace, collection)
    return brace

def create_shoulder_plate(name, side, collection):
    """Create shoulder plate (left or right)."""
    y_pos = side * (TORSO_WIDTH/2 - mm(20))
    
    plate = create_box(
        name,
        (TORSO_DEPTH + mm(60), mm(80), mm(15)),
        (0, y_pos, ARM_SHOULDER_HEIGHT - mm(7)),
        COLOR_BLUE
    )
    move_to_collection(plate, collection)
    return plate

def create_arm_mount(name, side, collection):
    """Create arm mounting bracket."""
    y_pos = side * ARM_MOUNT_SPACING/2
    
    mount = create_box(
        name,
        (ARM_MOUNT_DEPTH, ARM_MOUNT_WIDTH, ARM_MOUNT_THICKNESS),
        (0, y_pos, ARM_SHOULDER_HEIGHT + ARM_MOUNT_THICKNESS/2),
        COLOR_BLUE
    )
    move_to_collection(mount, collection)
    return mount

def create_sprocket(name, side, front, collection):
    """Create track sprocket."""
    x_pos = (1 if front else -1) * (BASE_LENGTH/2 - SPROCKET_RADIUS)
    y_pos = side * (BASE_WIDTH/2 + TRACK_WIDTH/2)
    
    sprocket = create_cylinder(
        name,
        SPROCKET_RADIUS,
        SPROCKET_THICKNESS,
        (x_pos, y_pos, SPROCKET_RADIUS + mm(10)),
        COLOR_GREY,
        rotation=(math.pi/2, 0, 0)
    )
    move_to_collection(sprocket, collection)
    
    # Hub
    hub = create_cylinder(
        f"{name}_hub",
        SPROCKET_RADIUS * 0.4,
        SPROCKET_THICKNESS + mm(10),
        (x_pos, y_pos, SPROCKET_RADIUS + mm(10)),
        COLOR_DARK,
        rotation=(math.pi/2, 0, 0)
    )
    move_to_collection(hub, collection)
    
    return sprocket

def create_head_front(collection):
    """Create front head shell (white face)."""
    head_z = HEAD_HEIGHT - HEAD_HEIGHT_SIZE/2
    
    # Main face plate
    face = create_box(
        "Head_Front",
        (WALL_THICKNESS * 2, HEAD_WIDTH, HEAD_HEIGHT_SIZE),
        (-HEAD_DEPTH/2 + WALL_THICKNESS, 0, head_z),
        COLOR_WHITE
    )
    move_to_collection(face, collection)
    
    # Display area (black inset)
    display = create_box(
        "Display_Area",
        (mm(5), DISPLAY_WIDTH, DISPLAY_HEIGHT),
        (-HEAD_DEPTH/2, 0, head_z - mm(5)),
        COLOR_DARK
    )
    move_to_collection(display, collection)
    
    return face

def create_head_rear(collection):
    """Create rear head shell (grey)."""
    head_z = HEAD_HEIGHT - HEAD_HEIGHT_SIZE/2
    
    rear = create_box(
        "Head_Rear",
        (HEAD_DEPTH - WALL_THICKNESS * 2, HEAD_WIDTH, HEAD_HEIGHT_SIZE),
        (WALL_THICKNESS, 0, head_z),
        COLOR_GREY
    )
    move_to_collection(rear, collection)
    
    return rear

def create_eye_ring(name, side, collection):
    """Create red camera eye ring."""
    head_z = HEAD_HEIGHT - HEAD_HEIGHT_SIZE/2
    eye_z = head_z + HEAD_HEIGHT_SIZE/2 - mm(20)
    y_pos = side * EYE_SPACING/2
    
    # Outer ring
    ring = create_cylinder(
        name,
        EYE_RADIUS + EYE_RING_THICKNESS,
        mm(8),
        (-HEAD_DEPTH/2 - mm(3), y_pos, eye_z),
        COLOR_RED,
        rotation=(0, math.pi/2, 0)
    )
    move_to_collection(ring, collection)
    
    # Camera lens (black center)
    lens = create_cylinder(
        f"{name}_lens",
        EYE_RADIUS,
        mm(10),
        (-HEAD_DEPTH/2 - mm(5), y_pos, eye_z),
        COLOR_DARK,
        rotation=(0, math.pi/2, 0)
    )
    move_to_collection(lens, collection)
    
    return ring

def create_neck(collection):
    """Create neck tube."""
    neck_z = ARM_SHOULDER_HEIGHT + NECK_HEIGHT/2
    
    neck = create_hollow_cylinder(
        "Neck_Tube",
        NECK_RADIUS, NECK_RADIUS - NECK_WALL,
        NECK_HEIGHT,
        (0, 0, neck_z),
        COLOR_GREY
    )
    move_to_collection(neck, collection)
    
    return neck

def create_arm_placeholder(name, side, collection):
    """Create SO-101 arm placeholder (not printed - reference only)."""
    y_pos = side * ARM_MOUNT_SPACING/2
    base_z = ARM_SHOULDER_HEIGHT + ARM_MOUNT_THICKNESS + mm(20)
    
    # Base
    base = create_cylinder(
        f"{name}_base",
        mm(35), mm(50),
        (0, y_pos, base_z),
        COLOR_ORANGE
    )
    move_to_collection(base, collection)
    
    # Upper arm
    upper = create_box(
        f"{name}_upper",
        (mm(45), mm(45), mm(150)),
        (0, y_pos, base_z + mm(100)),
        COLOR_ORANGE
    )
    move_to_collection(upper, collection)
    
    # Forearm (angled out for visibility)
    forearm = create_box(
        f"{name}_forearm",
        (mm(40), mm(40), mm(130)),
        (0, y_pos + side * mm(40), base_z + mm(220)),
        COLOR_ORANGE
    )
    move_to_collection(forearm, collection)
    
    # Gripper
    gripper = create_box(
        f"{name}_gripper",
        (mm(30), mm(50), mm(40)),
        (0, y_pos + side * mm(40), base_z + mm(300)),
        COLOR_DARK
    )
    move_to_collection(gripper, collection)
    
    return base

def create_mac_mini(collection):
    """Mac Mini placeholder (reference)."""
    mac = create_box(
        "Mac_Mini_Ref",
        (mm(197), mm(197), mm(36)),
        (0, 0, mm(5) + mm(18)),
        COLOR_SILVER
    )
    move_to_collection(mac, collection)
    return mac

def create_motor(name, side, collection):
    """Motor placeholder."""
    y_pos = side * (BASE_WIDTH/2 - mm(30))
    
    motor = create_cylinder(
        name,
        mm(18), mm(60),
        (-BASE_LENGTH/4, y_pos, mm(40)),
        COLOR_DARK,
        rotation=(math.pi/2, 0, 0)
    )
    move_to_collection(motor, collection)
    
    # Gearbox
    gear = create_box(
        f"{name}_gear",
        (mm(25), mm(40), mm(25)),
        (-BASE_LENGTH/4, y_pos + side * mm(35), mm(40)),
        COLOR_SILVER
    )
    move_to_collection(gear, collection)
    
    return motor

# =============================================================================
# MAIN BUILD FUNCTION
# =============================================================================

def build_robot():
    """Build the complete robot model."""
    
    # Clear scene
    clear_scene()
    
    # Create collections organized by print batch
    col_base_print = create_collection("01_Print_Base_Grey")
    col_spine_print = create_collection("02_Print_Spine_Grey")
    col_shoulders_print = create_collection("03_Print_Shoulders_Blue")
    col_head_white = create_collection("04_Print_Head_White")
    col_head_grey = create_collection("05_Print_Head_Grey")
    col_accents_red = create_collection("06_Print_Accents_Red")
    col_hardware = create_collection("07_Reference_Hardware")
    col_arms = create_collection("08_Reference_Arms")
    
    print("Building Ren robot body...")
    
    # =========================================================================
    # BASE (Grey) - Print Batch 1
    # =========================================================================
    print("  Creating base sections...")
    
    for i in range(4):
        create_base_section("Base_Section", i, 4, col_base_print)
    
    # Sprockets (4 total - front/rear, left/right)
    for side_name, side in [("L", -1), ("R", 1)]:
        for pos_name, front in [("Front", True), ("Rear", False)]:
            create_sprocket(f"Sprocket_{side_name}_{pos_name}", side, front, col_base_print)
    
    # Motor mounts integrated into base
    create_motor("Motor_Left", -1, col_hardware)
    create_motor("Motor_Right", 1, col_hardware)
    
    # =========================================================================
    # SPINE (Grey) - Print Batch 2
    # =========================================================================
    print("  Creating spine sections...")
    
    for i in range(NUM_SPINE_SECTIONS):
        create_spine_section("Spine_Section", i, col_spine_print)
    
    # Cross braces
    create_cross_brace("Brace_Lower", BASE_HEIGHT + mm(50), col_spine_print)
    create_cross_brace("Brace_Mid", BASE_HEIGHT + SPINE_HEIGHT/2, col_spine_print)
    create_cross_brace("Brace_Upper", ARM_SHOULDER_HEIGHT - mm(30), col_spine_print)
    
    # =========================================================================
    # SHOULDERS & ARM MOUNTS (Blue) - Print Batch 3
    # =========================================================================
    print("  Creating shoulder assembly...")
    
    create_shoulder_plate("Shoulder_Left", -1, col_shoulders_print)
    create_shoulder_plate("Shoulder_Right", 1, col_shoulders_print)
    create_arm_mount("Arm_Mount_Left", -1, col_shoulders_print)
    create_arm_mount("Arm_Mount_Right", 1, col_shoulders_print)
    
    # =========================================================================
    # HEAD - WHITE (Print Batch 4)
    # =========================================================================
    print("  Creating head (white parts)...")
    
    create_head_front(col_head_white)
    
    # Display bezel
    head_z = HEAD_HEIGHT - HEAD_HEIGHT_SIZE/2
    bezel = create_box(
        "Display_Bezel",
        (mm(10), DISPLAY_WIDTH + mm(10), DISPLAY_HEIGHT + mm(10)),
        (-HEAD_DEPTH/2 - mm(3), 0, head_z - mm(5)),
        COLOR_WHITE
    )
    move_to_collection(bezel, col_head_white)
    
    # =========================================================================
    # HEAD - GREY (Print Batch 5)
    # =========================================================================
    print("  Creating head (grey parts)...")
    
    create_head_rear(col_head_grey)
    create_neck(col_head_grey)
    
    # Pan-tilt base
    pan_base = create_cylinder(
        "Pan_Tilt_Base",
        mm(30), mm(20),
        (0, 0, ARM_SHOULDER_HEIGHT + mm(10)),
        COLOR_GREY
    )
    move_to_collection(pan_base, col_head_grey)
    
    # =========================================================================
    # ACCENTS - RED (Print Batch 6)
    # =========================================================================
    print("  Creating accents (red)...")
    
    create_eye_ring("Eye_Ring_Left", -1, col_accents_red)
    create_eye_ring("Eye_Ring_Right", 1, col_accents_red)
    
    # Small status indicator on chest
    indicator = create_cylinder(
        "Status_Indicator",
        mm(8), mm(5),
        (-TORSO_DEPTH/2 - mm(2), 0, ARM_SHOULDER_HEIGHT - mm(100)),
        COLOR_RED,
        rotation=(0, math.pi/2, 0)
    )
    move_to_collection(indicator, col_accents_red)
    
    # =========================================================================
    # REFERENCE HARDWARE (Not printed)
    # =========================================================================
    print("  Adding reference hardware...")
    
    create_mac_mini(col_hardware)
    
    # Rear camera
    rear_cam = create_cylinder(
        "Camera_Rear",
        mm(12), mm(15),
        (HEAD_DEPTH/2 + mm(5), 0, HEAD_HEIGHT - mm(40)),
        COLOR_DARK,
        rotation=(0, math.pi/2, 0)
    )
    move_to_collection(rear_cam, col_hardware)
    
    # =========================================================================
    # ARMS (Reference only - existing hardware)
    # =========================================================================
    print("  Adding arm references...")
    
    create_arm_placeholder("Arm_Left", -1, col_arms)
    create_arm_placeholder("Arm_Right", 1, col_arms)
    
    # =========================================================================
    # FINISHING
    # =========================================================================
    
    bpy.ops.object.select_all(action='DESELECT')
    
    # Set viewport
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.clip_end = 100
    
    print("\n" + "=" * 60)
    print("REN ROBOT BODY - PRINTABLE VERSION")
    print("=" * 60)
    print(f"Total height: {HEAD_HEIGHT*1000:.0f}mm ({HEAD_HEIGHT*1000/25.4:.1f}\")")
    print(f"Shoulder height: {ARM_SHOULDER_HEIGHT*1000:.0f}mm ({ARM_SHOULDER_HEIGHT*1000/25.4:.1f}\")")
    print(f"Base footprint: {BASE_LENGTH*1000:.0f} × {BASE_WIDTH*1000:.0f}mm")
    print("=" * 60)
    print("\nPRINT BATCHES (by collection):")
    print("  01_Print_Base_Grey     - Base frame sections, sprockets")
    print("  02_Print_Spine_Grey    - Spine sections, cross braces")
    print("  03_Print_Shoulders_Blue - Shoulder plates, arm mounts")
    print("  04_Print_Head_White    - Face plate, display bezel")
    print("  05_Print_Head_Grey     - Head rear, neck tube")
    print("  06_Print_Accents_Red   - Eye rings, status indicator")
    print("  07_Reference_Hardware  - Motors, Mac Mini (not printed)")
    print("  08_Reference_Arms      - SO-101 arms (existing)")
    print("=" * 60)
    print("\nTip: Toggle collection visibility in Outliner to see print batches")
    print("Tip: Export each print collection separately to STL")

# Run
if __name__ == "__main__":
    build_robot()
