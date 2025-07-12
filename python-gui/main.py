#!/usr/bin/env python3
"""
MiraC2 Python GUI
Cyberpunk-styled GUI interface for the MiraC2 system
"""

import sys
import asyncio
import json
from pathlib import Path

# Add the mira_gui package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mira_gui.main_window import MiraMainWindow
from mira_gui.backend_client import BackendClient
from mira_gui.config import load_config

def main():
    """Main entry point for the MiraC2 GUI application"""
    try:
        # Load configuration
        config = load_config()
        
        # Create backend client
        backend_client = BackendClient(
            host=config.get('server_host', 'localhost'),
            port=config.get('server_port', 8080)
        )
        
        # Create and run the main window
        app = MiraMainWindow(backend_client, config)
        app.run()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error starting MiraC2 GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()