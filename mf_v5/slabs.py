"""Floor and ceiling slab generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .config import CEILING_THICKNESS, FLOOR_THICKNESS, STORY_HEIGHT
from .datamodel import Rect, Room


@dataclass(frozen=True)
class Slab:
    rect: Rect
    z: float
    thickness: float
    kind: str


def build_floor_ceiling_slabs(rooms: Iterable[Room], floor_index: int) -> List[Slab]:
    rooms = list(rooms)
    if not rooms:
        return []

    min_x = min(r.rect.min_x for r in rooms)
    min_y = min(r.rect.min_y for r in rooms)
    max_x = max(r.rect.max_x for r in rooms)
    max_y = max(r.rect.max_y for r in rooms)
    footprint = Rect(min_x, min_y, max_x, max_y)

    floor_z = floor_index * STORY_HEIGHT
    ceil_z = floor_z + STORY_HEIGHT - CEILING_THICKNESS

    return [
        Slab(footprint, floor_z, FLOOR_THICKNESS, "floor"),
        Slab(footprint, ceil_z, CEILING_THICKNESS, "ceiling"),
    ]


def build_navmesh_slabs(slabs: Iterable[Slab]) -> List[Slab]:
    return [s for s in slabs if s.kind == "floor"]
