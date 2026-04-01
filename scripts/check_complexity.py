from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Iterable


MAX_COMPLEXITY = 8
RADON_COMMAND = ["poetry", "run", "radon", "cc", "src/", "-j"]


def main() -> int:
    """Run project complexity checks and print any violations."""

    process = subprocess.run(RADON_COMMAND, capture_output=True, text=True, check=False)
    if process.returncode != 0:
        print(process.stdout)
        print(process.stderr, file=sys.stderr)
        return process.returncode

    data = json.loads(process.stdout or "{}")
    failures = list(find_failures(data))
    if not failures:
        print(f"Cyclomatic complexity check passed (max <= {MAX_COMPLEXITY}).")
        return 0

    print(f"Cyclomatic complexity check failed. Threshold is {MAX_COMPLEXITY}.")
    for item in failures:
        print(
            f"- {item['path']}:{item['line']} {item['type']} {item['name']} "
            f"has complexity {item['complexity']}"
        )
    return 1


def find_failures(data: dict[str, list[dict[str, object]]]) -> Iterable[dict[str, object]]:
    """Yield code blocks that exceed the configured complexity limit."""

    for path, blocks in data.items():
        for block in blocks:
            complexity = block.get("complexity")
            if not isinstance(complexity, int) or complexity <= MAX_COMPLEXITY:
                continue
            yield {
                "path": path,
                "line": block.get("lineno", 0),
                "type": block.get("type", "block"),
                "name": block.get("name", "<unknown>"),
                "complexity": complexity,
            }


if __name__ == "__main__":
    raise SystemExit(main())
