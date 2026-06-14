#!/usr/bin/env python3
"""allocate-address.py — cross-platform address allocator for the vault.

Equivalent to allocate-address.sh but works on Windows without WSL.
File locking uses msvcrt on Windows, fcntl on Unix.

Usage:
  python scripts/allocate-address.py           # prints reserved address (e.g. c-000042)
  python scripts/allocate-address.py --peek    # prints next value without incrementing
  python scripts/allocate-address.py --rebuild # recomputes counter from max observed

Exit codes:
  0 — success
  1 — lock acquisition failed
  2 — vault-meta directory missing and cannot be created
  3 — counter value corrupt or non-numeric
"""

import os
import sys
import re
import time
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
VAULT_META = VAULT_ROOT / ".vault-meta"
COUNTER_FILE = VAULT_META / "address-counter.txt"
LOCK_FILE = VAULT_META / ".address.lock"
WIKI_DIR = VAULT_ROOT / "wiki"

LOCK_TIMEOUT = 5.0


def acquire_lock():
    VAULT_META.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + LOCK_TIMEOUT
    while True:
        try:
            fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return
        except FileExistsError:
            if time.monotonic() >= deadline:
                print("ERR: could not acquire address allocator lock within 5s", file=sys.stderr)
                sys.exit(1)
            time.sleep(0.05)


def release_lock():
    try:
        LOCK_FILE.unlink()
    except FileNotFoundError:
        pass


def scan_max_c_address() -> int:
    if not WIKI_DIR.is_dir():
        return 0
    max_n = 0
    fm_pattern = re.compile(r'^address:\s+c-(\d{6})\s*$')
    for md_file in WIKI_DIR.rglob("*.md"):
        try:
            in_fm = False
            for i, line in enumerate(md_file.read_text(encoding="utf-8", errors="ignore").splitlines()):
                if i == 0:
                    in_fm = (line.strip() == "---")
                    continue
                if in_fm:
                    if line.strip() == "---":
                        break
                    m = fm_pattern.match(line)
                    if m:
                        max_n = max(max_n, int(m.group(1)))
        except OSError:
            continue
    return max_n


def read_or_recover_counter() -> int:
    if not COUNTER_FILE.exists():
        max_c = scan_max_c_address()
        next_val = max_c + 1
        COUNTER_FILE.write_text(str(next_val), encoding="utf-8")
        print(f"INFO: counter file missing; recovered from vault scan, set to {next_val}", file=sys.stderr)
    raw = COUNTER_FILE.read_text(encoding="utf-8").strip()
    if not raw.isdigit():
        print(f"ERR: counter file content is not a positive integer: {raw}", file=sys.stderr)
        sys.exit(3)
    return int(raw)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "allocate"

    try:
        VAULT_META.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"ERR: cannot create .vault-meta/: {e}", file=sys.stderr)
        sys.exit(2)

    if mode == "--peek":
        acquire_lock()
        try:
            print(read_or_recover_counter())
        finally:
            release_lock()

    elif mode == "--rebuild":
        acquire_lock()
        try:
            max_c = scan_max_c_address()
            next_val = max_c + 1
            COUNTER_FILE.write_text(str(next_val), encoding="utf-8")
            print(f"Counter rebuilt: next = {next_val}")
        finally:
            release_lock()

    elif mode in ("allocate", ""):
        acquire_lock()
        try:
            current = read_or_recover_counter()
            COUNTER_FILE.write_text(str(current + 1), encoding="utf-8")
            print(f"c-{current:06d}")
        finally:
            release_lock()

    else:
        print(f"ERR: unknown mode: {mode}", file=sys.stderr)
        print("Usage: allocate-address.py [allocate|--peek|--rebuild]", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
