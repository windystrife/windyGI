# Collect the headline numbers of every sheet into data/summary.json (one row per sheet, GPU, map and GI tier), the input of
# make_charts.py and the README tables. Reads the data each sheet embeds in its index.html (`const D = {...};`), so a new GPU or map
# added to a sheet shows up here after a rebuild of that sheet. Pure Python, no dependencies.
# Usage: python tools/build_summary.py   (from the repo root)
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIERS = ['low', 'med', 'high', 'epic']


def sheet_data(path):
    s = path.read_text(encoding='utf-8')
    m = re.search(r'const D = (\{.*?\});\n', s, re.S)
    return json.loads(m.group(1))


def summarise(rows):
    ok = [r for r in rows if r.get('w') and r.get('l') and r['w'].get('ft') and r['l'].get('ft')]
    if not ok:
        return None
    mean = lambda xs: sum(xs) / len(xs) if xs else None
    wft, lft = mean([r['w']['ft'] for r in ok]), mean([r['l']['ft'] for r in ok])
    wgi = mean([r['w_gi'] for r in ok if r.get('w_gi') is not None])
    lgi = mean([r['l_gi'] for r in ok if r.get('l_gi') is not None])
    return {'views': len(ok), 'faster': sum(1 for r in ok if r['w']['ft'] < r['l']['ft']),
            'w_ft': round(wft, 3), 'l_ft': round(lft, 3), 'w_fps': round(1000 / wft, 1), 'l_fps': round(1000 / lft, 1),
            'w_gi': None if wgi is None else round(wgi, 3), 'l_gi': None if lgi is None else round(lgi, 3)}


MAPS = {'RT': 'Map_RT_Daylight', 'TG': 'TestGIMap'}
rows = []
# hardware sheets: one GPU and one map each (perf.meta.gpu, perf.tiers): hw/ (RX 9070 XT), then hw-<gpu_id>/ per further GPU
for f in sorted(ROOT.glob('hw*/index.html'), key=lambda p: (p.parent.name != 'hw', p.parent.name)):
    hw = sheet_data(f)['perf']
    g = hw['meta']['gpu']
    for t in TIERS:
        s = summarise(hw['tiers'].get(t, []))
        if s:
            rows.append({'sheet': 'hw', 'gpu': g['gpu_name'], 'res': g['gpu_res'], 'map': 'Map_RT_Daylight', 'tier': t, **s,
                         'machine': g.get('machine', ''), 'page': f.parent.name + '/'})
# software sheet: several GPUs and maps (perf.gpus[].maps[map][tier])
sw = sheet_data(ROOT / 'sw' / 'index.html')['perf']
for g in sw['gpus']:
    for mk, tiers in g['maps'].items():
        for t in TIERS:
            s = summarise(tiers.get(t, []))
            if s:
                rows.append({'sheet': 'sw', 'gpu': g['name'], 'res': g['res'], 'map': MAPS.get(mk, mk), 'tier': t, **s,
                             'machine': g.get('machine', ''), 'page': 'sw/'})
out = ROOT / 'data' / 'summary.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({'rows': rows}, indent=1) + '\n', encoding='utf-8')
print(f'{out.relative_to(ROOT)}: {len(rows)} rows')
