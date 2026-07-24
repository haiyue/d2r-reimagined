#!/usr/bin/env python3
"""Import new Chinese wiki pages into Wiki.js SQLite database."""
import sqlite3, hashlib, os, re, json
from datetime import datetime

DB = 'server/wikijs-server/db.sqlite'
WIKI_ZH = 'wiki-zh'
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

conn = sqlite3.connect(os.path.join(BASE, DB))
c = conn.cursor()

c.execute("SELECT MAX(id) FROM pages")
next_page_id = (c.fetchone()[0] or 0) + 1
c.execute("SELECT MAX(id) FROM pageTree")
next_tree_id = (c.fetchone()[0] or 0) + 1

now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

pages_to_import = [
    ('Amazon.html', 'Amazon', '亚马逊'),
    ('Assassin.html', 'Assassin', '刺客'),
    ('Barbarian.html', 'Barbarian', '野蛮人'),
    ('Druid.html', 'Druid', '德鲁伊'),
    ('Necromancer.html', 'Necromancer', '死灵法师'),
    ('Paladin.html', 'Paladin', '圣骑士'),
    ('Sorceress.html', 'Sorceress', '法师'),
    ('AreaLevels.html', 'AreaLevels', 'Reimagined 区域等级'),
    ('Items/ArmorBases.html', 'Items/ArmorBases', '护甲基底'),
    ('Items/Charms.html', 'Items/Charms', '护符'),
    ('Items/Orbs.html', 'Items/Orbs', '宝珠'),
    ('Items/Runes.html', 'Items/Runes', '符文'),
    ('Items/WeaponBases.html', 'Items/WeaponBases', '武器基底'),
]

for file_name, db_path, title in pages_to_import:
    full_path = os.path.join(BASE, WIKI_ZH, file_name)
    if not os.path.exists(full_path):
        print(f"  MISSING: {file_name}")
        continue

    with open(full_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    front_match = re.match(r'<!--\s*\n(.*?)\n-->', raw, re.DOTALL)
    description = ''
    if front_match:
        fm = front_match.group(1)
        m = re.search(r'description:\s*(.*)', fm)
        if m:
            description = m.group(1).strip()
        content = raw[front_match.end():].strip()
    else:
        content = raw.strip()

    hash_val = hashlib.sha256(content.encode('utf-8')).hexdigest()

    c.execute("SELECT id FROM pages WHERE path=? AND localeCode='zh'", (db_path,))
    if c.fetchone():
        print(f"  EXISTS: {db_path}")
        continue

    c.execute("""INSERT INTO pages (id, path, hash, title, description, isPrivate, isPublished,
         contentType, createdAt, updatedAt, editorKey, localeCode, creatorId, authorId, extra)
         VALUES (?, ?, ?, ?, ?, 0, 1, 'html', ?, ?, 'ckeditor', 'zh', 1, 1, '{}')""",
        (next_page_id, db_path, hash_val, title, description, now, now))
    c.execute("UPDATE pages SET content=? WHERE id=?", (content, next_page_id))

    depth = db_path.count('/')
    parent = None
    if depth > 0:
        pp = '/'.join(db_path.split('/')[:-1])
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
