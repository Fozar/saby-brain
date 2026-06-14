#!/usr/bin/env python3
"""sabydoc-extract.py — extract plain text from a .sabydoc file.

Usage:
    python scripts/sabydoc-extract.py <path-to-file.sabydoc>

Outputs plain text to stdout. Strips all component metadata, UUIDs,
style keywords, and formatting — keeps only readable content and URLs.
"""

import json
import re
import sys
import zipfile
from pathlib import Path

# Force UTF-8 output on all platforms (avoids CP1252/CP866 garbling on Windows)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
COMPONENT_RE = re.compile(r'[A-Za-z][A-Za-z0-9_]*/[A-Za-z]')
STYLE_WORDS = {'default', 'bold', 'italic', 'underline', 'strikethrough',
               'frame', 'removable', 'selectable', '1', '2', '3', '4', '5',
               '6', 'true', 'false', 'null', 'left', 'right', 'center'}


def is_noise(s: str) -> bool:
    s = s.strip()
    if not s or len(s) <= 1:
        return True
    if UUID_RE.match(s):
        return True
    if COMPONENT_RE.search(s):
        return True
    if s.lower() in STYLE_WORDS:
        return True
    if s.isdigit():
        return True
    return False


def walk(node, out: list):
    if isinstance(node, str):
        if not is_noise(node):
            out.append(node.strip())
    elif isinstance(node, list):
        for item in node:
            walk(item, out)
    elif isinstance(node, dict):
        # Extract hrefs as plain references
        for key, val in node.items():
            if key == 'href' and isinstance(val, str) and val.startswith('http'):
                out.append(f'[{val}]')
            elif isinstance(val, (list, dict)):
                walk(val, out)


def extract(path: str) -> str:
    with zipfile.ZipFile(path) as z:
        members = z.namelist()
        # index.site has the full content
        if 'index.site' in members:
            with z.open('index.site') as f:
                data = json.loads(f.read().decode('utf-8'))
        elif 'content.json' in members:
            with z.open('content.json') as f:
                data = json.loads(f.read().decode('utf-8'))
        else:
            return ''

    parts = []

    # Title
    name = data.get('name', '')
    if name:
        parts.append(f'# {name}')
        parts.append('')

    # TOC
    toc = data.get('propertyValues', {}).get('tableOfContents', [])
    if toc:
        parts.append('## Table of Contents')
        for entry in toc:
            indent = '  ' * (int(entry.get('level', 1)) - 1)
            parts.append(f'{indent}- {entry.get("text", "")}')
        parts.append('')

    # Pages
    pages = data.get('pages', [])
    for pg in pages:
        pg_name = pg.get('name')
        if pg_name:
            parts.append(f'## {pg_name}')
        content = pg.get('content', [])
        out = []
        walk(content, out)
        # Deduplicate consecutive identical lines and join
        prev = None
        for line in out:
            if line != prev:
                parts.append(line)
                prev = line
        parts.append('')

    return '\n'.join(parts)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: sabydoc-extract.py <file.sabydoc>', file=sys.stderr)
        sys.exit(1)
    print(extract(sys.argv[1]))
