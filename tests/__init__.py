"""Test bootstrap for local src-layout execution."""

from __future__ import annotations

import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
src_dir_str = str(SRC_DIR)
if src_dir_str not in sys.path:
    sys.path.insert(0, src_dir_str)
