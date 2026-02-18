import json
import subprocess
import os
import pytest

def test_full_pipeline_integration():
    fixture_path = "tests/fixtures/standard_wall.json"
    output_path = "tests/fixtures/standard_wall_output.json"
    
    # Ensure fixture exists
    assert os.path.exists(fixture_path)
    
    # Run production command
    cmd = [
        "/home/ubuntu/blender5/blender",
        "--background", "--python", "run_command.py",
        "--", fixture_path, output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    
    # Validate output report
    assert os.path.exists(output_path)
    with open(output_path, "r") as f:
        data = json.load(f)
        assert data["status"] == "success"
        assert "asset_name" in data["result"]
        
    # Validate registry persistence
    with open("_registry/inventory.json", "r") as f:
        inventory = json.load(f)
        asset_name = data["result"]["asset_name"]
        assert asset_name in inventory["assets"]
        
        asset = inventory["assets"][asset_name]
        assert len(asset["slots"]) > 0
        # Check modularity (GRID_UNIT = 0.25)
        for slot in asset["slots"]:
            assert slot["pos"][0] % 0.25 == 0

    # Validate file existence
    assert os.path.exists(f"_library/{asset_name}.blend")

    # Cleanup output only, keep fixture
    if os.path.exists(output_path): os.remove(output_path)
