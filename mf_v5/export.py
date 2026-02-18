"""Godot-oriented export settings and manifest generation for Blender 4.3."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    import bpy
except ImportError:
    bpy = None

@dataclass(frozen=True)
class ExportSettings:
    format: str = "GLTF2"
    y_up: bool = True
    apply_modifiers: bool = True
    apply_scale: bool = True
    selected_only: bool = True
    collider_suffix: str = "-col"
    navmesh_collection: str = "MF_Navmesh"

def export_manifest(output_path: Path, building_name: str, settings: ExportSettings) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, object] = {
        "building": f"{building_name}.glb",
        "collider": f"{building_name}{settings.collider_suffix}.glb",
        "navmesh": f"{building_name}_navmesh.glb",
        "settings": settings.__dict__,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path

def export_to_glb(obj: bpy.types.Object, output_dir: Path, filename: str, settings: ExportSettings = ExportSettings()):
    """Actual GLB export using bpy.ops for Blender 4.3."""
    if bpy is None:
        return None
        
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / f"{filename}.glb"
    
    # In Blender 4.x, some export parameters might have changed, but gltf basic ones are stable
    try:
        bpy.ops.export_scene.gltf(
            filepath=str(filepath),
            export_format='GLB',
            use_selection=settings.selected_only,
            export_yup=settings.y_up,
            export_apply=settings.apply_modifiers,
        )
    except Exception as e:
        print(f"Export failed: {e}")
        return None
    
    # Selection handling is now done in engine.py before calling this function
    # This function now exports a single object that is already selected
    # The collider path logic should be handled by the caller as well
    
    return filepath
