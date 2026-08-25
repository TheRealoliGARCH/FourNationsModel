from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # The workflow/report contract is intentionally explicit: this script is
    # replaced only when every concrete provider callable is available.
    payload = {
        "status": "blocked_execution_configuration",
        "reason": "live provider entrypoint is not yet fully configured",
        "snapshot_manifest": None,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
