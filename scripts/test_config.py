import sys
from pathlib import Path

# Resolve project root
ROOT = Path(__file__).resolve().parent.parent

# Add project root to Python path
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import load_env

cfg = load_env()
print(cfg)
