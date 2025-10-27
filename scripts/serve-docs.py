#!/usr/bin/env python3
"""
Script to serve documentation locally for development.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Serve documentation locally."""
    project_root = Path(__file__).parent.parent

    print("Starting MkDocs development server...")
    print("Documentation will be available at: http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the server")

    try:
        subprocess.run(
            [sys.executable, "-m", "mkdocs", "serve", "--dev-addr", "127.0.0.1:8000"],
            cwd=project_root,
            check=True,
        )
    except KeyboardInterrupt:
        print("\nStopping documentation server...")
    except subprocess.CalledProcessError as e:
        print(f"Error running MkDocs: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
