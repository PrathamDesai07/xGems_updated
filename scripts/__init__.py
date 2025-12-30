"""
Initialize the scripts package and provide common imports.
"""

from pathlib import Path
import sys

# Add scripts directory to Python path
SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Common imports that will be used across modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Import configuration
from config import *

__all__ = [
    'np', 'pd', 'plt',
    'SCRIPTS_DIR', 'PROJECT_ROOT',
]
