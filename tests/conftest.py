import sys
from pathlib import Path

# add repo root to sys.path so tests can import core.*, etc.
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))