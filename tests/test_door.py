"""
Test suite for modular door system with 4-part anatomy.

This test file verifies:
1. Door part generation (jambs, head, leaf)
2. Slot system (wall interface, doorknob, hinges)
3. Different door styles (single, double, garage)
4. Material system
5. Swing directions
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from blenpc.atoms.door import build_door, door_to_json, DOOR_MATERIALS
from blenpc.engine.grid_pos import GridPos
from blenpc import config


class TestDoorBasics:
    """Test basic door creation."""
    
    def test_simple_door_creation(self):
        """Test creating a simple single door."""
        door = build_door(style="single", material="wood")
        
        assert door.name == "door"
        assert door.style == "single"
        assert door.material == "wood"
        assert len(door.parts) == 4  # jamb_left, jamb_right, head, leaf
        assert len(door.slots) >= 4  # wall_interface, doorknob, hinge_top, hinge_bot
    
    def test_door_dimensions(self):
        """Test door dimensions match standards."""
        door = build_door(style="single")
        
        dims = config.DOOR_STANDARDS["single"]
        assert door.meta["width_m"] == dims["w"]
        assert door.meta["height_m"] == dims["h"]
    
    def test_door_tags(self):
        """Test automatic tag generation."""
        door = build_door(style="single", material="wood", swing="inward_left")
        
        assert "arch_door" in door.tags
        assert "door_single" in door.tags
        assert "mat_wood" in door.tags
        assert "swing_inward_left" in door.tags
        assert "modular_v2" in door.tags


class TestDoorParts:
    """Test door part generation."""
    
    def test_all_parts_present(self):
        """Test all 4 required parts are generated."""
        door = build_door(style="single")
        
        assert "frame_jamb_left" in door.parts
        assert "frame_jamb_right" in door.parts
        assert "frame_head" in door.parts
        assert "door_leaf" in door.parts
    
    def test_part_types(self):
        """Test part types are correctly assigned."""
        door = build_door(style="single")
        
        assert door.parts["frame_jamb_left"]["type"] == "frame_vertical"
        assert door.parts["frame_jamb_right"]["type"] == "frame_vertical"
        assert door.parts["frame_head"]["type"] == "frame_horizontal"
        assert door.parts["door_leaf"]["type"] == "leaf"
    
    def test_part_positions(self):
        """Test parts are positioned correctly."""
        door = build_door(style="single")
        
        # Left jamb should be at x=0
        assert door.parts["frame_jamb_left"]["position"][0] == 0.0
        
        # Right jamb should be at x=width-thickness
        width = door.meta["width_m"]
        thickness = door.meta["frame_thickness"]
        assert door.parts["frame_jamb_right"]["position"][0] == pytest.approx(width - thickness)
        
        # Head should be at top
        height = door.meta["height_m"]
        assert door.parts["frame_head"]["position"][2] == pytest.approx(height - thickness)
    
    def test_leaf_material(self):
        """Test leaf material is correctly assigned."""
        door = build_door(style="single", material="glass")
        
        assert door.parts["door_leaf"]["material"] == "glass"


class TestDoorStyles:
    """Test different door styles."""
    
    def test_single_door(self):
        """Test single door dimensions."""
        door = build_door(style="single")
        
        dims = config.DOOR_STANDARDS["single"]
        assert door.meta["width_m"] == dims["w"]
        assert door.meta["height_m"] == dims["h"]
    
    def test_double_door(self):
        """Test double door dimensions."""
        door = build_door(style="double")
        
        dims = config.DOOR_STANDARDS["double"]
        assert door.meta["width_m"] == dims["w"]
        assert door.meta["height_m"] == dims["h"]
        assert door.meta["width_m"] > config.DOOR_STANDARDS["single"]["w"]
    
    def test_garage_door(self):
        """Test garage door dimensions."""
        door = build_door(style="garage")
        
        dims = config.DOOR_STANDARDS["garage"]
        assert door.meta["width_m"] == dims["w"]
        assert door.meta["height_m"] == dims["h"]
    
    def test_invalid_style(self):
        """Test invalid style raises error."""
        with pytest.raises(ValueError):
            build_door(style="invalid_style")


class TestDoorMaterials:
    """Test door material system."""
    
    def test_wood_material(self):
        """Test wood material door."""
        door = build_door(material="wood")
        assert door.material == "wood"
        assert "mat_wood" in door.tags
    
    def test_glass_material(self):
        """Test glass material door."""
        door = build_door(material="glass")
        assert door.material == "glass"
        assert "mat_glass" in door.tags
    
    def test_metal_material(self):
        """Test metal material door."""
        door = build_door(material="metal")
        assert door.material == "metal"
        assert "mat_metal" in door.tags
    
    def test_composite_material(self):
        """Test composite material door."""
        door = build_door(material="composite")
        assert door.material == "composite"
        assert "mat_composite" in door.tags
    
    def test_invalid_material(self):
        """Test invalid material raises error."""
        with pytest.raises(ValueError):
            build_door(material="invalid_material")
    
    def test_material_definitions(self):
        """Test material definitions exist."""
        assert "wood" in DOOR_MATERIALS
        assert "glass" in DOOR_MATERIALS
        assert "metal" in DOOR_MATERIALS
        assert "composite" in DOOR_MATERIALS


class TestDoorSwing:
    """Test door swing directions."""
    
    def test_inward_left(self):
        """Test inward left swing."""
        door = build_door(swing="inward_left")
        assert door.swing == "inward_left"
        assert door.parts["door_leaf"]["swing"] == "inward_left"
    
    def test_inward_right(self):
        """Test inward right swing."""
        door = build_door(swing="inward_right")
        assert door.swing == "inward_right"
    
    def test_outward_left(self):
        """Test outward left swing."""
        door = build_door(swing="outward_left")
        assert door.swing == "outward_left"
    
    def test_outward_right(self):
        """Test outward right swing."""
        door = build_door(swing="outward_right")
        assert door.swing == "outward_right"
    
    def test_sliding(self):
        """Test sliding door."""
        door = build_door(swing="sliding")
        assert door.swing == "sliding"
    
    def test_invalid_swing(self):
        """Test invalid swing raises error."""
        with pytest.raises(ValueError):
            build_door(swing="invalid_swing")


class TestDoorSlots:
    """Test door slot system."""
    
    def test_wall_interface_slot(self):
        """Test wall interface slot exists."""
        door = build_door(style="single")
        
        wall_slots = [s for s in door.slots if s["id"] == "wall_interface"]
        assert len(wall_slots) == 1
        
        slot = wall_slots[0]
        assert slot["type"] == "door_opening"
        assert slot["required"] is True
    
    def test_doorknob_slot(self):
        """Test doorknob slot exists."""
        door = build_door(style="single")
        
        knob_slots = [s for s in door.slots if s["id"] == "doorknob"]
        assert len(knob_slots) == 1
        
        slot = knob_slots[0]
        assert slot["type"] == "door_hardware"
        assert slot["required"] is False
    
    def test_hinge_slots(self):
        """Test hinge slots exist."""
        door = build_door(style="single")
        
        hinge_slots = [s for s in door.slots if "hinge" in s["id"]]
        assert len(hinge_slots) == 2  # top and bottom
        
        for slot in hinge_slots:
            assert slot["type"] == "door_hinge"
            assert slot["required"] is True
    
    def test_slot_positions(self):
        """Test slot positions are reasonable."""
        door = build_door(style="single")
        
        for slot in door.slots:
            pos = slot["pos_meters"]
            
            # All positions should be within door bounds
            assert 0 <= pos[0] <= door.meta["width_m"]
            assert 0 <= pos[2] <= door.meta["height_m"]
    
    def test_doorknob_position_left(self):
        """Test doorknob position for left swing."""
        door = build_door(swing="inward_left")
        
        knob_slot = [s for s in door.slots if s["id"] == "doorknob"][0]
        pos = knob_slot["pos_meters"]
        
        # Knob should be on right side for left swing
        assert pos[0] > door.meta["width_m"] / 2
    
    def test_doorknob_position_right(self):
        """Test doorknob position for right swing."""
        door = build_door(swing="inward_right")
        
        knob_slot = [s for s in door.slots if s["id"] == "doorknob"][0]
        pos = knob_slot["pos_meters"]
        
        # Knob should be on left side for right swing
        assert pos[0] < door.meta["width_m"] / 2


class TestGridIntegration:
    """Test integration with grid system."""
    
    def test_door_implements_igridobject(self):
        """Test that DoorData implements IGridObject interface."""
        door = build_door(style="single")
        
        # Check required attributes
        assert hasattr(door, 'name')
        assert hasattr(door, 'grid_pos')
        assert hasattr(door, 'grid_size')
        assert hasattr(door, 'snap_mode')
        assert hasattr(door, 'slots')
        assert hasattr(door, 'tags')
        
        # Check grid_pos is GridPos
        assert isinstance(door.grid_pos, GridPos)
    
    def test_door_footprint(self):
        """Test door footprint calculation."""
        door = build_door(style="single")
        
        footprint = door.get_footprint()
        
        # Should have cells
        assert len(footprint) > 0
    
    def test_door_aabb(self):
        """Test door AABB calculation."""
        door = build_door(style="single")
        
        aabb = door.get_aabb()
        
        assert "min" in aabb
        assert "max" in aabb
        assert aabb["min"][0] == pytest.approx(0.0)
        assert aabb["max"][0] == pytest.approx(door.meta["width_m"])
    
    def test_door_center(self):
        """Test door center calculation."""
        door = build_door(style="single")
        
        center = door.get_center()
        cx, cy, cz = center.to_meters()
        
        # Center should be roughly in middle
        assert cx == pytest.approx(door.meta["width_m"] / 2, abs=0.1)
        assert cz == pytest.approx(door.meta["height_m"] / 2, abs=0.1)


class TestSerialization:
    """Test JSON serialization."""
    
    def test_door_to_json(self):
        """Test door serialization to JSON."""
        door = build_door(style="single", material="wood", name="test_door")
        
        json_str = door_to_json(door)
        
        assert "test_door" in json_str
        assert "single" in json_str
        assert "wood" in json_str
        assert "parts" in json_str
        assert "slots" in json_str
    
    def test_json_contains_metadata(self):
        """Test JSON contains all necessary metadata."""
        door = build_door(style="single")
        json_str = door_to_json(door)
        
        import json
        data = json.loads(json_str)
        
        assert "meta" in data
        assert "style" in data
        assert "material" in data
        assert "swing" in data
        assert data["style"] == "single"


class TestEdgeCases:
    """Test edge cases."""
    
    def test_door_with_custom_name(self):
        """Test door with custom name."""
        door = build_door(name="custom_door_01")
        assert door.name == "custom_door_01"
    
    def test_door_with_position(self):
        """Test door with custom position."""
        door = build_door(position=(1.0, 0.0, 0.0))
        
        # Position should be snapped to grid
        pos_meters = door.grid_pos.to_meters()
        assert pos_meters[0] == pytest.approx(1.0, abs=0.25)
    
    def test_metadata_completeness(self):
        """Test all metadata fields are present."""
        door = build_door(style="single", material="wood", swing="inward_left")
        
        required_meta = ["width_m", "height_m", "style", "material", "swing", 
                        "frame_thickness", "leaf_thickness", "part_count", "slot_count"]
        
        for field in required_meta:
            assert field in door.meta


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
