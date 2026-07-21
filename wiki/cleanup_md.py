#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import re

def cleanup_md(md_path):
    """Remove excessive blank lines and clean up markdown"""
    text = md_path.read_text(encoding='utf-8')
    
    # Replace multiple consecutive newlines with just 2
    text = re.sub(r'\n\n\n+', '\n\n', text)
    
    # Remove trailing whitespace
    lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    md_path.write_text(text + '\n', encoding='utf-8')

# Process markdown files
root = Path('haiyue')
for md_file in root.glob('*.md'):
    print(f'Cleaning {md_file.name}...')
    cleanup_md(md_file)
    print(f'✓ Cleaned {md_file.name}')
