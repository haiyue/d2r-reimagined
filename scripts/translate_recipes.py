#!/usr/bin/env python3
"""Create Chinese versions of recipes/Crafting and other recipe pages."""
import re, os

WIKI_ZH = '/Users/wangxinlei/haiyue/d2r-reimagined/wiki-zh'
TMP = '/tmp'

def translate_page(src, dst, replacements):
    with open(src, 'r', encoding='utf-8') as f:
        content = f.read()

    for old, new in replacements.items():
        content = content.replace(old, new)

    with open(dst, 'w', encoding='utf-8') as f:
        f.write(content)

    lines = content.count('\n')
    print(f"  Created: {dst} ({lines} lines)")

# === Crafting page ===
crafting_replacements = {
    '<h1>Item Crafting System</h1>': '<h1>物品合成系统</h1>',
    '<p>Players can craft a variety of items to help define their builds, both as they level and during end-game progression.&nbsp;</p>': '<p>玩家可以合成各种物品来帮助构建自己的玩法，既适用于升级过程，也适用于终局发展。&nbsp;</p>',
    '<p>When an item returns as magic that means it gives you the guaranteed stats with a chance of a prefix and a suffix on a magical item.</p>': '<p>当结果物品为魔法品质时，表示它提供保证属性，并有几率附加一个前缀和一个后缀。</p>',
    '<p>When it returns as rare, that means it gives the guaranteed stats with a chance at between 1-3 prefixes and 1-3 suffixes chosen at random.&nbsp;</p>': '<p>当结果物品为稀有品质时，表示它提供保证属性，并有几率随机附加 1-3 个前缀和 1-3 个后缀。&nbsp;</p>',
}
crafting_replacements.update({
    '<p>When the item is returned as crafted, it will have a chance to have a set number of bonus affixes in addition to the guaranteed stats based on the level of the item returned, which is always the same as the character that created the craft unless specified otherwise. More information on level requirements and affix count for crafted items can be found <a href="https://maxroll.gg/d2/items/crafted-items">here</a>.</p>':
    '<p>当结果物品为手工制品品质时，除了保证属性外，根据返回物品的等级还有几率获得固定数量的额外词缀（返回物品等级始终等同于制作角色等级，除非另有说明）。关于手工制品等级需求和词缀数量的更多信息请参见<a href="https://maxroll.gg/d2/items/crafted-items">此处</a>。</p>',
    '<mark class="pen-green"><strong>Reagent</strong></mark>': '<mark class="pen-green"><strong>材料</strong></mark>',
    '<mark class="pen-green"><strong>Guaranteed Stats</strong></mark>': '<mark class="pen-green"><strong>保证属性</strong></mark>',
    '<h2>Amulets</h2>': '<h2>项链</h2>',
    '<h2>Rings</h2>': '<h2>戒指</h2>',
    '<h2>Gloves</h2>': '<h2>手套</h2>',
    '<h2>Boots</h2>': '<h2>鞋子</h2>',
    '<h2>Belts</h2>': '<h2>腰带</h2>',
    '<h2>Helms</h2>': '<h2>头盔</h2>',
    '<h2>Body Armor</h2>': '<h2>胸甲</h2>',
    '<h2>Shields</h2>': '<h2>盾牌</h2>',
    '<h2>Weapons</h2>': '<h2>武器</h2>',
    '<h2>Charms</h2>': '<h2>护符</h2>',
    '<h2>Jewels</h2>': '<h2>珠宝</h2>',
    '<h2>Wands</h2>': '<h2>法杖</h2>',
    'Magic Amulet': '魔法项链',
    'Magic Ring': '魔法戒指',
    'Magic Jewel': '魔法珠宝',
    'Rare Jewel': '稀有珠宝',
    'Unique Jewel': '暗金珠宝',
    'Magic Charm': '魔法护符',
    'Orb of Infusion': '注入宝珠',
    'Gem (Any)': '宝石（任意）',
    'Standard of Terror': '恐怖标准',
    'Standard of Heroes': '英雄标准',
    '>Reagent<': '>材料<',
    '>Guaranteed Stats<': '>保证属性<',
    '% Enhanced Defense': '% 增强防御',
    '% Enhanced Damage': '% 增强伤害',
    '% Faster Run': '% 高速跑步',
    '% Faster Hit Recovery': '% 快速打击恢复',
    'Life Stolen': '生命偷取',
    'Mana Stolen': '法力偷取',
    'Cold Resist': '冰冷抗性',
    'Lightning Resist': '闪电抗性',
    'Fire Resist': '火焰抗性',
    'Poison Resist': '毒素抗性',
    'All Resistances': '所有抗性',
    'Damage Reduced By': '物理伤害减少',
    'Magic Damage Reduced By': '魔法伤害减少',
    'Half Freeze Duration': '冰冻时间减半',
    'Replenish Life': '生命恢复',
    '% Increased Chance of Blocking': '% 提升格挡几率',
    'Faster Block Rate': '快速格挡速率',
    'Increase Maximum Life': '增加最大生命',
    '% to Max': '% 最大',
    'Attack Rating': '攻击命中率',
    'To Mana After Each Kill': '击杀后法力',
    'Regenerate Mana': '法力恢复',
})

translate_page(os.path.join(TMP, 'recipes_Crafting.html'),
                os.path.join(WIKI_ZH, 'recipes', 'Crafting.html'),
                crafting_replacements)

# === CubeRecipes page ===
trans = {
    '<h1>Cube Recipes</h1>': '<h1>合成配方</h1>',
    '<p>Horadric Cube recipes that players may find useful on their journeys.</p>': '<p>玩家在旅途中可能用得上的赫拉迪克魔盒配方。</p>',
    '<mark class="pen-green"><strong>Reagent</strong></mark>': '<mark class="pen-green"><strong>材料</strong></mark>',
    '<mark class="pen-green"><strong>Outcome</strong></mark>': '<mark class="pen-green"><strong>结果</strong></mark>',
    '<h2>Socket Recipes</h2>': '<h2>打孔配方</h2>',
    '<h2>Unsocket Recipes</h2>': '<h2>去孔配方</h2>',
    '<h2>Conversion Recipes</h2>': '<h2>转换配方</h2>',
    '<h2>Upgrade Recipes</h2>': '<h2>升级配方</h2>',
    '<h2>Misc Recipes</h2>': '<h2>其他配方</h2>',
    '<p>Applies to Weapons, Shields, Chest Armor and Helms only.</p>': '<p>仅适用于武器、盾牌、胸甲和头盔。</p>',
    '<p>Jewelry, Belts, Gloves and Boots cannot have sockets.</p>': '<p>首饰、腰带、手套和鞋子不能有孔。</p>',
    '<p>Pliers can be bought from Blacksmithing vendors in all acts.</p>': '<p>所有幕的铁匠供应商均可购买钳子。</p>',
    'Socketed amount will remain, but you get the socketed items attached jewels or runes returned.': '孔数将保留，但你会取回镶嵌的珠宝或符文。',
    'Item (White)': '物品（白色）',
    'Item (Magic)': '物品（魔法）',
    'Item (Rare)': '物品（稀有）',
    'Item (Set)': '物品（套装）',
    'Item (Unique)': '物品（暗金）',
    'Item (Crafted)': '物品（手工）',
    'Orb of Socketing': '打孔宝珠',
    '# Sockets': '# 孔',
    'Magic Jewels': '魔法珠宝',
    'Rare Jewels': '稀有珠宝',
    'Unique Jewels': '暗金珠宝',
    'Jewel Pliers': '珠宝钳',
    'Rune Pliers': '符文钳',
    '/en/': '/zh/',
}
translate_page(os.path.join(TMP, 'recipes_CubeRecipes.html'),
                os.path.join(WIKI_ZH, 'recipes', 'CubeRecipes.html'),
                trans)

# === ISCStatLimits page ===
trans2 = {
    'Work in Progress list of stats and their limits in relation to our item upgrade/enchantment system.': '物品属性及其在升级/附魔系统中的限制列表（持续更新中）。',
    'This is to communicate information, not to provide a modding guide or tutorial.': '此为信息传达之用，并非模组制作指南或教程。',
    '<mark class="pen-green"><strong>Key:</strong></mark>': '<mark class="pen-green"><strong>说明：</strong></mark>',
    '<mark class="pen-green">Stat </mark>= Item Property or Stat': '<mark class="pen-green">Stat（属性）</mark>= 物品属性或变量',
    '<mark class="pen-green">Range </mark>= Min - Max values of Stat (Roughly)': '<mark class="pen-green">Range（范围）</mark>= 属性的最小-最大值（大致）',
    '<mark class="pen-green">Par Rng</mark> = The range a secondary option can be, usually used to select a skill but can do other things.': '<mark class="pen-green">Par Rng（参数范围）</mark>= 辅助选项的范围，通常用于选择技能但也可做其他用途。',
    '<mark class="pen-green">Fraction </mark>= Per Level growth type. If it says 8ths then it is min-max/fraction per level.': '<mark class="pen-green">Fraction（分数）</mark>= 每级成长类型。如果显示 8ths，则表示每级最小-最大/分数。',
    '<th><mark class="pen-green">Stat</mark></th>': '<th><mark class="pen-green">属性</mark></th>',
    '<th><mark class="pen-green">Range</mark></th>': '<th><mark class="pen-green">范围</mark></th>',
    '<th><mark class="pen-green">Par Rng</mark></th>': '<th><mark class="pen-green">参数范围</mark></th>',
    '<th><mark class="pen-green">Fraction</mark></th>': '<th><mark class="pen-green">分数</mark></th>',
}
translate_page(os.path.join(TMP, 'recipes_ISCStatLimits.html'),
                os.path.join(WIKI_ZH, 'recipes', 'ISCStatLimits.html'),
                trans2)

# === ItemEnchants page ===
trans3 = {
    '<h1>Item Enchants</h1>': '<h1>物品附魔</h1>',
    'Item Enchants are used to upgrade items to add additional stats.': '物品附魔用于升级物品以添加额外属性。',
    '<mark class="pen-green"><strong>Material</strong></mark>': '<mark class="pen-green"><strong>材料</strong></mark>',
    '<mark class="pen-green"><strong>Enchant</strong></mark>': '<mark class="pen-green"><strong>附魔</strong></mark>',
    '<mark class="pen-green"><strong>Reagent</strong></mark>': '<mark class="pen-green"><strong>材料</strong></mark>',
    '<mark class="pen-green"><strong>Outcome</strong></mark>': '<mark class="pen-green"><strong>结果</strong></mark>',
    '<h2>Weapon Enchants</h2>': '<h2>武器附魔</h2>',
    '<h2>Armor Enchants</h2>': '<h2>防具附魔</h2>',
    '<h2>Shield Enchants</h2>': '<h2>盾牌附魔</h2>',
    '<h2>Helm Enchants</h2>': '<h2>头盔附魔</h2>',
    '<h2>Amulet Enchants</h2>': '<h2>项链附魔</h2>',
    '<h2>Ring Enchants</h2>': '<h2>戒指附魔</h2>',
    '<h2>Belt Enchants</h2>': '<h2>腰带附魔</h2>',
    '<h2>Glove Enchants</h2>': '<h2>手套附魔</h2>',
    '<h2>Boot Enchants</h2>': '<h2>鞋子附魔</h2>',
    '<h2>Jewel Enchants</h2>': '<h2>珠宝附魔</h2>',
    '<h2>Charm Enchants</h2>': '<h2>护符附魔</h2>',
    '<h2>Class Changes</h2>': '<h2>职业属性附魔</h2>',
    '/en/': '/zh/',
    'Standard of Terror': '恐怖标准',
    'Standard of Heroes': '英雄标准',
    'Orb of Infusion': '注入宝珠',
    'Orb of Socketing': '打孔宝珠',
    'Orb of Shadows': '暗影宝珠',
    'Orb of Conversion': '转换宝珠',
    'Orb of Assemblage': '组合宝珠',
    'Orb of Corruption': '腐化宝珠',
    'Gem Bag': '宝石袋',
    'Magic Jewel': '魔法珠宝',
    'Rare Jewel': '稀有珠宝',
    'Unique Jewel': '暗金珠宝',
    'Magic Amulet': '魔法项链',
    'Magic Ring': '魔法戒指',
    'Magic Charm': '魔法护符',
    'Gem (Any)': '宝石（任意）',
}
translate_page(os.path.join(TMP, 'recipes_ItemEnchants.html'),
                os.path.join(WIKI_ZH, 'recipes', 'ItemEnchants.html'),
                trans3)

print("\nAll recipe pages created!")
