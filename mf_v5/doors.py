"""Door carving by splitting wall segments into manifold-safe pieces."""

from __future__ import annotations

from typing import Dict, Iterable, List, DefaultDict
from collections import defaultdict

from .config import DOOR_HEIGHT, DOOR_WIDTH, EPSILON
from .datamodel import DoorOpening, WallSegment


def _split_horizontal(seg: WallSegment, cx: float, door_width: float) -> List[WallSegment]:
    left_end = cx - door_width / 2
    right_start = cx + door_width / 2
    x_min, x_max = sorted((seg.x1, seg.x2))

    pieces: List[WallSegment] = []
    if left_end - x_min > EPSILON:
        pieces.append(WallSegment(seg.room_id, seg.side, x_min, seg.y1, left_end, seg.y2, seg.height, seg.thickness))
    if x_max - right_start > EPSILON:
        pieces.append(WallSegment(seg.room_id, seg.side, right_start, seg.y1, x_max, seg.y2, seg.height, seg.thickness))
    return pieces


def _split_vertical(seg: WallSegment, cy: float, door_width: float) -> List[WallSegment]:
    bottom_end = cy - door_width / 2
    top_start = cy + door_width / 2
    y_min, y_max = sorted((seg.y1, seg.y2))

    pieces: List[WallSegment] = []
    if bottom_end - y_min > EPSILON:
        pieces.append(WallSegment(seg.room_id, seg.side, seg.x1, y_min, seg.x2, bottom_end, seg.height, seg.thickness))
    if y_max - top_start > EPSILON:
        pieces.append(WallSegment(seg.room_id, seg.side, seg.x1, top_start, seg.x2, y_max, seg.height, seg.thickness))
    return pieces


def carve_doors(
    wall_segments: Dict[int, List[WallSegment]],
    openings: Iterable[DoorOpening],
) -> Dict[int, List[WallSegment]]:
    # Group openings by (room_id, side)
    openings_by_room_side: DefaultDict[tuple, List[DoorOpening]] = defaultdict(list)
    for d in openings:
        openings_by_room_side[(d.room_id, d.side)].append(d)
        
    carved: Dict[int, List[WallSegment]] = {}

    for room_id, segments in wall_segments.items():
        out: List[WallSegment] = []
        for seg in segments:
            room_openings = openings_by_room_side.get((room_id, seg.side), [])
            if not room_openings:
                out.append(seg)
                continue

            # Apply all openings to this segment
            current_pieces = [seg]
            for opening in room_openings:
                next_pieces = []
                for p in current_pieces:
                    if seg.side in ("north", "south"):
                        # Check if opening is within this piece
                        p_min, p_max = sorted((p.x1, p.x2))
                        if opening.center[0] > p_min + EPSILON and opening.center[0] < p_max - EPSILON:
                            next_pieces.extend(_split_horizontal(p, opening.center[0], opening.width))
                        else:
                            next_pieces.append(p)
                    else:
                        p_min, p_max = sorted((p.y1, p.y2))
                        if opening.center[1] > p_min + EPSILON and opening.center[1] < p_max - EPSILON:
                            next_pieces.extend(_split_vertical(p, opening.center[1], opening.width))
                        else:
                            next_pieces.append(p)
                current_pieces = next_pieces
            out.extend(current_pieces)
        carved[room_id] = out

    return carved


def corridor_door_openings(corridor_facing: Dict[int, List[str]], room_rect_lookup: Dict[int, tuple]) -> List[DoorOpening]:
    openings: List[DoorOpening] = []
    for room_id, sides in corridor_facing.items():
        for side in sides: # Process all facing sides
            min_x, min_y, max_x, max_y = room_rect_lookup[room_id]
            if side in ("north", "south"):
                center = ((min_x + max_x) / 2, max_y if side == "north" else min_y)
            else:
                center = (max_x if side == "east" else min_x, (min_y + max_y) / 2)
            openings.append(DoorOpening(room_id, side, center, DOOR_WIDTH, DOOR_HEIGHT))
    return openings
