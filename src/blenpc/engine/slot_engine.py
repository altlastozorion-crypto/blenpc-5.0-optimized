import json
import os
from typing import List, Dict, Optional, Tuple

# Expert Fix: Absolute imports for the package structure
from .. import config

def get_aabb(obj) -> Dict[str, List[float]]:
    """Calculate Axis-Aligned Bounding Box for a Blender object."""
    bbox_corners = [obj.matrix_world @ v for v in obj.bound_box]
    
    min_x = min(v[0] for v in bbox_corners)
    min_y = min(v[1] for v in bbox_corners)
    min_z = min(v[2] for v in bbox_corners)
    
    max_x = max(v[0] for v in bbox_corners)
    max_y = max(v[1] for v in bbox_corners)
    max_z = max(v[2] for v in bbox_corners)
    
    # Expert Fix: Rounding for consistent exports
    return {
        "min": [round(min_x, config.EXPORT_PRECISION), round(min_y, config.EXPORT_PRECISION), round(min_z, config.EXPORT_PRECISION)],
        "max": [round(max_x, config.EXPORT_PRECISION), round(max_y, config.EXPORT_PRECISION), round(max_z, config.EXPORT_PRECISION)]
    }

def find_asset(tags: List[str]) -> Optional[Dict]:
    """Find an asset in the inventory that matches all provided tags."""
    if not os.path.exists(config.INVENTORY_FILE):
        return None
        
    with open(config.INVENTORY_FILE, "r") as f:
        inventory = json.load(f)
        
    for asset_id, asset_data in inventory.get("assets", {}).items():
        if all(tag in asset_data.get("tags", []) for tag in tags):
            return asset_data
            
    return None

def place_on_slot(parent_obj, slot_data: Dict, asset_tags: List[str]):
    """Place a matching asset on a specific slot of a parent object."""
    asset_data = find_asset(asset_tags)
    if not asset_data:
        return {"status": "error", "message": f"Asset not found for tags: {asset_tags}"}
        
    return {"status": "success", "asset": asset_data["name"]}
