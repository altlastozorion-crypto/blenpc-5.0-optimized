import os
import platform
import logging
from typing import Any, Dict

"""BlenPC v5.1.1 - Expert-Driven Configuration System."""

# --- 1. I18N & UI SETTINGS (Expert: UX Designer & Technical Writer) ---
I18N_LANGUAGE = os.getenv("BLENPC_LANG", "tr")  # Default to Turkish
CLI_COLOR_THEME = "modern"  # options: modern, classic, mono
LOG_FORMAT_EXTENDED = '%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s'

# --- 2. LOGGING CONFIGURATION (Expert: DevOps Engineer) ---
LOG_LEVEL = os.getenv("MF_LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("MF_LOG_FILE", None)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT_EXTENDED,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE) if LOG_FILE else logging.NullHandler()
    ]
)
logger = logging.getLogger("blenpc")

# --- 3. PATH MANAGEMENT (Expert: Software Architect) ---
# Dynamic Project Root Detection
# Current file is in PROJECT_ROOT/src/blenpc/config.py
# So PROJECT_ROOT is three levels up
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Expert Fix: Use cross-platform path joining
LIBRARY_DIR = os.path.join(PROJECT_ROOT, "_library")
REGISTRY_DIR = os.path.join(PROJECT_ROOT, "_registry")
INVENTORY_FILE = os.path.join(REGISTRY_DIR, "inventory.json")
SLOTS_FILE = os.path.join(REGISTRY_DIR, "slot_types.json")
TAGS_FILE = os.path.join(REGISTRY_DIR, "tag_vocabulary.json")

# --- 4. BLENDER EXECUTABLE (Expert: Blender Pipeline Specialist) ---
def get_blender_path():
    """Expert Fix: Improved Windows Blender discovery."""
    env_path = os.getenv("BLENDER_PATH") or os.getenv("BLENDER_EXECUTABLE")
    if env_path and os.path.exists(env_path):
        return env_path
    
    if platform.system() == "Windows":
        # Standard installation paths for Blender 5.0
        paths = [
            r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
            os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender\blender.exe")
        ]
        for p in paths:
            if os.path.exists(p): return p
        return "blender.exe" # Fallback to PATH
    elif platform.system() == "Darwin":
        return "/Applications/Blender.app/Contents/MacOS/Blender"
    else:
        return "/usr/bin/blender"

BLENDER_PATH = get_blender_path()
HEADLESS_ARGS = ["--background", "--python"]

# --- 5. PERFORMANCE & LIMITS (Expert: System Engineer) ---
MAX_WORKER_PROCESSES = os.cpu_count() or 4
STRICT_VALIDATION = True  # Expert Fix: Ensure production-ready assets
CACHE_ENABLED = True
AUTO_BACKUP_REGISTRY = True
BLENDER_MEMORY_WARN = 3000  # MB

# --- 6. ARCHITECTURAL CONSTANTS (Expert: Architect) ---
GRID_UNIT = 0.25
STORY_HEIGHT = 3.0
WALL_THICKNESS_BASE = 0.2
DEFAULT_UNIT_SYSTEM = "metric"  # metric or imperial
EXPORT_PRECISION = 4  # decimal places for geometry

# --- 7. MATH CONSTANTS ---
PHI = (1 + 5**0.5) / 2
GOLDEN_RATIO_VARIATION = 0.04

# --- 8. INVENTORY LOCKING (Expert: Cyber Security Specialist) ---
INVENTORY_LOCK_TIMEOUT = 5
INVENTORY_LOCK_POLL_INTERVAL = 0.1
INVENTORY_LOCK_STALE_AGE = 60

# --- 9. EXPORT SETTINGS ---
EXPORT_FORMATS_SUPPORTED = ["glb", "blend", "fbx", "obj"]

# --- 10. DEFAULTS ---
DEFAULT_ROOF_PITCH = 35.0
WINDOW_SILL_HEIGHT_DEFAULT = 1.2
WINDOW_DEFAULT_WIDTH = 1.0
WINDOW_DEFAULT_HEIGHT = 1.2
TEST_TIMEOUT_DEFAULT = 120

def get_settings() -> Dict[str, Any]:
    """Returns all settings as a dictionary."""
    return {k: v for k, v in globals().items() if k.isupper()}
