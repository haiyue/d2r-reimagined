/**
 * D2R Reimagined — Compact Markdown Generator (v3, ultra-compact)
 *
 * Ultra-compact format to fit all entries in ≤200KB.
 * Minimizes whitespace, abbreviations, no bold markers.
 */

const fs = require('fs');
const path = require('path');

const DIR = p => path.resolve(__dirname, '../../website/static/data', p);
const DATA = f => JSON.parse(fs.readFileSync(DIR('keyed/' + f), 'utf8'));

const zhCN = JSON.parse(fs.readFileSync(DIR('strings/zhCN.json'), 'utf8'));
const enUS = JSON.parse(fs.readFileSync(DIR('strings/enUS.json'), 'utf8'));
const propertyGroups = JSON.parse(fs.readFileSync(
  path.resolve(__dirname, '../../website/src/resources/property_groups.json'), 'utf8'
));

function utf8(s) { return Buffer.byteLength(s, 'utf8'); }

const SEQ = /%(?:\+d|d|D|s|S|i|c\d|\d|%)/g;
function lookup(k) { return k ? (zhCN[k] || enUS[k] || k) : ''; }
function fa(v, t) {
  if (v == null) return '';
  const n = Number(v), f = Number.isFinite(n);
  if (t === '%+d') return f ? (n >= 0 ? '+' : '') + Math.trunc(n) : String(v);
  if (t === '%d' || t === '%D' || t === '%i') return f ? String(Math.trunc(n)) : String(v);
  if (t === '%s' || t === '%S') return String(v);
  return String(v);
}
function ft(tpl, args) {
  if (!tpl) return '';
  const toks = tpl.match(SEQ)??[], seq = toks.filter(m => m !== '%%' && !/^%\d$/.test(m) && !/^%c\d$/.test(m));
  const isN = m => m === '%+d' || /^%[dDi]$/.test(m);
  let pb = Math.max(0, Math.min(args.length - seq.length, seq.filter(isN).length));
  const iT = toks.filter(m => /^%\d$/.test(m)), iS = iT.reduce((m, x) => Math.max(m, +x[1]), 0);
  const rI = iT.length && args.length > iS ? (() => { let p = 0, b = args.length - iS, r = []; for (let i = 0; i < iS; i++) { const mn = args[p], mx = args[p+1]; if (b > 0 && typeof mn === 'number' && typeof mx === 'number' && Number.isFinite(mn) && Number.isFinite(mx)) { const ms = fa(mn, '%d'); r.push(mn === mx ? ms : ms + '-' + fa(mx, '%d')); p += 2; b--; } else r.push(fa(args[p++], '%0')); } return r; })() : null;
  let si = 0;
  return tpl.replace(SEQ, m => {
    if (m === '%%') return '%';
    if (/^%\d$/.test(m)) { const i = +m[1]; return rI ? rI[i]??'' : fa(args[i], m); }
    if (/^%c\d$/.test(m)) return '';
    if (isN(m) && pb > 0) { pb--; const mn = args[si++], mx = args[si++], ms = fa(mn, m); return (typeof mn === 'number' && typeof mx === 'number' && Number.isFinite(mn) && Number.isFinite(mx) && mn !== mx) ? ms + '-' + fa(mx, m === '%+d' ? '%d' : m) : ms; }
    return fa(args[si++], m);
  });
}
function fl(line) {
  if (!line) return '';
  const args = (line.args || []).map(a => typeof a === 'string' ? (zhCN[a] || enUS[a] || a) : a);
  let r = ft(lookup(line.key), args);
  if (line.perLevel) r += '(按等级)';
  if (line.qualifier) { const q = {weapon:'(武器)',shield:'(盾牌)',armor:'(护甲)'}[line.qualifier]; if (q) r += q; }
  if (line.classOnly) r += ' ' + (zhCN[line.classOnly] || enUS[line.classOnly] || line.classOnly);
  if (line.itemsRequired) r = `{${line.itemsRequired}}${r}`;
  else if (line.fullSet) r = `{全}${r}`;
  return r;
}
function ls(arr) { return (arr||[]).map(fl).filter(Boolean); }
function typeLabel(idx) { const l = lookup(idx); return l !== idx ? l : idx; }

const DL = ['1H','2H','投掷','伤害','元素'];
function dmgStr(dts) {
  if (!dts||!dts.length) return '';
  return dts.map(d => `${DL[d.Type]||'?'}:${(d.Lines||[]).map(fl).filter(Boolean).join(' ')}${d.AverageDamage?`<${d.AverageDamage}>`:''}`).join(';');
}

const MAXB = 194000;
let BW = 0;
function pl(out, s) { const a = utf8(s)+1; if (BW + a > MAXB) return false; BW += a; out.push(s); return true; }

// ── 1. 底材 ──────────────────────────────────────────────────────────
function genBases() {
  const armors = DATA('armors.json');
  const weapons = DATA('weapons.json');
  const all = [...armors.map((it,i)=>({...it,__kind:'armor',__index:i,Code:it.Code||it.NameKey})),
    ...weapons.map((it,i)=>({...it,__kind:'weapon',__index:i+10000,Code:it.Code||it.NameKey}))];
  const groups = {};
  for (const it of all) { const k = it.Type?.Name||'Other'; if (!groups[k]) groups[k]=[]; groups[k].push(it); }
  const out = []; BW = 0;
  pl(out, '# 物品底材'); pl(out, '');
  pl(out, `armors.json+weapons.json | ${all.length}条（盔甲${armors.length} 武器${weapons.length}）`);
  pl(out, '格式: 名 [N/X/E] | 类型 | req | 孔 | code | class | 属性'); pl(out, ''); pl(out, '---'); pl(out, '');
  for (const [tn, items] of Object.entries(groups)) {
    if (!pl(out, '') || !pl(out, `## ${lookup(tn)} (${tn}) ${items.length}`)) break;
    items.sort((a,b)=>(a.RequiredLevel||1)-(b.RequiredLevel||1));
    for (const it of items) {
      const nm = lookup(it.NameKey);
      const t = nm.includes('[N]')?'[N]':nm.includes('[X]')?'[X]':nm.includes('[E]')?'[E]':'';
      const cn = nm.replace(/\[[NXE]\]/g,'').trim();
      const s = [];
      if (it.DamageTypes?.length) { const d = dmgStr(it.DamageTypes); if (d) s.push(d); }
      if (it.Lines) for (const l of it.Lines) {
        if (['strDefense','strDefenseRange','strDefenseRangeRange','strChanceToBlock','strSmiteDamage','strKickDamage',
             'strDurability','strIndestructible','strRequiredStrength','strRequiredDexterity','strRequiredClass',
             'strethereal','strSocketedCount'].includes(l.key)) { const f = fl(l); if (f) s.push(f); }
      }
      if (!pl(out, `- ${cn}${t?' '+t:''} | ${typeLabel(it.Type?.Index)} | req${it.RequiredLevel||1} | 孔${it.GemSockets||'0'}${it.Code?' c:'+it.Code:''}${it.RequiredClass?' cls:'+lookup(it.RequiredClass):''}${s.length?' | '+s.join(';'):''}`)) break;
    }
    if (BW >= MAXB) break;
  }
  return out.join('\n');
}

// ── 2. 词缀 ──────────────────────────────────────────────────────────
const PG_ZH = {
  'prop_group_absorbs': '吸收', 'prop_group_attack_rating': '命中',
  'prop_group_attributes': '属性', 'prop_group_auto_repair': '自修',
  'prop_group_block_chance': '格挡', 'prop_group_charges': '充能',
  'prop_group_ctc_level_up': '升级触发', 'prop_group_ctc_when_striking': '击中触发',
  'prop_group_ctc_when_struck': '被击触发', 'prop_group_damage': '伤害',
  'prop_group_defense': '防御', 'prop_group_demon_damage': '对恶魔',
  'prop_group_elemental_effect_defense': '元素防御',
  'prop_group_elemental_skill_effect': '元素技能',
  'prop_group_elemental_weapon_damage': '武器元素', 'prop_group_equip_aura': '灵气',
  'prop_group_experience': '经验', 'prop_group_gold_find': '金币',
  'prop_group_indestructible': '不毁', 'prop_group_kick_damage': '踢击',
  'prop_group_life': '生命', 'prop_group_life_leech': '生命偷取',
  'prop_group_light_radius': '光照', 'prop_group_magic_find': 'MF',
  'prop_group_mana': '法力', 'prop_group_mana_leech': '法力偷取',
  'prop_group_reanimate': '复活', 'prop_group_requirements': '需求',
  'prop_group_resistances': '抗性', 'prop_group_skill_levels': '技能等级',
  'prop_group_skill_special_effects': '技能特效', 'prop_group_sockets': '镶孔',
  'prop_group_speeds': '速度', 'prop_group_thorns': '荆棘',
  'prop_group_undead_damage': '对不死', 'prop_group_vendor_prices': '价格',
  'prop_group_weapon_effects': '武器效果',
};

function genAffixes() {
  const prefixes = DATA('magicprefix.json').map(x=>({...x,__pt:'前'}));
  const suffixes = DATA('magicsuffix.json').map(x=>({...x,__pt:'后'}));
  const all = [...prefixes, ...suffixes];
  const gd = new Map();
  for (const g of propertyGroups) { const ds = new Set(); for (const i of g.items) if (i.description) ds.add(i.description); gd.set(g.group, ds); }
  const ag = {};
  for (const a of all) { const k = gd.get(a.Group); const key = k && k.size ? [...k].sort().join('+') : '其他'; if (!ag[key]) ag[key] = []; ag[key].push(a); }
  const sg = Object.entries(ag).sort((a,b)=>b[1].length - a[1].length);
  const oi = sg.findIndex(([k])=>k==='其他'); if (oi>-1){const o=sg.splice(oi,1)[0];sg.push(o);}
  const out = []; BW = 0;
  pl(out, '# 词缀'); pl(out, ''); pl(out, `magicprefix.json+magicsuffix.json | 前${prefixes.length}+后${suffixes.length}=${all.length}条`); pl(out, ''); pl(out, '---'); pl(out, '');
  for (const [dk, afs] of sg) {
    const dl = dk.split('+').map(d=>PG_ZH[d]||d.replace('prop_group_','')).filter(Boolean).join('/');
    if (!pl(out, '') || !pl(out, `## ${dl} ${afs.length}`)) break;
    afs.sort((a,b)=>(a.RequiredLevel||1)-(b.RequiredLevel||1)||(a.NameKey||'').localeCompare(b.NameKey||''));
    for (const a of afs) {
      const nm = lookup(a.NameKey)||a.NameKey;
      const rl = a.RequiredLevel||1;
      const al = a.MaxLevel?`${a.Level}-${a.MaxLevel}`:String(a.Level||rl);
      const types = (a.Types||[]).map(typeLabel).join(',');
      const etypes = (a.ETypes||[]).map(typeLabel).join(',');
      const props = ls(a.Lines);
      let ln = `- ${nm} | ${a.__pt} | ${rl} | (${al})`;
      if (types) ln += ` | ${types}`;
      if (etypes) ln += ` -${etypes}`;
      if (props.length) ln += ` | ${props.join(';')}`;
      if (!pl(out, ln)) break;
    }
    if (BW >= MAXB) break;
  }
  return out.join('\n');
}

// ── 3. 暗金 ──────────────────────────────────────────────────────────
function genUniques() {
  const data = DATA('uniques.json');
  data.sort((a,b)=>(a.RequiredLevel||1)-(b.RequiredLevel||1)||(a.Index||'').localeCompare(b.Index||''));
  const out = []; BW = 0;
  pl(out, '# 暗金物品'); pl(out, '');
  pl(out, `uniques.json | ${data.length}条 | 格式: 名称 | 底材(code) | lv | V/M | 属性`); pl(out, ''); pl(out, '---'); pl(out, '');
  let cl = 0, skipHeader = 0;
  for (const it of data) {
    if (BW >= MAXB) { pl(out, ''); pl(out, `> 已达200KB限制，剩余${data.length - data.indexOf(it)}条未收录。完整数据请访问网站。`); break; }
    const lv = it.RequiredLevel||1;
    if (lv !== cl) { cl = lv; }
    const nm = lookup(it.Index)||it.Index;
    const base = lookup(it.Equipment?.NameKey)||it.Equipment?.NameKey||'?';
    const src = it.Vanilla==='Y'?'V':'M';
    const rar = it.Rarity?` r${it.Rarity}`:'';
    const cd = it.Code?`(${it.Code})`:'';
    const props = ls(it.Lines);
    if (!pl(out, `- ${nm}|${base}${cd}|${lv}|${src}${rar}${props.length?'|'+props.join(';'):''}`)) break;
  }
  return out.join('\n');
}

// ── 4. 套装 ──────────────────────────────────────────────────────────
function genSets() {
  const data = DATA('sets.json');
  const out = []; BW = 0;
  pl(out, '# 套装'); pl(out, ''); pl(out, `sets.json | ${data.length}套`); pl(out, ''); pl(out, '---'); pl(out, '');
  for (const s of data) {
    if (BW >= MAXB) { pl(out, '> 200KB截断'); break; }
    const sn = lookup(s.Index)||s.Index;
    const src = s.Vanilla==='Y'?'V':'M';
    const cnt = s.SetItems?.length||0;
    pl(out, ''); pl(out, `## ${sn} | ${cnt}件 | ${src}`);
    const p = ls(s.PartialBonuses), f = ls(s.FullBonuses);
    if (p.length) pl(out, `- 部分: ${p.join(';')}`);
    if (f.length) pl(out, `- 完整: ${f.join(';')}`);
    for (const si of s.SetItems||[]) {
      if (BW >= MAXB) break;
      const in_ = lookup(si.Index)||si.Index;
      const bn = lookup(si.Equipment?.NameKey)||si.Equipment?.NameKey||'?';
      const il = si.RequiredLevel||1;
      const is_ = si.Vanilla==='Y'?'V':'M';
      const pr = ls(si.Lines);
      const bo = []; if (si.SetBonuses) for (const bg of si.SetBonuses) bo.push(...ls(bg));
      let e = `  - ${in_} (${bn}) | ${il} | ${is_}`;
      if (pr.length) e += ` | ${pr.join(';')}`;
      if (bo.length) e += ` | +${bo.join(';')}`;
      if (!pl(out, e)) break;
    }
  }
  return out.join('\n');
}

// ── 5. 符文之语 ──────────────────────────────────────────────────────
function genRunewords() {
  const data = DATA('runewords.json');
  data.sort((a,b)=>(a.RequiredLevel||1)-(b.RequiredLevel||1));
  const out = []; BW = 0;
  pl(out, '# 符文之语'); pl(out, ''); pl(out, `runewords.json | ${data.length}条`); pl(out, ''); pl(out, '---'); pl(out, '');
  let cl = 0;
  for (const rw of data) {
    if (BW >= MAXB) break;
    const lv = rw.RequiredLevel||1;
    if (lv !== cl) { if (lv > cl+2) { pl(out, ''); pl(out, `## ${lv}`); } cl = lv; }
    const nm = lookup(rw.Index)||rw.Index;
    const src = rw.Vanilla==='Y'?'V':'M';
    const runes = (rw.Runes||[]).map(r=>lookup(r.NameKey)||r.NameKey).join('+');
    const types = (rw.Types||[]).map(ti=>typeLabel(ti.Index)).join('/');
    const props = ls(rw.Lines);
    if (!pl(out, `- ${nm} | ${runes} | ${types} | ${lv} | ${src}${props.length?' | '+props.join(';'):''}`)) break;
  }
  return out.join('\n');
}

// ── 6. 方块配方 ──────────────────────────────────────────────────────
function genCubeRecipes() {
  const data = DATA('cube-recipes.json');
  const groups = {};
  for (const r of data) { const nk = (r.Notes||[]).map(n=>n.key).join(';')||'其他'; if (!groups[nk]) groups[nk]=[]; groups[nk].push(r); }
  const sorted = Object.entries(groups).sort((a,b)=>a[1][0].Index - b[1][0].Index);
  const nzh = {
    'strCubeNoteOrbOfCorruption':'腐化', 'strCubeNoteOrbOfConversion':'转化',
    'strCubeNoteOrbOfAssemblage':'聚汇', 'strCubeNoteOrbOfSocketing':'打孔球',
    'strCubeNoteSocketPunch':'打孔', 'strCubeNotePliers':'钳',
    'strCubeNoteOrbOfInfusion':'灌输', 'strCubeNoteOrbOfShadows':'暗影',
    'strCubeNoteForceEthereal':'强制无形', 'strCubeNoteItemCrafting':'制作',
    'strCubeNoteSunderItemCrafting':'破碎制作', 'strCubeNoteKeyConversion':'钥匙转化',
    'strCubeNotePandemoniumFinalePortal':'终局门', 'strCubeNotePandemoniumPortal':'传送门',
    'strCubeNoteTristramUberSouls':'超级灵魂', 'strCubeNoteUberCharmUpgrade':'超护符升级',
    'strCubeNoteRerollUberAncient':'重铸超远古', 'strCubeNoteRecycle':'回收',
    'strCubeNoteRerollItem':'重铸', 'strCubeNoteJewelUpgrade':'珠宝升级',
    'strCubeNoteSplashCharmUpgrade':'溅射符升级', 'strCubeNoteItemEnchantment':'附魔',
    'strCubeNoteSocketItem':'打孔', 'strCubeNoteBaseTierUpgrade':'底材升级',
    'strCubeNoteRepairEthereal':'修无形', 'strCubeNoteReplenishQuiver':'补箭袋',
    'strCubeNoteRepairNonEthereal':'修非无形', 'strCubeNoteCowPortalRecipe':'奶牛关',
    'strCubeNoteRandomMiniUberPortal':'随机超门', 'strCubeNoteTristramUberPortal':'超门',
    'strCubeNoteForceWhite':'强制白',
  };
  const out = []; BW = 0;
  pl(out, '# 方块配方'); pl(out, ''); pl(out, `cube-recipes.json | ${data.length}条`); pl(out, ''); pl(out, '---'); pl(out, '');
  for (const [nk, grp] of sorted) {
    if (BW >= MAXB) { pl(out, '> 200KB截断'); break; }
    const nl = nk.split(';').filter(Boolean).map(k=>nzh[k]||lookup(k)||k.replace('strCubeNote','').replace(/([A-Z])/g,' $1').trim()).filter(Boolean).join('+')||'其他';
    pl(out, ''); pl(out, `## ${nl} ${grp.length}`);
    pl(out, '|#|输入→输出|几率|'); pl(out, '|---|---|---|');
    for (const r of grp) {
      if (BW >= MAXB) break;
      const inputs = (r.Inputs||[]).map(inp=>{const n=fl(inp.Name)||inp.RawToken||inp.Name?.key||'?';return(inp.Quantity||1)>1?`${inp.Quantity}x${n}`:n;}).join('+');
      const outputs = r.Outputs?Object.values(r.Outputs).map(o=>{const n=fl(o.Name)||'?',q=o.Quantity||1,qs=(o.Qualifiers||[]).map(qq=>typeof qq==='string'?qq:fl(qq)).filter(Boolean),ps=(o.Lines||[]).map(l=>fl(l)).filter(Boolean);let s=q>1?`${q}x${n}`:n;if(qs.length)s+=`(${qs.join(',')})`;if(ps.length)s+=`[${ps.join(';')}]`;return s;}).join('+'):'?';
      const ch = r.Value?`${r.Value}%`:'-';
      const cl = r.RequiredClass?` ${lookup('class_'+r.RequiredClass.toLowerCase())}`:'';
      if (!pl(out, `|${r.Index}|${inputs}→${outputs}${cl}|${ch}|`)) break;
    }
  }
  return out.join('\n');
}

// ── Main ──────────────────────────────────────────────────────────────
const start = Date.now();
console.log('Generating...');
for (const [name, fn, label] of [
  ['item-bases.md', genBases, '底材'],
  ['affixes.md', genAffixes, '词缀'],
  ['uniques.md', genUniques, '暗金物品'],
  ['sets.md', genSets, '套装'],
  ['runewords.md', genRunewords, '符文之语'],
  ['cube-recipes.md', genCubeRecipes, '方块配方'],
]) {
  console.log(`  ${label}...`);
  const c = fn();
  const kb = (utf8(c)/1024).toFixed(0);
  console.log(`    ${kb} KB, ${c.split('\n').length} lines`);
  fs.writeFileSync(path.join(__dirname, name), c, 'utf8');
}
console.log(`Done ${((Date.now()-start)/1000).toFixed(1)}s`);
