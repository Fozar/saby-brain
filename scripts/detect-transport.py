#!/usr/bin/env python3
"""Detect vault transport mode and write result to .vault-meta/transport.json."""

import json
import os
import shutil
import sys
from pathlib import Path

VAULT_ROOT = Path(__file__).parent.parent
VAULT_META = VAULT_ROOT / ".vault-meta"
TRANSPORT_FILE = VAULT_META / "transport.json"


def detect_transport() -> str:
    # 1. obsidian-cli binary takes precedence
    if shutil.which("obsidian-cli"):
        return "cli"

    # 2. MCP server env vars (set by MCP clients before launching Claude)
    if os.environ.get("OBSIDIAN_MCP_URL") or os.environ.get("MCP_OBSIDIAN_URL"):
        return "mcp-obsidian"

    if os.environ.get("MCPVAULT_URL") or os.environ.get("MCP_VAULT_URL"):
        return "mcpvault"

    # 3. Default: direct filesystem access via Claude Read/Write/Glob/Grep tools
    return "filesystem"


def main() -> None:
    if not VAULT_META.exists():
        print(f"ERROR: .vault-meta not found at {VAULT_META}", file=sys.stderr)
        sys.exit(2)

    transport = detect_transport()
    data = {"transport": transport, "detected_by": "detect-transport.py"}

    TRANSPORT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"transport: {transport}")
    print(f"written:   {TRANSPORT_FILE}")


if __name__ == "__main__":
    main()
