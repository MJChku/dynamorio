#!/usr/bin/env python3
"""Regression for DynamoRIO close_range scalability and subprocess semantics."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time


PROBE = r"""
import subprocess
import sys
import threading
import time

count = int(sys.argv[1])
release = threading.Event()
threads = [threading.Thread(target=release.wait) for _ in range(count)]
for thread in threads:
    thread.start()

started = time.monotonic()
for iteration in range(10):
    result = subprocess.run(
        [sys.executable, "-c", "import sys; sys.stdout.write('x')"],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    assert result.stdout == "x"
elapsed = time.monotonic() - started

release.set()
for thread in threads:
    thread.join()
print(f"GXVM_DR_CLOSE_RANGE_PASS threads={count} launches=10 elapsed={elapsed:.6f}")
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--drrun", required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    for thread_count in (0, 128):
        started = time.monotonic()
        completed = subprocess.run(
            [
                args.drrun,
                "-quiet",
                "-no_follow_children",
                "-opt_speed",
                "--",
                args.python,
                "-c",
                PROBE,
                str(thread_count),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=20,
        )
        wall = time.monotonic() - started
        if completed.returncode != 0 or "GXVM_DR_CLOSE_RANGE_PASS" not in completed.stdout:
            raise RuntimeError(
                f"close_range probe failed for {thread_count} threads\n"
                f"{completed.stdout}"
            )
        # The pre-fix path needs roughly 55 seconds for one launch on the GX
        # host.  Keep generous CI headroom while making that regression fail
        # deterministically rather than silently timing out a framework run.
        if wall >= 20:
            raise RuntimeError(
                f"close_range probe exceeded scalability gate: {wall:.3f}s"
            )
        print(completed.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
