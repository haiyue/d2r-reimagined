#!/usr/bin/env python3
"""Import new Chinese recipe pages into Wiki.js SQLite database."""
import sqlite3, hashlib, os, re, json
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, 'server', 'wikijs-server', 'db.sqlite')
WIKI_ZH = os.path.join(BASE, 'wiki-zh')

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("SELECT MAX(id) FROM pages")
next_page_id = (c.fetchone()[0] or 0) + 1
c.execute("SELECT MAX(id) FROM pageTree")
next_tree_id = (c.fetchone()[0] or 0) + 1

now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

pages = [
    ('recipes.md', 'recipes', '配方', 'markdown'),
    ('recipes/Crafting.html', 'recipes/Crafting', '物品合成', 'html'),
    ('recipes/CubeRecipes.html', 'recipes/CubeRecipes', '合成配方', 'html'),
    ('recipes/ISCStatLimits.html', 'recipes/ISCStatLimits', '物品属性限制', 'html'),
    ('recipes/ItemEnchants.html', 'recipes/ItemEnchants', '物品附魔', 'html'),
]

for file_name, db_path, title, ctype in pages:
    full_path = os.path.join(WIKI_ZH, file_name)
    if not os.path.exists(full_path):
        print(f"  MISSING: {file_name}")
        continue

    with open(full_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    # Parse frontmatter for .md files
    content = raw
    description = ''
    if file_name.endswith('.md'):
        fm_match = re.match(r'^---\s*\n(.*?)\n---\n', raw, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            m = re.search(r'^description:\s*(.*)', fm, re.MULTILINE)
            if m:
                description = m.group(1).strip()
            content = raw[fm_match.end():].strip()

    hash_val = hashlib.sha256(content.encode('utf-8')).hexdigest()

    c.execute("SELECT id FROM pages WHERE path=? AND localeCode='zh'", (db_path,))
    if c.fetchone():
        print(f"  EXISTS: {db_path}")
        continue

    editor = 'markdown' if ctype == 'markdown' else 'ckeditor'
    c.execute("""INSERT INTO pages (id, path, hash, title, description, isPrivate, isPublished,
         contentType, createdAt, updatedAt, editorKey, localeCode, creatorId, authorId, extra)
         VALUES (?, ?, ?, ?, ?, 0, 1, ?, ?, ?, ?, 'zh', 1, 1, '{}')""",
        (next_page_id, db_path, hash_val, title, description, ctype, now, now, editor))
    c.execute("UPDATE pages SET content=? WHERE id=?", (content, next_page_id))

    depth = db_path.count('/')
    parent = None
    if depth > 0:
        pp = db_path.rsplit('/', 1)[0]
        c.execute("SELECT id FROM pageTree WHERE path=? AND localeCode='zh'", (pp,))
        r = c.fetchone()
        if r:
            parent = r[0]

    ancestors = []
    if parent:
        c.execute("SELECT ancestors FROM pageTree WHERE id=?", (parent,))
        pa = c.fetchone()
        if pa and pa[0]:
            ancestors = json.loads(pa[0])
        ancestors.append({"id": parent})

    c.execute("""INSERT INTO pageTree (id, path, depth, title, isPrivate, isFolder, pageId, parent, localeCode, ancestors)
         VALUES (?, ?, ?, ?, 0, 0, ?, ?, ?, ?)""",
        (next_tree_id, db_path, depth, title, next_page_id, parent, 'zh', json.dumps(ancestors)))

    print(f"  IMPORTED: {db_path} ({title})")
    next_page_id += 1
    next_tree_id += 1

conn.commit()
conn.close()
print("Done!")
