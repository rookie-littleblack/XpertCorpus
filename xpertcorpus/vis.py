"""
Entry script for JSONL visualization tool launcher.

@author: rookielittleblack
@date:   2025-08-15
"""

import os
import sys
import subprocess

from pathlib import Path
from xpertcorpus.utils.xlogger import xlogger


def main():
    """Launch the visualization tool."""
    
    # Get script directory
    script_dir = Path(__file__).parent.parent
    xvis_path = script_dir / "xpertcorpus" / "utils" / "xvis.py"
    
    if not xvis_path.exists():
        error_msg = f"Error: Cannot find xvis.py file: {xvis_path}"
        print(error_msg)
        xlogger.error(error_msg)
        sys.exit(1)
    
    xlogger.info("🚀 Starting JSONL corpus visualization tool...")
    xlogger.info(f"📍 Tool path: {xvis_path}")
    
    print("🚀 Starting JSONL corpus visualization tool...")
    print(f"📍 Tool path: {xvis_path}")
    print("\n📝 Usage Instructions:")
    print("1. Enter full paths to JSONL files on the left (one per line)")
    print("2. Set maximum number of records (default: 1000)")
    print("3. Click 'Load Files'")
    print("4. Use search and navigation features to browse data")
    print("\n🌐 Browser will open automatically. If not, please visit the displayed URL manually")
    print("-" * 50)
    
    try:
        # Check if streamlit is installed
        subprocess.run([sys.executable, "-c", "import streamlit"], 
                      check=True, capture_output=True)
        xlogger.info("Streamlit dependency check passed")
    except subprocess.CalledProcessError:
        error_msg = "❌ Error: Streamlit not installed"
        install_msg = "Please run: pip install streamlit pandas markdown"
        print(error_msg)
        print(install_msg)
        xlogger.error(f"{error_msg}. {install_msg}")
        sys.exit(1)
    
    # Launch streamlit application
    try:
        xlogger.info("Launching Streamlit application...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(xvis_path),
            "--server.address", "0.0.0.0",
            "--server.port", "8501",
            "--browser.serverAddress", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        stop_msg = "\n👋 Visualization tool stopped"
        print(stop_msg)
        xlogger.info("Visualization tool stopped by user")
    except subprocess.CalledProcessError as e:
        error_msg = f"❌ Launch failed: {e}"
        print(error_msg)
        xlogger.error(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()