import json
import os
import time
from typing import List, Dict, Optional

# Expert Fix: Absolute imports for the package structure
from .. import config
    
LOCK_FILE = os.path.join(config.REGISTRY_DIR, ".inventory.lock")

class InventoryManager:
    @staticmethod
    def acquire_lock(timeout=None):
        """Acquire a simple file lock for inventory operations."""
        if timeout is None:
            timeout = config.INVENTORY_LOCK_TIMEOUT
            
        start_time = time.time()
        while os.path.exists(LOCK_FILE):
            if os.path.exists(LOCK_FILE):
                lock_age = time.time() - os.path.getmtime(LOCK_FILE)
                if lock_age > config.INVENTORY_LOCK_STALE_AGE:
                    try:
                        os.remove(LOCK_FILE)
                    except:
                        pass
            
            if time.time() - start_time > timeout:
                raise TimeoutError("Could not acquire inventory lock")
            time.sleep(config.INVENTORY_LOCK_POLL_INTERVAL)
        
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))

    @staticmethod
    def release_lock():
        """Release the inventory file lock."""
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
            except:
                pass

    @staticmethod
    def find_asset(tags: List[str]) -> Optional[Dict]:
        """Find an asset matching all tags using the registry."""
        if not os.path.exists(config.INVENTORY_FILE):
            return None
            
        with open(config.INVENTORY_FILE, "r") as f:
            inventory = json.load(f)
            
        for asset_name, asset_data in inventory.get("assets", {}).items():
            asset_tags = asset_data.get("tags", [])
            if all(tag in asset_tags for tag in tags):
                return asset_data
        return None

    @staticmethod
    def register_asset(asset_data: Dict):
        """Add or update an asset in the inventory with locking."""
        InventoryManager.acquire_lock()
        try:
            inventory = {"version": "1.1", "assets": {}}
            if os.path.exists(config.INVENTORY_FILE):
                with open(config.INVENTORY_FILE, "r") as f:
                    inventory = json.load(f)
            
            name = asset_data["name"]
            inventory["assets"][name] = asset_data
            inventory["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            
            os.makedirs(config.REGISTRY_DIR, exist_ok=True)
            
            with open(config.INVENTORY_FILE, "w") as f:
                json.dump(inventory, f, indent=2)
                
            # Expert Suggestion: Auto-backup
            if config.AUTO_BACKUP_REGISTRY:
                backup_file = config.INVENTORY_FILE + f".{time.strftime('%Y%m%d%H%M%S')}.bak"
                with open(backup_file, "w") as f:
                    json.dump(inventory, f, indent=2)
                    
        finally:
            InventoryManager.release_lock()
