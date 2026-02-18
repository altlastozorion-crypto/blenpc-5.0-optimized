"""Roof topology descriptors including true hip, gabled, and shed roof surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .config import ROOF_HEIGHT
from .datamodel import Rect, RoofType


@dataclass(frozen=True)
class RoofFace:
    vertices: Tuple[Tuple[float, float, float], ...]


@dataclass(frozen=True)
class RoofGeometry:
    roof_type: RoofType
    faces: List[RoofFace]


def build_roof(footprint: Rect, base_z: float, roof_type: RoofType) -> RoofGeometry:
    min_x, min_y, max_x, max_y = footprint.min_x, footprint.min_y, footprint.max_x, footprint.max_y
    
    if roof_type == RoofType.HIP:
        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        apex = (cx, cy, base_z + ROOF_HEIGHT)
        corners = [
            (min_x, min_y, base_z),
            (max_x, min_y, base_z),
            (max_x, max_y, base_z),
            (min_x, max_y, base_z),
        ]
        faces = [
            RoofFace((corners[0], corners[1], apex)),
            RoofFace((corners[1], corners[2], apex)),
            RoofFace((corners[2], corners[3], apex)),
            RoofFace((corners[3], corners[0], apex)),
            # Bottom face
            RoofFace((corners[3], corners[2], corners[1], corners[0])),
        ]
        return RoofGeometry(roof_type, faces)

    if roof_type == RoofType.FLAT:
        faces = [
            # Top face
            RoofFace(((min_x, min_y, base_z), (max_x, min_y, base_z), (max_x, max_y, base_z), (min_x, max_y, base_z))),
            # Bottom face
            RoofFace(((min_x, max_y, base_z), (max_x, max_y, base_z), (max_x, min_y, base_z), (min_x, min_y, base_z))),
        ]
        return RoofGeometry(roof_type, faces)

    if roof_type == RoofType.GABLED:
        mid_x = (min_x + max_x) / 2
        ridge_a = (mid_x, min_y, base_z + ROOF_HEIGHT)
        ridge_b = (mid_x, max_y, base_z + ROOF_HEIGHT)
        
        c0 = (min_x, min_y, base_z)
        c1 = (max_x, min_y, base_z)
        c2 = (max_x, max_y, base_z)
        c3 = (min_x, max_y, base_z)
        
        faces = [
            # Main slopes
            RoofFace((c0, ridge_a, ridge_b, c3)),
            RoofFace((c1, c2, ridge_b, ridge_a)),
            # Gable ends
            RoofFace((c0, c1, ridge_a)),
            RoofFace((c3, ridge_b, c2)),
            # Bottom
            RoofFace((c3, c2, c1, c0)),
        ]
        return RoofGeometry(roof_type, faces)

    if roof_type == RoofType.SHED:
        # High side at max_x
        c0 = (min_x, min_y, base_z)
        c1 = (max_x, min_y, base_z + ROOF_HEIGHT)
        c2 = (max_x, max_y, base_z + ROOF_HEIGHT)
        c3 = (min_x, max_y, base_z)
        
        # Bottom corners for solid
        b0 = (min_x, min_y, base_z)
        b1 = (max_x, min_y, base_z)
        b2 = (max_x, max_y, base_z)
        b3 = (min_x, max_y, base_z)
        
        faces = [
            # Top slope
            RoofFace((c0, c1, c2, c3)),
            # Sides
            RoofFace((b0, b1, c1, c0)),
            RoofFace((b1, b2, c2, c1)),
            RoofFace((b2, b3, c3, c2)),
            RoofFace((b3, b0, c0, c3)),
            # Bottom
            RoofFace((b3, b2, b1, b0)),
        ]
        return RoofGeometry(roof_type, faces)

    # Fallback to FLAT
    return build_roof(footprint, base_z, RoofType.FLAT)
