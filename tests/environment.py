"""Entry point that behave requires: it loads hooks only from a file named environment.py.

The hooks themselves live in test_setup.py, next to this file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_setup import after_scenario, after_step, before_all, before_scenario  # noqa: E402, F401
