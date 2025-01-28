#!/usr/bin/env python3
"""Main entry point for Like4Book application."""

import os
import sys
from pathlib import Path

# Add project root to path to allow imports
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)

try:
    # Import and run main function
    from src.main import main
    main()
except KeyboardInterrupt:
    sys.exit(0)
except Exception as e:
    print(f"[Error] {str(e).capitalize()}!")
    sys.exit(1)