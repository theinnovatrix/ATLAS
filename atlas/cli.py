"""
Module: atlas.cli
Purpose: Command-line entry point for the Atlas assistant foundation.
Author: NOVA Development Agent
Version: 0.1.0
Dependencies: standard library, atlas.core
Last Updated: 2026-04-26
"""

from __future__ import annotations

import argparse
import json

from atlas.core.orchestrator import AtlasOrchestrator
from atlas.core.safety import CONFIRMATION_TOKEN


def build_parser() -> argparse.ArgumentParser:
    """Build the Atlas CLI parser."""
    parser = argparse.ArgumentParser(description="Atlas local-first desktop assistant")
    parser.add_argument("command", nargs="*", help="Natural-language command for Atlas")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help=f"Confirm a risky action using {CONFIRMATION_TOKEN}",
    )
    parser.add_argument("--json", action="store_true", help="Print structured JSON output")
    return parser


def main() -> int:
    """Execute a command from the terminal."""
    args = build_parser().parse_args()
    command = " ".join(args.command).strip()
    if not command:
        command = "features"

    orchestrator = AtlasOrchestrator()
    token = CONFIRMATION_TOKEN if args.confirm else None
    response = orchestrator.execute_text(command, confirmation_token=token)
    if args.json:
        print(
            json.dumps(
                {
                    "ok": response.ok,
                    "message": response.message,
                    "intent": response.intent,
                    "risk": response.risk.value,
                    "data": response.data,
                    "requires_confirmation": response.requires_confirmation,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(response.message)
    return 0 if response.ok or response.requires_confirmation else 1


if __name__ == "__main__":
    raise SystemExit(main())
