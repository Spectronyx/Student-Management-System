#!/usr/bin/env python3
"""
==============================================================================
STUDENT MANAGEMENT SYSTEM - MAIN ENTRY POINT
Architecture: Python 3 + MySQL | Multi-Layered OOP (UI -> Service -> Repository -> DB)
==============================================================================
"""

import sys
import os
from database.connection import db_manager
from ui.login import LoginUI
from utils.helpers import Color, print_header, print_success, print_error, print_info

def initialize_system():
    """Verifies database connection and initializes tables/seed data if required."""
    print_header("STUDENT MANAGEMENT SYSTEM - BOOTSTRAP INITIALIZATION")
    print_info("Connecting to MySQL Database...")
    try:
        db_manager.initialize_schema()
        print_success("Database connection verified and schema synced successfully!")
    except Exception as e:
        print_error(f"Failed to initialize database: {e}")
        print_info("Please check database configuration in .env or config.py")
        sys.exit(1)

def main():
    try:
        initialize_system()
        login_ui = LoginUI()
        login_ui.start()
    except KeyboardInterrupt:
        print("\n\n" + Color.YELLOW + "System interrupted by user. Exiting safely..." + Color.END)
        sys.exit(0)
    except Exception as e:
        print_error(f"Fatal System Exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
