import sys
from pathlib import Path

# make the repo root importable (parser, models) when running plain `pytest`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
