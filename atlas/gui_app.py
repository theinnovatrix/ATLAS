"""
Module: atlas.gui_app
Purpose: Console entry point for launching the Atlas GUI.
Author: NOVA Development Agent
Version: 0.7.0
Dependencies: atlas.gui
Last Updated: 2026-04-27
"""

from __future__ import annotations

from atlas.gui.main_window import run_gui


def main() -> int:
    """Launch the Atlas GUI."""
    try:
        return run_gui()
    except RuntimeError as error:
        print(error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
