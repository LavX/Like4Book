"""Main entry point for the Like4Book application."""

import os
import sys
from pathlib import Path

# Add project root to path to allow imports
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from src.interfaces.cli.menu import MenuManager
from src.interfaces.cli.display import DisplayManager
from src.core.exceptions import Like4BookError

def main():
    """Main application entry point."""
    try:
        # Initialize display and show banner
        display = DisplayManager()
        display.show_banner()
        
        # Initialize and run menu system
        menu = MenuManager()
        menu.run()
        
    except Like4BookError as e:
        display.show_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        sys.exit(0)
    except Exception as e:
        # Catch any unexpected errors
        display.show_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()