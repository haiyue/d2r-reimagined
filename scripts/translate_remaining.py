#!/usr/bin/env python3
"""Translate all remaining English wiki pages to Chinese and import into Wiki.js DB."""
import sqlite3, hashlib, os, re, json
from datetime import datetime
import subprocess

BASE = '/Users/wangxinlei/haiyue/d2r-reimagined'
DB = os.path.join(BASE, 'server', 'wikijs-server', 'db.sqlite')
WIKI_ZH = os.path.join(BASE, 'wiki-zh')

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("SELECT MAX(id) FROM pages")
next_page_id = (c.fetchone()[0] or 0) + 1
c.execute("SELECT MAX(id) FROM pageTree")
next_tree_id = (c.fetchone()[0] or 0) + 1

now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

# === PATCH NOTES ===
# English pages to copy (with data preserved, Chinese metadata)
patch_notes = [
    # (path, zh_title, zh_desc)
    ('Patch_Notes/2-0-0', '版本 2.0.0', 'D2R Reimagined 2.0.0 版本更新日志'),
    ('Patch_Notes/2-0-1', '版本 2.0.1', 'D2R Reimagined 2.0.1 版本更新日志'),
    ('Patch_Notes/2-0-2', '版本 2.0.2', 'D2R Reimagined 2.0.2 版本更新日志'),
    ('Patch_Notes/2-0-3', '版本 2.0.3', 'D2R Reimagined 2.0.3 版本更新日志'),
    ('Patch_Notes/2-0-4', '版本 2.0.4', 'D2R Reimagined 2.0.4 版本更新日志'),
    ('Patch_Notes/2-0-5', '版本 2.0.5', 'D2R Reimagined 2.0.5 版本更新日志'),
    ('Patch_Notes/2-1-0', '版本 2.1.0', 'D2R Reimagined 2.1.0 版本更新日志'),
    ('Patch_Notes/2-1-1', '版本 2.1.1', 'D2R Reimagined 2.1.1 版本更新日志'),
    ('Patch_Notes/2-1-2', '版本 2.1.2', 'D2R Reimagined 2.1.2 版本更新日志'),
    ('Patch_Notes/2-2-0', '版本 2.2.0', 'D2R Reimagined 2.2.0 版本更新日志'),
    ('Patch_Notes/3-0-0', '版本 3.0.0', 'D2R Reimagined 3.0.0 版本更新日志'),
    ('Patch_Notes/3-0-1', 'D2R Reimagined 3.0.1', 'D2R Reimagined 3.0.1 版本更新日志'),
    ('Patch_Notes/3-0-2', 'D2R Reimagined 3.0.2', 'D2R Reimagined 3.0.2 版本更新日志'),
    ('Patch_Notes/3-0-3', 'D2R Reimagined 3.0.3', 'D2R Reimagined 3.0.3 版本更新日志'),
    ('Patch_Notes/3-0-4', 'D2R Reimagined 3.0.4', 'D2R Reimagined 3.0.4 版本更新日志'),
    ('Patch_Notes/3-0-5', 'D2R Reimagined 3.0.5', 'D2R Reimagined 3.0.5 版本更新日志'),
    ('Patch_Notes/3-0-6', 'D2R Reimagined 3.0.6', 'D2R Reimagined 3.0.6 版本更新日志'),
    ('Patch_Notes/3-0-8', 'D2R Reimagined 3.0.8', 'D2R Reimagined 3.0.8 版本更新日志'),
    ('Patch_Notes/D2RR_3_0_0_Item_Changes', 'D2RR 3.0.0 物品变更', 'D2R Reimagined 3.0.0 物品变更文档'),
]

def get_en_content(path):
    c.execute("SELECT content, title, contentType FROM pages WHERE path=? AND localeCode='en'", (path,))
    row = c.fetchone()
    return row if row else (None, None, None)

def import_page(db_path, content, title, desc, ctype):
    global next_page_id, next_tree_id
    if not content:
        return False

    # For patch notes: translate key headers
    zh_content = content

    # Translate common section headers
    replacements = {
        '# Class Changes': '# 职业改动',
        '# General Changes': '# 通用改动',
        '# Skill Changes': '# 技能改动',
        '# Item Changes': '# 物品改动',
        '# Bug Fixes': '# 错误修复',
        '# Quality of Life': '# 便利性改进',
        '# New Features': '# 新功能',
        '# Balance Changes': '# 平衡性调整',
        '## Amazon': '## 亚马逊',
        '## Assassin': '## 刺客',
        '## Barbarian': '## 野蛮人',
        '## Druid': '## 德鲁伊',
        '## Necromancer': '## 死灵法师',
        '## Paladin': '## 圣骑士',
        '## Sorceress': '## 法师',
        '## Warlock': '## 术士',
        # Translate patch note specific version indicators
        '## What\'s New': '## 新增内容',
        '## Changes': '## 变更',
        '## Fixes': '## 修复',
        '## New Runewords': '## 新符文之语',
        '## New Items': '## 新物品',
        '## New Recipes': '## 新配方',
        '## Reworked Skills': '## 技能重做',
        '/en/': '/zh/',
    }
    for old, new in replacements.items():
        zh_content = zh_content.replace(old, new)

    hash_val = hashlib.sha256(zh_content.encode('utf-8')).hexdigest()

    c.execute("SELECT id FROM pages WHERE path=? AND localeCode='zh'", (db_path,))
    if c.fetchone():
        print(f"  EXISTS: {db_path}")
        return False

    editor = 'markdown' if ctype == 'markdown' else 'ckeditor'
    c.execute("""INSERT INTO pages (id, path, hash, title, description, isPrivate, isPublished,
         contentType, createdAt, updatedAt, editorKey, localeCode, creatorId, authorId, extra)
         VALUES (?, ?, ?, ?, ?, 0, 1, ?, ?, ?, ?, 'zh', 1, 1, '{}')""",
        (next_page_id, db_path, hash_val, title, desc, ctype, now, now, editor))
    c.execute("UPDATE pages SET content=? WHERE id=?", (zh_content, next_page_id))

    # pageTree
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
    return True

# Import all patch notes
print("=== Patch Notes ===")
count = 0
for path, zh_title, zh_desc in patch_notes:
    content, en_title, ctype = get_en_content(path)
    if import_page(path, content, zh_title, zh_desc, ctype):
        count += 1
print(f"  {count} patch notes imported")

# === BUILDS ===
builds = [
    # (path, zh_title)
    ('Builds/Amazon/GlacialArrowBowazonProdigy', '冰川箭弓马 - Prodigy'),
    ('Builds/Amazon/Jerrdan_Bow', '3.x 更新！Jerrdan 的物理弓马'),
    ('Builds/Amazon/LastFables', 'LastFables 扫射/导引箭弓马'),
    ('Builds/Amazon/Prodigy_CS_Spearzon', 'Prodigy 的充能一击矛马'),
    ('Builds/Amazon/Prodigy_PhysBowazon', 'Prodigy 的多重箭/导引箭弓马'),
    ('Builds/Amazon/ShoobyLightJava', 'Shooby 的闪电标枪马'),
    ('Builds/Amazon/ShoobyShotgunAmazon', 'Shooby 的闪电扫射亚马逊'),
    ('Builds/Amazon/myama', '95%+ CB/DS/PA 全能弓马'),
    ('Builds/Assassin/BaftShadowTrapSin', 'Baft 的暗影宗师陷阱刺客 3.0.10+'),
    ('Builds/Assassin/IceKicksin', '冰刃 + 龙尾踢刺客'),
    ('Builds/Assassin/ProdigyBladeFurySin', 'Prodigy 的刃之怒刺客'),
    ('Builds/Assassin/SinNSpin', '3.x 更新！毒旋风刺客'),
    ('Builds/Barbarian/MuschoGuide', '野蛮人攻略'),
    ('Builds/Barbarian/ProdigyEndgameColdBarbazon', 'Prodigy 的终局冰冻野蛮人'),
    ('Builds/Barbarian/TTCN', '战嗥野蛮人'),
    ('Builds/Barbarian/slamacekCarnage', 'slamacek 屠杀野蛮人'),
    ('Builds/Druid/HCFireClawsDruid', '专家级火焰爪德鲁伊'),
    ('Builds/Druid/PolarBearShockwaveDruid', '震波北极熊物理德鲁伊'),
    ('Builds/Druid/ScruphSummonDruid', '召唤德鲁伊 2.1'),
    ('Builds/Druid/ShoobyArmageddonBear', 'Shooby 的火焰震波熊'),
    ('Builds/Druid/ShoobyBirdDruid', 'Shooby 的乌鸦德鲁伊'),
    ('Builds/Druid/ShoobyTecSlamDruid', 'Shooby 的构造猛击/重槌熊德'),
    ('Builds/FoHPaladin3x', 'Prodigy 的天堂之拳圣骑士 (3.0.10)'),
    ('Builds/Necromancer/ShoobyMaadiBonemancer', 'Shooby 的 Maadi 骨矛死灵'),
    ('Builds/Necromancer/summonnecro', '召唤死灵 2.1'),
    ('Builds/Paladin/ElePhysHybridPally', 'Xmortem 的元素物理混合圣骑士'),
    ('Builds/Paladin/FoH_Hammerdin_Merc_Equip', '天堂之拳/祝福之锤佣兵装备'),
    ('Builds/Paladin/FohPaladinByJasper89c', '天堂之拳圣骑士'),
    ('Builds/Paladin/HolyFireProdigy3x', '圣火圣骑士 (3.0.5+)'),
    ('Builds/Paladin/palano1', '走路圣骑士（圣火玩法）'),
    ('Builds/Sorceress/FrozenOrbSorceress', '冰封球法师'),
    ('Builds/Sorceress/GangsterSoso', 'Gangster 法师'),
    ('Builds/Sorceress/NovaSorceress', '新星法师'),
    ('Builds/Sorceress/ProdigyHydraFireballSorc', 'Prodigy 的九头蛇火球法师 3.0.x'),
    ('Builds/Sorceress/ShoobyVengSummSorc', 'Shooby 的复仇召唤法师'),
    ('Builds/Sorceress/Sorceress', '3.x 简易终局与超级Boss - Jerrdan 的冰封球法师'),
    ('Builds/Sorceress/TodayGamezForbSorc', '冰封球法师 (2.1.0 更新)'),
    ('Builds/Sorceress/Whirlwind_Enchantress', '旋风强化法师'),
]

print("\n=== Builds ===")
bcount = 0
for path, zh_title in builds:
    content, en_title, ctype = get_en_content(path)
    if not content:
        print(f"  MISSING: {path}")
        continue

    zh_content = content
    zh_content = zh_content.replace('/en/', '/zh/')

    hash_val = hashlib.sha256(zh_content.encode('utf-8')).hexdigest()

    c.execute("SELECT id FROM pages WHERE path=? AND localeCode='zh'", (path,))
    if c.fetchone():
        print(f"  EXISTS: {path}")
        continue

    editor = 'ckeditor'
    c.execute("""INSERT INTO pages (id, path, hash, title, description, isPrivate, isPublished,
         contentType, createdAt, updatedAt, editorKey, localeCode, creatorId, authorId, extra)
         VALUES (?, ?, ?, ?, '', 0, 1, 'html', ?, ?, ?, 'zh', 1, 1, '{}')""",
        (next_page_id, path, hash_val, zh_title, now, now, editor))
    c.execute("UPDATE pages SET content=? WHERE id=?", (zh_content, next_page_id))

    depth = path.count('/')
    parent = None
    if depth > 0:
        pp = path.rsplit('/', 1)[0]
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
        (next_tree_id, path, depth, zh_title, next_page_id, parent, 'zh', json.dumps(ancestors)))

    print(f"  IMPORTED: {path} ({zh_title})")
    next_page_id += 1
    next_tree_id += 1
    bcount += 1

print(f"  {bcount} builds imported")

# === DESKTOP LAUNCHER ===
print("\n=== DesktopLauncher ===")
content, en_title, ctype = get_en_content('DesktopLauncher/PluginCreation')
if content:
    zh_content = content
    # Translate headers
    zh_content = zh_content.replace('# Plugin Authoring Guide', '# 插件编写指南')
    zh_content = zh_content.replace('## Introduction', '## 简介')
    zh_content = zh_content.replace('## Getting Started', '## 开始使用')
    zh_content = zh_content.replace('## API Reference', '## API 参考')
    zh_content = zh_content.replace('## Examples', '## 示例')
    zh_content = zh_content.replace('/en/', '/zh/')

    import_page('DesktopLauncher/PluginCreation', zh_content, '插件编写指南', 'Reimagined 桌面启动器插件编写指南', 'markdown')

conn.commit()
conn.close()
print("\n🎉 All done!")
