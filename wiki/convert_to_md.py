#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import sys

def convert_html_to_md(html_path):
    """Convert HTML file to Markdown"""
    print(f'Processing {html_path.name}...', file=sys.stderr)
    
    text = html_path.read_text(encoding='utf-8')
    soup = BeautifulSoup(text, 'html.parser')
    
    # Remove unwanted tags
    for tagname in ['script', 'style', 'noscript', 'svg', 'link', 'meta', 'head', 'iframe']:
        for tag in soup.find_all(tagname):
            tag.decompose()
    
    for tagname in ['nav', 'header', 'footer', 'aside', 'form', 'button', 'input', 'select', 'label']:
        for tag in soup.find_all(tagname):
            tag.decompose()
    
    # Get main content only
    card_container = soup.find(class_='card-container')
    if card_container:
        content = card_container
    else:
        content = soup.body or soup
    
    markdown = md(str(content), heading_style='ATX', bullets='*')
    
    # Write markdown file
    out_path = html_path.with_suffix('.md')
    out_path.write_text(markdown, encoding='utf-8')
    print(f'✓ Wrote {out_path.name}', file=sys.stderr)
    return out_path

# Process files in haiyue folder
root = Path('haiyue')
files = [
    root / 'Runewords _D2R Reimagined.html',
    root / 'Cube Recipes _D2R Reimagined.html'
]

for html_path in files:
    if html_path.exists():
        try:
            out_path = convert_html_to_md(html_path)
        except Exception as e:
            print(f'✗ Error processing {html_path.name}: {e}', file=sys.stderr)
    else:
        print(f'✗ {html_path.name} not found', file=sys.stderr)
