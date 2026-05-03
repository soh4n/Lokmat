"""
LokMat Tests — Shared fixtures for unit and integration tests.

Per GEMINI.md: pytest + pytest-asyncio for all test layers.
"""

import sys
from pathlib import Path

# Ensure the project root is in the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
