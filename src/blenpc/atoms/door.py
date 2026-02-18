"""
Modular Door System - 4-part anatomy with slot system for BlenPC v5.2.0

Door Anatomy:
- frame_jamb_left   → left door frame (vertical)
- frame_jamb_right  → right door frame (vertical)
- frame_head        → top frame (horizontal lintel)
- door_leaf         → door panel (replaceable material)
- [threshold]       → optional floor threshold

Slot System:
- wall_interface    → connects to wall opening_slot
- doorknob          → handle/knob attachment point
- hinge_top         → top hinge
- hinge_bot         → bottom hinge
- [threshold_slot]  → optional threshold attachment
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json

try:
    import bpy
    import bmesh
except ImportError:
    bpy = None
    bmesh = None

from ..engine.grid_pos import GridPos, meters_to_units
from ..engine.grid_object import GridObjectMixin
from .. import config


@dataclass
class DoorData(GridObjectMixin):
    """
    Complete door data structure implementing IGridObject.
    
    Attributes:
        name: Unique door identifier
        grid_pos: Position in grid space
        grid_size: Size in grid units
        snap_mode: Snap mode used
        style: Door style ("single" | "double" | "garage")
        material: Leaf material ("wood" | "glass" | "metal" | "composite")
        swing: Swing direction ("inward_left" | "inward_right" | "outward_left" | "outward_right" | "sliding")
        parts: Dict of door part names to mesh data
        slots: List of slot definitions
        tags: Classification tags
        meta: Additional metadata
    """
    name: str
    grid_pos: GridPos
    grid_size: Tuple[int, int, int]
    snap_mode: str
    style: str
    material: str
    swing: str
    parts: Dict[str, Dict] = field(default_factory=dict)
    slots: List[Dict] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    meta: Dict = field(default_factory=dict)


def build_door(
    style: str = "single",
    material: str = "wood",
    swing: str = "inward_left",
    name: str = "door",
    position: Optional[Tuple[float, float, float]] = None
) -> DoorData:
    """
    Build a modular door with 4-part anatomy and slot system.
    
    Args:
        style: Door style ("single" | "double" | "garage")
        material: Leaf material ("wood" | "glass" | "metal" | "composite")
        swing: Swing direction
        name: Door identifier
        position: Optional position in meters (x, y, z)
    
    Returns:
        DoorData object with parts and slots
    
    Example:
        >>> door = build_door(style="single", material="wood", swing="inward_left")
        >>> len(door.parts)
        4  # jamb_left, jamb_right, head, leaf
        >>> len(door.slots)
        4  # wall_interface, doorknob, hinge_top, hinge_bot
    """
    # Validate inputs
    if style not in config.DOOR_STANDARDS:
        raise ValueError(f"Invalid door style: {style}. Valid: {list(config.DOOR_STANDARDS.keys())}")
    
    valid_materials = ["wood", "glass", "metal", "composite"]
    if material not in valid_materials:
        raise ValueError(f"Invalid material: {material}. Valid: {valid_materials}")
    
    valid_swings = ["inward_left", "inward_right", "outward_left", "outward_right", "sliding"]
    if swing not in valid_swings:
        raise ValueError(f"Invalid swing: {swing}. Valid: {valid_swings}")
    
    # Get standard dimensions
    dims = config.DOOR_STANDARDS[style]
    width = dims["w"]
    height = dims["h"]
    
    # Door constants
    FRAME_THICKNESS = 0.05  # 5cm frame thickness
    LEAF_THICKNESS = 0.05   # 5cm leaf thickness
    FRAME_DEPTH = 0.15      # 15cm frame depth (matches wall thickness)
    
    # Convert to grid coordinates
    if position is None:
        position = (0.0, 0.0, 0.0)
    
    grid_pos = GridPos.from_meters(*position, snap="meso")
    width_units = meters_to_units(width)
    height_units = meters_to_units(height)
    depth_units = meters_to_units(FRAME_DEPTH)
    
    grid_size = (width_units, depth_units, height_units)
    
    # Build parts
    parts = {
        "frame_jamb_left": {
            "type": "frame_vertical",
            "position": [0.0, 0.0, 0.0],
            "size": [FRAME_THICKNESS, FRAME_DEPTH, height],
            "material": "frame_wood"
        },
        "frame_jamb_right": {
            "type": "frame_vertical",
            "position": [width - FRAME_THICKNESS, 0.0, 0.0],
            "size": [FRAME_THICKNESS, FRAME_DEPTH, height],
            "material": "frame_wood"
        },
        "frame_head": {
            "type": "frame_horizontal",
            "position": [0.0, 0.0, height - FRAME_THICKNESS],
            "size": [width, FRAME_DEPTH, FRAME_THICKNESS],
            "material": "frame_wood"
        },
        "door_leaf": {
            "type": "leaf",
            "position": [FRAME_THICKNESS, FRAME_DEPTH / 2, FRAME_THICKNESS],
            "size": [width - 2 * FRAME_THICKNESS, LEAF_THICKNESS, height - 2 * FRAME_THICKNESS],
            "material": material,
            "swing": swing
        }
    }
    
    # Build slots
    slots = []
    
    # 1. Wall interface slot (connects to wall opening)
    wall_interface_slot = {
        "id": "wall_interface",
        "type": "door_opening",
        "grid_pos": GridPos(
            width_units // 2,
            depth_units // 2,
            height_units // 2
        ),
        "pos_meters": (width / 2, FRAME_DEPTH / 2, height / 2),
        "size_meters": (width, height),
        "required": True,
        "occupied": False
    }
    slots.append(wall_interface_slot)
    
    # 2. Doorknob slot
    knob_x = width - 0.1 if "left" in swing else 0.1
    knob_z = 0.95  # Standard handle height
    
    doorknob_slot = {
        "id": "doorknob",
        "type": "door_hardware",
        "grid_pos": GridPos.from_meters(knob_x, FRAME_DEPTH / 2, knob_z, snap="micro"),
        "pos_meters": (knob_x, FRAME_DEPTH / 2, knob_z),
        "size_meters": (0.06, 0.06),
        "required": False,
        "occupied": False
    }
    slots.append(doorknob_slot)
    
    # 3. Hinge slots
    hinge_x = 0.05 if "left" in swing else width - 0.05
    
    hinge_top_slot = {
        "id": "hinge_top",
        "type": "door_hinge",
        "grid_pos": GridPos.from_meters(hinge_x, FRAME_DEPTH / 2, height - 0.2, snap="micro"),
        "pos_meters": (hinge_x, FRAME_DEPTH / 2, height - 0.2),
        "size_meters": (0.04, 0.1),
        "required": True,
        "occupied": False
    }
    slots.append(hinge_top_slot)
    
    hinge_bot_slot = {
        "id": "hinge_bot",
        "type": "door_hinge",
        "grid_pos": GridPos.from_meters(hinge_x, FRAME_DEPTH / 2, 0.3, snap="micro"),
        "pos_meters": (hinge_x, FRAME_DEPTH / 2, 0.3),
        "size_meters": (0.04, 0.1),
        "required": True,
        "occupied": False
    }
    slots.append(hinge_bot_slot)
    
    # Build tags
    tags = [
        "arch_door",
        f"door_{style}",
        f"mat_{material}",
        f"swing_{swing}",
        f"size_{width}m",
        "modular_v2"
    ]
    
    # Build metadata
    meta = {
        "width_m": width,
        "height_m": height,
        "style": style,
        "material": material,
        "swing": swing,
        "frame_thickness": FRAME_THICKNESS,
        "leaf_thickness": LEAF_THICKNESS,
        "part_count": len(parts),
        "slot_count": len(slots),
        "aabb": {
            "min": [0.0, 0.0, 0.0],
            "max": [width, FRAME_DEPTH, height]
        }
    }
    
    return DoorData(
        name=name,
        grid_pos=grid_pos,
        grid_size=grid_size,
        snap_mode="meso",
        style=style,
        material=material,
        swing=swing,
        parts=parts,
        slots=slots,
        tags=tags,
        meta=meta
    )


def generate_door_mesh(door_data: DoorData) -> Optional[object]:
    """
    Generate Blender mesh from door data.
    
    Args:
        door_data: DoorData object from build_door()
    
    Returns:
        Blender object with mesh, or None if bpy not available
    
    Note:
        Creates separate objects for each part, grouped under parent.
    """
    if not bpy:
        raise ImportError("Blender 'bpy' module required for mesh generation")
    
    # Create parent empty
    parent = bpy.data.objects.new(door_data.name, None)
    parent.empty_display_type = 'PLAIN_AXES'
    parent.empty_display_size = 0.1
    
    if bpy.context.scene.collection:
        bpy.context.scene.collection.objects.link(parent)
    
    # Generate mesh for each part
    for part_name, part_data in door_data.parts.items():
        mesh = bpy.data.meshes.new(f"{door_data.name}_{part_name}")
        obj = bpy.data.objects.new(f"{door_data.name}_{part_name}", mesh)
        
        if bpy.context.scene.collection:
            bpy.context.scene.collection.objects.link(obj)
        
        # Parent to main object
        obj.parent = parent
        
        # Create box geometry
        bm = bmesh.new()
        
        pos = part_data["position"]
        size = part_data["size"]
        
        # Create cube and scale
        bmesh.ops.create_cube(bm, size=1.0)
        
        # Scale and position
        for v in bm.verts:
            v.co.x = v.co.x * size[0] / 2 + pos[0] + size[0] / 2
            v.co.y = v.co.y * size[1] / 2 + pos[1] + size[1] / 2
            v.co.z = v.co.z * size[2] / 2 + pos[2] + size[2] / 2
        
        bm.to_mesh(mesh)
        bm.free()
        
        # Store part metadata
        obj["part_type"] = part_data["type"]
        obj["material_type"] = part_data["material"]
    
    # Store metadata in parent
    parent["door_data"] = json.dumps({
        "style": door_data.style,
        "material": door_data.material,
        "swing": door_data.swing,
        "parts": len(door_data.parts),
        "slots": len(door_data.slots)
    })
    
    if door_data.slots:
        # Convert GridPos to serializable format
        serializable_slots = []
        for slot in door_data.slots:
            slot_copy = slot.copy()
            if "grid_pos" in slot_copy and hasattr(slot_copy["grid_pos"], "to_tuple"):
                slot_copy["grid_pos"] = slot_copy["grid_pos"].to_tuple()
            serializable_slots.append(slot_copy)
        parent["slots_json"] = json.dumps(serializable_slots)
    
    # Mark as asset
    parent.asset_mark()
    
    return parent


def door_to_json(door_data: DoorData) -> str:
    """
    Serialize door data to JSON.
    
    Args:
        door_data: DoorData object
    
    Returns:
        JSON string representation
    """
    # Convert slots to serializable format
    serializable_slots = []
    for slot in door_data.slots:
        slot_copy = slot.copy()
        if "grid_pos" in slot_copy and hasattr(slot_copy["grid_pos"], "to_tuple"):
            slot_copy["grid_pos"] = slot_copy["grid_pos"].to_tuple()
        serializable_slots.append(slot_copy)
    
    data = {
        "name": door_data.name,
        "grid_pos": door_data.grid_pos.to_tuple(),
        "grid_size": door_data.grid_size,
        "snap_mode": door_data.snap_mode,
        "style": door_data.style,
        "material": door_data.material,
        "swing": door_data.swing,
        "parts": door_data.parts,
        "slots": serializable_slots,
        "tags": door_data.tags,
        "meta": door_data.meta
    }
    return json.dumps(data, indent=2)


# Material definitions for different door types
DOOR_MATERIALS = {
    "wood": {
        "color": [0.4, 0.25, 0.15],
        "roughness": 0.7,
        "metallic": 0.0
    },
    "glass": {
        "color": [0.9, 0.9, 0.9],
        "roughness": 0.0,
        "metallic": 0.0,
        "alpha": 0.1,
        "ior": 1.45
    },
    "metal": {
        "color": [0.5, 0.5, 0.5],
        "roughness": 0.3,
        "metallic": 1.0
    },
    "composite": {
        "color": [0.6, 0.6, 0.6],
        "roughness": 0.5,
        "metallic": 0.2
    }
}
