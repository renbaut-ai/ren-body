"""
Ren Robot Body - DETAILED Printable Model
==========================================
This version includes:
- Mounting holes & heat-set insert pockets
- Bolt clearances
- Rod channels for reinforcement
- Interlocking features between sections
- SO-101 arm mount pattern
- Cable routing channels
- Proper wall thicknesses

Run in Blender: Scripting tab → Open → Run Script
Or: /Applications/Blender.app/Contents/MacOS/Blender --background --python ren_body_detailed.py
"""

import bpy
import bmesh
import math
import os
import struct
from mathutils import Vector

# =============================================================================
# PARAMETERS (all in mm, converted to meters for Blender)
# =============================================================================

def mm(val):
    """Convert mm to Blender meters."""
    return val / 1000

# Output
OUTPUT_DIR = "/Users/renbaut/Projects/ren-body/stl_detailed"

# Overall dimensions
ARM_SHOULDER_HEIGHT = mm(864)    # 34 inches from ground
HEAD_HEIGHT = mm(1067)           # 42 inches from ground

# Base platform
BASE_LENGTH = mm(350)
BASE_WIDTH = mm(300)
BASE_HEIGHT = mm(80)
BASE_WALL = mm(4)                # Wall thickness

# Spine/Torso
TORSO_WIDTH = mm(200)
TORSO_DEPTH = mm(100)
SPINE_SECTION_HEIGHT = mm(200)
SPINE_WALL = mm(4)
NUM_SPINE_SECTIONS = 4

# Reinforcement rods
ROD_DIAMETER = mm(8)
ROD_HOLE_DIAMETER = mm(8.5)      # Clearance fit
ROD_POCKET_DEPTH = mm(15)        # How deep rod seats into connectors

# Hardware
M3_CLEARANCE = mm(3.4)           # M3 bolt pass-through
M3_INSERT_OD = mm(4.5)           # M3 heat-set insert outer diameter
M3_INSERT_DEPTH = mm(6)          # M3 insert depth
M4_CLEARANCE = mm(4.5)           # M4 bolt pass-through
M4_INSERT_OD = mm(5.6)           # M4 heat-set insert outer diameter
M4_INSERT_DEPTH = mm(8)          # M4 insert depth

# Arm mounting
ARM_MOUNT_SPACING = mm(280)      # Distance between arm centers
ARM_MOUNT_WIDTH = mm(80)
ARM_MOUNT_DEPTH = mm(80)
ARM_MOUNT_THICKNESS = mm(12)
# SO-101 mounting pattern (approximate - measure your actual arms!)
SO101_MOUNT_HOLE_SPACING = mm(50)  # Bolt pattern square
SO101_MOUNT_HOLE_DIA = mm(4)       # M4 bolts

# Head
HEAD_WIDTH = mm(100)
HEAD_DEPTH = mm(90)
HEAD_HEIGHT_SIZE = mm(75)
HEAD_WALL = mm(3)
NECK_OUTER_RADIUS = mm(25)
NECK_INNER_RADIUS = mm(18)       # Hollow for cables
NECK_HEIGHT = HEAD_HEIGHT - ARM_SHOULDER_HEIGHT - HEAD_HEIGHT_SIZE / 2

# Display (8x8 NeoPixel matrix is ~71mm)
DISPLAY_WIDTH = mm(72)
DISPLAY_HEIGHT = mm(72)
DISPLAY_DEPTH = mm(10)

# Cameras
EYE_HOLE_RADIUS = mm(15)         # OAK-D Lite lens clearance
EYE_SPACING = mm(55)
EYE_RING_OUTER = mm(20)
EYE_RING_INNER = mm(14)
EYE_RING_DEPTH = mm(6)

# Tracks
TRACK_WIDTH = mm(60)
SPROCKET_OUTER_RADIUS = mm(40)
SPROCKET_INNER_RADIUS = mm(15)   # Hub hole
SPROCKET_THICKNESS = mm(12)
SPROCKET_TEETH = 12
SPROCKET_TOOTH_DEPTH = mm(5)

# Interlock features
TAB_WIDTH = mm(20)
TAB_DEPTH = mm(10)
TAB_HEIGHT = mm(15)
TAB_CLEARANCE = mm(0.3)          # Tolerance for fit

# Cable routing
CABLE_CHANNEL_WIDTH = mm(25)
CABLE_CHANNEL_DEPTH = mm(15)

# Colors (RGBA)
COLOR_GREY = (0.35, 0.35, 0.38, 1.0)
COLOR_BLUE = (0.2, 0.4, 0.8, 1.0)
COLOR_WHITE = (0.92, 0.92, 0.92, 1.0)
COLOR_RED = (0.85, 0.15, 0.15, 1.0)
COLOR_DARK = (0.1, 0.1, 0.1, 1.0)
COLOR_GREEN = (0.2, 0.7, 0.3, 1.0)  # For holes visualization

# =============================================================================
# BLENDER HELPERS
# =============================================================================

def clear_scene():
    """Remove all objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

def create_collection(name):
    """Create a new collection."""
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def move_to_collection(obj, collection):
    """Move object to collection."""
    for col in obj.users_collection:
        col.objects.unlink(obj)
    collection.objects.link(obj)

def set_material(obj, color, name=None):
    """Apply material with color."""
    mat_name = name or f"{obj.name}_mat"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.4
    obj.data.materials.append(mat)

def create_cube(name, size, location=(0,0,0)):
    """Create a cube mesh."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def create_cylinder(name, radius, depth, location=(0,0,0), rotation=(0,0,0), vertices=32):
    """Create a cylinder mesh."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius, 
        depth=depth, 
        location=location, 
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj

def boolean_difference(obj, cutter, delete_cutter=True):
    """Apply boolean difference modifier."""
    mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'FAST'
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    if delete_cutter:
        bpy.data.objects.remove(cutter, do_unlink=True)

def boolean_union(obj, other, delete_other=True):
    """Apply boolean union modifier."""
    mod = obj.modifiers.new(name="Boolean", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object = other
    mod.solver = 'FAST'
    
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    if delete_other:
        bpy.data.objects.remove(other, do_unlink=True)

def add_hole(obj, radius, depth, location, direction='Z'):
    """Add a cylindrical hole to object."""
    if direction == 'Z':
        rot = (0, 0, 0)
    elif direction == 'X':
        rot = (0, math.pi/2, 0)
    elif direction == 'Y':
        rot = (math.pi/2, 0, 0)
    
    cutter = create_cylinder("_hole_cutter", radius, depth + mm(1), location, rot)
    boolean_difference(obj, cutter)

def add_counterbore(obj, clearance_r, insert_r, clearance_depth, insert_depth, location, direction='Z'):
    """Add a counterbored hole (clearance + insert pocket)."""
    # Main clearance hole (through)
    add_hole(obj, clearance_r, clearance_depth + mm(1), location, direction)
    
    # Insert pocket (from one side)
    if direction == 'Z':
        pocket_loc = (location[0], location[1], location[2] + clearance_depth/2 - insert_depth/2)
        rot = (0, 0, 0)
    elif direction == 'X':
        pocket_loc = (location[0] + clearance_depth/2 - insert_depth/2, location[1], location[2])
        rot = (0, math.pi/2, 0)
    elif direction == 'Y':
        pocket_loc = (location[0], location[1] + clearance_depth/2 - insert_depth/2, location[2])
        rot = (math.pi/2, 0, 0)
    
    cutter = create_cylinder("_insert_cutter", insert_r, insert_depth + mm(0.5), pocket_loc, rot)
    boolean_difference(obj, cutter)

# =============================================================================
# DETAILED PART GENERATORS
# =============================================================================

def create_base_section_detailed(name, quadrant, collection):
    """
    Create one quadrant of the base with:
    - Hollow interior for electronics
    - Interlocking tabs
    - M4 bolt holes for joining sections
    - Motor mount holes (for quadrants 0,1)
    """
    section_length = BASE_LENGTH / 2
    section_width = BASE_WIDTH / 2
    
    # Position offset based on quadrant (0=front-left, 1=front-right, 2=rear-left, 3=rear-right)
    x_offset = (quadrant % 2 - 0.5) * section_length
    y_offset = (quadrant // 2 - 0.5) * section_width
    
    # Outer shell
    obj = create_cube(name, (section_length, section_width, BASE_HEIGHT))
    obj.location = (x_offset, y_offset, BASE_HEIGHT / 2)
    bpy.ops.object.transform_apply(location=True)
    
    # Hollow out interior (leave walls)
    inner = create_cube("_inner", 
                        (section_length - BASE_WALL*2, section_width - BASE_WALL*2, BASE_HEIGHT - BASE_WALL),
                        (x_offset, y_offset, BASE_HEIGHT/2 + BASE_WALL/2))
    boolean_difference(obj, inner)
    
    # Add interlocking tabs on edges that meet other sections
    # Front-back edge (Y direction tabs)
    if quadrant in [0, 2]:  # Left side - add tab
        tab = create_cube("_tab",
                         (TAB_WIDTH, TAB_DEPTH, TAB_HEIGHT),
                         (x_offset, y_offset + section_width/2 + TAB_DEPTH/2, BASE_HEIGHT/2))
        boolean_union(obj, tab)
    else:  # Right side - add slot
        slot = create_cube("_slot",
                          (TAB_WIDTH + TAB_CLEARANCE*2, TAB_DEPTH + TAB_CLEARANCE, TAB_HEIGHT + TAB_CLEARANCE*2),
                          (x_offset, y_offset - section_width/2 + TAB_DEPTH/2, BASE_HEIGHT/2))
        boolean_difference(obj, slot)
    
    # Left-right edge (X direction tabs)
    if quadrant in [0, 1]:  # Front side - add tab
        tab = create_cube("_tab2",
                         (TAB_DEPTH, TAB_WIDTH, TAB_HEIGHT),
                         (x_offset + section_length/2 + TAB_DEPTH/2, y_offset, BASE_HEIGHT/2))
        boolean_union(obj, tab)
    else:  # Rear side - add slot  
        slot = create_cube("_slot2",
                          (TAB_DEPTH + TAB_CLEARANCE, TAB_WIDTH + TAB_CLEARANCE*2, TAB_HEIGHT + TAB_CLEARANCE*2),
                          (x_offset - section_length/2 + TAB_DEPTH/2, y_offset, BASE_HEIGHT/2))
        boolean_difference(obj, slot)
    
    # M4 bolt holes for joining sections (on mating edges)
    bolt_z = BASE_HEIGHT / 2
    
    # Holes on Y edges
    for bx in [-section_length/4, section_length/4]:
        if quadrant in [0, 2]:  # Left sections get inserts
            add_counterbore(obj, M4_CLEARANCE/2, M4_INSERT_OD/2, 
                           section_width, M4_INSERT_DEPTH,
                           (x_offset + bx, y_offset + section_width/2, bolt_z), 'Y')
        else:  # Right sections get clearance holes
            add_hole(obj, M4_CLEARANCE/2, section_width,
                    (x_offset + bx, y_offset - section_width/2, bolt_z), 'Y')
    
    # Motor mount holes (front sections only)
    if quadrant in [0, 1]:
        motor_y = y_offset
        motor_x = x_offset - section_length/4
        # 4 M3 holes for motor mounting plate
        for dx, dy in [(-mm(15), -mm(15)), (-mm(15), mm(15)), (mm(15), -mm(15)), (mm(15), mm(15))]:
            add_counterbore(obj, M3_CLEARANCE/2, M3_INSERT_OD/2,
                           BASE_WALL*2, M3_INSERT_DEPTH,
                           (motor_x + dx, motor_y + dy, BASE_WALL), 'Z')
    
    # Spine mounting holes (center area where all 4 meet)
    # Only add partial holes - they complete when sections join
    spine_offset = mm(25)  # Distance from center to mounting hole
    for dx, dy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
        # Check if this hole belongs to this quadrant
        hole_x = dx * spine_offset
        hole_y = dy * spine_offset
        if (hole_x > 0) == (quadrant % 2 == 1) and (hole_y > 0) == (quadrant // 2 == 1):
            add_counterbore(obj, M4_CLEARANCE/2, M4_INSERT_OD/2,
                           BASE_HEIGHT, M4_INSERT_DEPTH,
                           (x_offset + (1 if quadrant%2==0 else -1)*section_length/2 + hole_x, 
                            y_offset + (1 if quadrant//2==0 else -1)*section_width/2 + hole_y,
                            BASE_HEIGHT/2), 'Z')
    
    set_material(obj, COLOR_GREY)
    move_to_collection(obj, collection)
    return obj

def create_spine_section_detailed(name, index, collection):
    """
    Create one spine section with:
    - Hollow rectangular profile
    - Rod channels at corners
    - Bolt holes top/bottom for connectors
    - Cable channel through center
    """
    outer_w = TORSO_DEPTH
    outer_d = mm(70)
    inner_w = outer_w - SPINE_WALL * 2
    inner_d = outer_d - SPINE_WALL * 2
    
    z_base = BASE_HEIGHT + SPINE_SECTION_HEIGHT * index
    z_center = z_base + SPINE_SECTION_HEIGHT / 2
    
    # Outer shell
    obj = create_cube(name, (outer_w, outer_d, SPINE_SECTION_HEIGHT))
    obj.location = (0, 0, z_center)
    bpy.ops.object.transform_apply(location=True)
    
    # Hollow interior
    inner = create_cube("_inner", (inner_w, inner_d, SPINE_SECTION_HEIGHT + mm(1)),
                        (0, 0, z_center))
    boolean_difference(obj, inner)
    
    # Rod channels at corners
    rod_offset_x = outer_w/2 - SPINE_WALL - ROD_HOLE_DIAMETER/2 - mm(2)
    rod_offset_y = outer_d/2 - SPINE_WALL - ROD_HOLE_DIAMETER/2 - mm(2)
    
    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        # Through hole for rod
        rod_hole = create_cylinder("_rod", ROD_HOLE_DIAMETER/2, SPINE_SECTION_HEIGHT + mm(2),
                                   (dx * rod_offset_x, dy * rod_offset_y, z_center))
        boolean_difference(obj, rod_hole)
    
    # Cable routing channel (center)
    cable_channel = create_cube("_cable", 
                               (CABLE_CHANNEL_WIDTH, CABLE_CHANNEL_DEPTH, SPINE_SECTION_HEIGHT + mm(2)),
                               (0, 0, z_center))
    boolean_difference(obj, cable_channel)
    
    # Bolt holes for connectors (top and bottom faces)
    bolt_offset = mm(20)
    for side_z, z_pos in [(-1, z_base + mm(10)), (1, z_base + SPINE_SECTION_HEIGHT - mm(10))]:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            # Skip positions that conflict with rod holes
            if abs(dx * bolt_offset) < rod_offset_x and abs(dy * bolt_offset) < rod_offset_y:
                add_counterbore(obj, M3_CLEARANCE/2, M3_INSERT_OD/2,
                               SPINE_WALL * 2, M3_INSERT_DEPTH,
                               (dx * bolt_offset, dy * bolt_offset, z_pos), 'Z')
    
    set_material(obj, COLOR_GREY)
    move_to_collection(obj, collection)
    return obj

def create_spine_connector_detailed(name, index, collection):
    """
    Create connector that joins two spine sections:
    - Rod pockets
    - Bolt holes matching spine sections
    - Structural bridge
    """
    conn_w = TORSO_DEPTH + mm(30)
    conn_d = mm(90)
    conn_h = mm(40)
    
    z_pos = BASE_HEIGHT + SPINE_SECTION_HEIGHT * (index + 1)
    
    obj = create_cube(name, (conn_w, conn_d, conn_h))
    obj.location = (0, 0, z_pos)
    bpy.ops.object.transform_apply(location=True)
    
    # Rod pockets (blind holes from top and bottom)
    rod_offset_x = TORSO_DEPTH/2 - SPINE_WALL - ROD_HOLE_DIAMETER/2 - mm(2)
    rod_offset_y = mm(70)/2 - SPINE_WALL - ROD_HOLE_DIAMETER/2 - mm(2)
    
    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        # Through holes for rods
        rod_hole = create_cylinder("_rod", ROD_HOLE_DIAMETER/2, conn_h + mm(2),
                                  (dx * rod_offset_x, dy * rod_offset_y, z_pos))
        boolean_difference(obj, rod_hole)
    
    # Cable channel continuation
    cable = create_cube("_cable", (CABLE_CHANNEL_WIDTH, CABLE_CHANNEL_DEPTH, conn_h + mm(2)),
                       (0, 0, z_pos))
    boolean_difference(obj, cable)
    
    # Bolt holes to mate with spine sections
    bolt_offset = mm(20)
    for dz in [-conn_h/2 + mm(8), conn_h/2 - mm(8)]:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if abs(dx * bolt_offset) < rod_offset_x and abs(dy * bolt_offset) < rod_offset_y:
                add_hole(obj, M3_CLEARANCE/2, conn_d,
                        (dx * bolt_offset, 0, z_pos + dz), 'Y')
    
    set_material(obj, COLOR_GREY)
    move_to_collection(obj, collection)
    return obj

def create_cross_brace_detailed(name, z_height, collection):
    """
    Create cross brace with:
    - Bolt holes to attach to spine
    - Lighter weight (cut-outs)
    """
    brace_w = TORSO_DEPTH + mm(50)
    brace_d = TORSO_WIDTH
    brace_h = mm(25)
    
    obj = create_cube(name, (brace_w, brace_d, brace_h))
    obj.location = (0, 0, z_height)
    bpy.ops.object.transform_apply(location=True)
    
    # Center cutout (weight reduction + cable routing)
    cutout = create_cube("_cutout", (brace_w - mm(40), brace_d - mm(60), brace_h + mm(2)),
                        (0, 0, z_height))
    boolean_difference(obj, cutout)
    
    # Bolt holes to spine
    spine_attach_y = mm(35)/2 + mm(10)
    for dy in [-spine_attach_y, spine_attach_y]:
        for dx in [-mm(20), mm(20)]:
            add_hole(obj, M3_CLEARANCE/2, brace_h + mm(2),
                    (dx, dy, z_height), 'Z')
    
    set_material(obj, COLOR_GREY)
    move_to_collection(obj, collection)
    return obj

def create_shoulder_plate_detailed(name, side, collection):
    """
    Create shoulder plate with:
    - Mounting holes to spine top
    - Arm mount attachment holes
    - Cable pass-through
    """
    plate_w = TORSO_DEPTH + mm(70)
    plate_d = mm(90)
    plate_h = mm(18)
    
    y_pos = side * (TORSO_WIDTH/2 - mm(20))
    z_pos = ARM_SHOULDER_HEIGHT - plate_h/2
    
    obj = create_cube(name, (plate_w, plate_d, plate_h))
    obj.location = (0, y_pos, z_pos)
    bpy.ops.object.transform_apply(location=True)
    
    # Spine attachment holes (bolt down to top of spine)
    for dx in [-mm(25), mm(25)]:
        for dy in [-mm(25), mm(25)]:
            add_counterbore(obj, M4_CLEARANCE/2, M4_INSERT_OD/2,
                           plate_h, M4_INSERT_DEPTH,
                           (dx, y_pos + dy * 0.3, z_pos), 'Z')
    
    # Arm mount attachment holes (threaded inserts on top)
    arm_attach_offset = mm(25)
    for dx in [-arm_attach_offset, arm_attach_offset]:
        for dy_off in [-arm_attach_offset, arm_attach_offset]:
            actual_y = y_pos + dy_off * 0.4
            add_counterbore(obj, M4_CLEARANCE/2, M4_INSERT_OD/2,
                           plate_h, M4_INSERT_DEPTH,
                           (dx, actual_y, z_pos), 'Z')
    
    # Cable pass-through
    cable_hole = create_cylinder("_cable", mm(20), plate_h + mm(2),
                                (0, y_pos, z_pos))
    boolean_difference(obj, cable_hole)
    
    set_material(obj, COLOR_BLUE)
    move_to_collection(obj, collection)
    return obj

def create_arm_mount_detailed(name, side, collection):
    """
    Create SO-101 arm mount with:
    - SO-101 mounting pattern (4x M4 holes, 50mm square pattern)
    - Shoulder plate attachment holes
    - Chamfered edges
    """
    y_pos = side * ARM_MOUNT_SPACING/2
    z_pos = ARM_SHOULDER_HEIGHT + ARM_MOUNT_THICKNESS/2
    
    obj = create_cube(name, (ARM_MOUNT_DEPTH, ARM_MOUNT_WIDTH, ARM_MOUNT_THICKNESS))
    obj.location = (0, y_pos, z_pos)
    bpy.ops.object.transform_apply(location=True)
    
    # SO-101 mounting holes (4 corners, 50mm square pattern)
    so101_offset = SO101_MOUNT_HOLE_SPACING / 2
    for dx, dy in [(-so101_offset, -so101_offset), (-so101_offset, so101_offset),
                   (so101_offset, -so101_offset), (so101_offset, so101_offset)]:
        # Through holes for SO-101 bolts
        add_hole(obj, SO101_MOUNT_HOLE_DIA/2, ARM_MOUNT_THICKNESS + mm(2),
                (dx, y_pos + dy, z_pos), 'Z')
    
    # Shoulder plate attachment holes (countersunk from bottom)
    attach_offset = mm(30)
    for dx, dy in [(-attach_offset, -attach_offset), (-attach_offset, attach_offset),
                   (attach_offset, -attach_offset), (attach_offset, attach_offset)]:
        add_counterbore(obj, M4_CLEARANCE/2, M4_INSERT_OD/2,
                       ARM_MOUNT_THICKNESS, M4_INSERT_DEPTH,
                       (dx, y_pos + dy * 0.7, z_pos), 'Z')
    
    # Center hole for arm wiring
    cable_hole = create_cylinder("_cable", mm(15), ARM_MOUNT_THICKNESS + mm(2),
                                (0, y_pos, z_pos))
    boolean_difference(obj, cable_hole)
    
    set_material(obj, COLOR_BLUE)
    move_to_collection(obj, collection)
    return obj

def create_head_front_detailed(name, collection):
    """
    Create front head shell with:
    - Display cutout
    - Camera/eye holes
    - Mounting tabs
    """
    z_pos = HEAD_HEIGHT - HEAD_HEIGHT_SIZE/2
    
    obj = create_cube(name, (HEAD_WALL * 3, HEAD_WIDTH, HEAD_HEIGHT_SIZE))
    obj.location = (-HEAD_DEPTH/2 + HEAD_WALL * 1.5, 0, z_pos)
    bpy.ops.object.transform_apply(location=True)
    
    # Display cutout
    display_cut = create_cube("_display", 
                             (HEAD_WALL * 4, DISPLAY_WIDTH + mm(2), DISPLAY_HEIGHT + mm(2)),
                             (-HEAD_DEPTH/2 + HEAD_WALL * 1.5, 0, z_pos - mm(5)))
    boolean_difference(obj, display_cut)
    
    # Eye holes for cameras
    eye_z = z_pos + HEAD_HEIGHT_SIZE/2 - mm(22)
    for side in [-1, 1]:
        eye_hole = create_cylinder("_eye", EYE_HOLE_RADIUS, HEAD_WALL * 4,
                                  (-HEAD_DEPTH/2 + HEAD_WALL * 1.5, side * EYE_SPACING/2, eye_z),
                                  (0, math.pi/2, 0))
        boolean_difference(obj, eye_hole)
    
    # Mounting holes to connect to rear shell
    for dy in [-HEAD_WIDTH/2 + mm(10), HEAD_WIDTH/2 - mm(10)]:
        for dz in [-HEAD_HEIGHT_SIZE/2 + mm(10), HEAD_HEIGHT_SIZE/2 - mm(10)]:
            add_counterbore(obj, M3_CLEARANCE/2, M3_INSERT_OD/2,
                           HEAD_WALL * 3, M3_INSERT_DEPTH,
                           (-HEAD_DEPTH/2 + HEAD_WALL * 1.5, dy, z_pos + dz), 'X')
    
    set_material(obj, COLOR_WHITE)
    move_to_collection(obj, collection)
    return obj

def create_head_rear_detailed(name, collection):
    """
    Create rear head shell with:
    - Hollow interior for electronics
    - Mounting holes
    - Rear camera hole
    - Neck attachment
    """
    z_pos = HEAD_HEIGHT - HEAD_HEIGHT_SIZE/2
    
    # Outer shell
    obj = create_cube(name, (HEAD_DEPTH - HEAD_WALL * 3, HEAD_WIDTH, HEAD_HEIGHT_SIZE))
    obj.location = (HEAD_WALL * 1.5, 0, z_pos)
    bpy.ops.object.transform_apply(location=True)
    
    # Hollow interior
    inner = create_cube("_inner",
                       (HEAD_DEPTH - HEAD_WALL * 5, HEAD_WIDTH - HEAD_WALL * 2, HEAD_HEIGHT_SIZE - HEAD_WALL * 2),
                       (HEAD_WALL, 0, z_pos))
    boolean_difference(obj, inner)
    
    # Front opening (mates with front shell)
    front_open = create_cube("_front_open",
                            (mm(10), HEAD_WIDTH - HEAD_WALL * 4, HEAD_HEIGHT_SIZE - HEAD_WALL * 4),
                            (-HEAD_DEPTH/2 + HEAD_WALL * 4, 0, z_pos))
    boolean_difference(obj, front_open)
    
    # Rear camera hole
    rear_cam = create_cylinder("_rear_cam", mm(12), HEAD_WALL * 3,
                              (HEAD_DEPTH/2 - HEAD_WALL, 0, z_pos - mm(10)),
                              (0, math.pi/2, 0))
    boolean_difference(obj, rear_cam)
    
    # Neck attachment hole (bottom)
    neck_hole = create_cylinder("_neck", NECK_OUTER_RADIUS + mm(1), HEAD_WALL * 2,
                               (0, 0, z_pos - HEAD_HEIGHT_SIZE/2 + HEAD_WALL))
    boolean_difference(obj, neck_hole)
    
    # Neck attachment bolt holes
    neck_bolt_r = NECK_OUTER_RADIUS + mm(8)
    for angle in [0, 90, 180, 270]:
        bx = neck_bolt_r * math.cos(math.radians(angle))
        by = neck_bolt_r * math.sin(math.radians(angle))
        add_counterbore(obj, M3_CLEARANCE/2, M3_INSERT_OD/2,
                       HEAD_WALL * 2, M3_INSERT_DEPTH,
                       (bx, by, z_pos - HEAD_HEIGHT_SIZE/2 + HEAD_WALL), 'Z')
    
    set_material(obj, COLOR_GREY)
    move_to_collection(obj, collection)
    return obj

def create_neck_detailed(name, collection):
    """
    Create hollow neck tube with:
    - Cable pass-through
    - Mounting flanges top and bottom
    """
    neck_z = ARM_SHOULDER_HEIGHT + NECK_HEIGHT/2
    
    # Main tube
    obj = create_cylinder(name, NECK_OUTER_RADIUS, NECK_HEIGHT, (0, 0, neck_z))
    
    # Hollow interior
    inner = create_cylinder("_inner", NECK_INNER_RADIUS, NECK_HEIGHT + mm(2), (0, 0, neck_z))
    boolean_difference(obj, inner)
    
    # Bottom flange
    flange_b = create_cylinder("_flange_b", NECK_OUTER_RADIUS + mm(12), mm(8),
                              (0, 0, ARM_SHOULDER_HEIGHT + mm(4)))
    boolean_union(obj, flange_b)
    
    # Top flange  
    flange_t = create_cylinder("_flange_t", NECK_OUTER_RADIUS + mm(10), mm(6),
                              (0, 0, ARM_SHOULDER_HEIGHT + NECK_HEIGHT - mm(3)))
    boolean_union(obj, flange_t)
    
    # Bolt holes in flanges
    bolt_r = NECK_OUTER_RADIUS + mm(8)
    for angle in [0, 90, 180, 270]:
        bx = bolt_r * math.cos(math.radians(angle))
        by = bolt_r * math.sin(math.radians(angle))
        # Bottom flange
        add_hole(obj, M3_CLEARANCE/2, mm(10),
                (bx, by, ARM_SHOULDER_HEIGHT + mm(4)), 'Z')
        # Top flange
        add_hole(obj, M3_CLEARANCE/2, mm(10),
                (bx, by, ARM_SHOULDER_HEIGHT + NECK_HEIGHT - mm(3)), 'Z')
    
    set_material(obj, COLOR_GREY)
    move_to_collection(obj, collection)
    return obj

def create_eye_ring_detailed(name, side, collection):
    """
    Create camera eye ring accent.
    """
    head_z = HEAD_HEIGHT - HEAD_HEIGHT_SIZE/2
    eye_z = head_z + HEAD_HEIGHT_SIZE/2 - mm(22)
    y_pos = side * EYE_SPACING/2
    x_pos = -HEAD_DEPTH/2 - mm(2)
    
    # Outer ring
    obj = create_cylinder(name, EYE_RING_OUTER, EYE_RING_DEPTH,
                         (x_pos, y_pos, eye_z), (0, math.pi/2, 0))
    
    # Inner cutout
    inner = create_cylinder("_inner", EYE_RING_INNER, EYE_RING_DEPTH + mm(2),
                           (x_pos, y_pos, eye_z), (0, math.pi/2, 0))
    boolean_difference(obj, inner)
    
    set_material(obj, COLOR_RED)
    move_to_collection(obj, collection)
    return obj

def create_sprocket_detailed(name, side, front, collection):
    """
    Create track sprocket with:
    - Teeth for track engagement
    - Hub hole for motor shaft
    - Set screw hole
    """
    x_pos = (1 if front else -1) * (BASE_LENGTH/2 - SPROCKET_OUTER_RADIUS - mm(10))
    y_pos = side * (BASE_WIDTH/2 + TRACK_WIDTH/2)
    z_pos = SPROCKET_OUTER_RADIUS + mm(15)
    
    # Main disc
    obj = create_cylinder(name, SPROCKET_OUTER_RADIUS, SPROCKET_THICKNESS,
                         (x_pos, y_pos, z_pos), (math.pi/2, 0, 0), vertices=48)
    
    # Hub hole
    hub = create_cylinder("_hub", SPROCKET_INNER_RADIUS, SPROCKET_THICKNESS + mm(2),
                         (x_pos, y_pos, z_pos), (math.pi/2, 0, 0))
    boolean_difference(obj, hub)
    
    # Teeth (simplified - notches around edge)
    tooth_angle = 360 / SPROCKET_TEETH
    for i in range(SPROCKET_TEETH):
        angle = math.radians(i * tooth_angle + tooth_angle/2)
        tx = x_pos
        ty = y_pos + (SPROCKET_OUTER_RADIUS - SPROCKET_TOOTH_DEPTH/2) * math.sin(angle)
        tz = z_pos + (SPROCKET_OUTER_RADIUS - SPROCKET_TOOTH_DEPTH/2) * math.cos(angle)
        
        tooth_cut = create_cube("_tooth",
                               (SPROCKET_THICKNESS + mm(2), mm(8), SPROCKET_TOOTH_DEPTH * 2))
        tooth_cut.location = (tx, ty, tz)
        tooth_cut.rotation_euler = (angle, 0, 0)
        bpy.ops.object.transform_apply(location=True, rotation=True)
        boolean_difference(obj, tooth_cut)
    
    # Set screw hole (radial)
    set_screw = create_cylinder("_setscrew", mm(2), mm(15),
                               (x_pos, y_pos + SPROCKET_INNER_RADIUS + mm(5), z_pos),
                               (math.pi/2, 0, 0))
    boolean_difference(obj, set_screw)
    
    set_material(obj, COLOR_GREY)
    move_to_collection(obj, collection)
    return obj

def create_cable_clip_detailed(name, index, collection):
    """
    Create snap-fit cable clip.
    """
    clip_w = mm(20)
    clip_d = mm(12)
    clip_h = mm(15)
    channel_r = mm(6)
    
    # Base
    obj = create_cube(name, (clip_w, clip_d, clip_h))
    obj.location = (0, 0, clip_h/2)
    bpy.ops.object.transform_apply(location=True)
    
    # Cable channel (top)
    channel = create_cylinder("_channel", channel_r, clip_w + mm(2),
                             (0, 0, clip_h - channel_r + mm(2)), (0, math.pi/2, 0))
    boolean_difference(obj, channel)
    
    # Snap tab cutouts
    for dy in [-1, 1]:
        snap_cut = create_cube("_snap",
                              (clip_w - mm(4), mm(3), mm(8)),
                              (0, dy * (clip_d/2 - mm(1)), clip_h - mm(4)))
        boolean_difference(obj, snap_cut)
    
    # Mounting hole
    add_hole(obj, M3_CLEARANCE/2, clip_h, (0, 0, clip_h/2), 'Z')
    
    # Move to grid position for export
    obj.location = (mm(25) * (index % 5), mm(25) * (index // 5), 0)
    bpy.ops.object.transform_apply(location=True)
    
    set_material(obj, COLOR_GREY)
    move_to_collection(obj, collection)
    return obj

# =============================================================================
# STL EXPORT
# =============================================================================

def write_stl_binary(filepath, obj, scale=1000.0):
    """Write binary STL file."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    
    mesh.calc_loop_triangles()
    
    with open(filepath, 'wb') as f:
        header = f"Ren Robot: {obj.name}"[:80].ljust(80)
        f.write(header.encode('ascii'))
        
        num_tris = len(mesh.loop_triangles)
        f.write(struct.pack('<I', num_tris))
        
        for tri in mesh.loop_triangles:
            n = tri.normal
            f.write(struct.pack('<fff', n.x, n.y, n.z))
            
            for vert_idx in tri.vertices:
                v = mesh.vertices[vert_idx].co
                f.write(struct.pack('<fff', v.x * scale, v.y * scale, v.z * scale))
            
            f.write(struct.pack('<H', 0))
    
    obj_eval.to_mesh_clear()
    return num_tris

def export_all_stls():
    """Export all printable parts."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    collections = [
        "01_Base_Detailed",
        "02_Spine_Detailed",
        "03_Shoulders_Detailed",
        "04_Head_White_Detailed",
        "05_Head_Grey_Detailed",
        "06_Accents_Detailed",
    ]
    
    exported = []
    print(f"\nExporting to {OUTPUT_DIR}\n")
    
    for col_name in collections:
        if col_name not in bpy.data.collections:
            continue
        
        collection = bpy.data.collections[col_name]
        print(f"📁 {col_name}")
        
        for obj in collection.objects:
            if obj.type != 'MESH':
                continue
            
            filename = obj.name.replace(" ", "_")
            filepath = os.path.join(OUTPUT_DIR, f"{filename}.stl")
            
            try:
                num_tris = write_stl_binary(filepath, obj)
                exported.append(filename)
                print(f"  ✓ {filename}.stl ({num_tris} tris)")
            except Exception as e:
                print(f"  ✗ {obj.name}: {e}")
    
    print(f"\n{'='*50}")
    print(f"Exported {len(exported)} detailed STL files")
    return exported

# =============================================================================
# MAIN BUILD
# =============================================================================

def build_detailed_model():
    """Build the complete detailed model."""
    clear_scene()
    
    # Collections
    col_base = create_collection("01_Base_Detailed")
    col_spine = create_collection("02_Spine_Detailed")
    col_shoulders = create_collection("03_Shoulders_Detailed")
    col_head_w = create_collection("04_Head_White_Detailed")
    col_head_g = create_collection("05_Head_Grey_Detailed")
    col_accents = create_collection("06_Accents_Detailed")
    
    print("Building detailed model...")
    
    # Base sections
    print("  Base sections...")
    for i in range(4):
        create_base_section_detailed(f"Base_Section_{i+1}_Detailed", i, col_base)
    
    # Sprockets
    print("  Sprockets...")
    for side_name, side in [("Left", -1), ("Right", 1)]:
        for pos_name, front in [("Front", True), ("Rear", False)]:
            create_sprocket_detailed(f"Sprocket_{side_name}_{pos_name}_Detailed", side, front, col_base)
    
    # Spine sections
    print("  Spine sections...")
    for i in range(NUM_SPINE_SECTIONS):
        create_spine_section_detailed(f"Spine_Section_{i+1}_Detailed", i, col_spine)
    
    # Spine connectors
    print("  Spine connectors...")
    for i in range(NUM_SPINE_SECTIONS - 1):
        create_spine_connector_detailed(f"Spine_Connector_{i+1}_Detailed", i, col_spine)
    
    # Cross braces
    print("  Cross braces...")
    for name, z in [("Lower", BASE_HEIGHT + mm(60)),
                    ("Mid", BASE_HEIGHT + SPINE_SECTION_HEIGHT * 2),
                    ("Upper", ARM_SHOULDER_HEIGHT - mm(40))]:
        create_cross_brace_detailed(f"Cross_Brace_{name}_Detailed", z, col_spine)
    
    # Shoulders
    print("  Shoulders...")
    for side_name, side in [("Left", -1), ("Right", 1)]:
        create_shoulder_plate_detailed(f"Shoulder_Plate_{side_name}_Detailed", side, col_shoulders)
        create_arm_mount_detailed(f"Arm_Mount_{side_name}_Detailed", side, col_shoulders)
    
    # Head
    print("  Head...")
    create_head_front_detailed("Head_Front_Detailed", col_head_w)
    create_head_rear_detailed("Head_Rear_Detailed", col_head_g)
    create_neck_detailed("Neck_Detailed", col_head_g)
    
    # Accents
    print("  Accents...")
    for side_name, side in [("Left", -1), ("Right", 1)]:
        create_eye_ring_detailed(f"Eye_Ring_{side_name}_Detailed", side, col_accents)
    
    # Cable clips
    print("  Cable clips...")
    for i in range(6):
        create_cable_clip_detailed(f"Cable_Clip_{i+1}_Detailed", i, col_accents)
    
    print("\nDetailed model complete!")

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    build_detailed_model()
    export_all_stls()
    
    print("\n" + "="*60)
    print("DETAILED MODEL BUILD COMPLETE")
    print("="*60)
    print(f"\nFiles exported to: {OUTPUT_DIR}")
    print("\nFeatures included:")
    print("  • Interlocking tabs on base sections")
    print("  • Heat-set insert pockets (M3, M4)")
    print("  • Rod channels in spine")
    print("  • SO-101 mounting pattern on arm mounts")
    print("  • Cable routing channels throughout")
    print("  • Sprocket teeth and hub holes")
    print("  • Snap-fit cable clips")
    print("="*60)
