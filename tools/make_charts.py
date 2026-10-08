# Draw the README infographics from data/summary.json (build_summary.py) as self-contained SVG files in charts/: they carry their own
# dark background, so they read the same on GitHub's light and dark themes. A new GPU or map in summary.json becomes a new panel.
#   charts/gi-cost-hw.svg, charts/gi-cost-sw.svg  GI cost (GI on - GI off, ms) per tier, WindyGI against Lumen, one panel per GPU and map
#   charts/fps-gain.svg                           WindyGI's FPS against Lumen's (%) per tier, every sheet, GPU and map
# Pure Python, no dependencies. Usage: python tools/make_charts.py   (from the repo root)
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ROWS = json.loads((ROOT / 'data' / 'summary.json').read_text(encoding='utf-8'))['rows']
OUT = ROOT / 'charts'
OUT.mkdir(exist_ok=True)
C = {'bg': '#101316', 'panel': '#171c21', 'line': '#2a3139', 'ink': '#e7eaec', 'muted': '#98a2ab', 'w': '#f0a640', 'l': '#7f93a8',
     'good': '#52c7a0', 'bad': '#ee7269'}
FONT = "Segoe UI, Helvetica Neue, Helvetica, Arial, sans-serif"
MONO = "Consolas, SFMono-Regular, Menlo, monospace"
TN = {'low': 'Low', 'med': 'Medium', 'high': 'High', 'epic': 'Epic'}
SHEET = {'hw': 'WindyGI Hardware vs Lumen HWRT', 'sw': 'WindyGI Software vs Lumen SW'}
W = 900


def text(x, y, s, size=13, fill=C['ink'], weight=400, anchor='start', font=FONT):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>'


def rect(x, y, w, h, fill, rx=0):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"/>'


def panels(rows):
    keys = []
    for r in rows:
        k = (r['sheet'], r['gpu'], r['res'], r['map'])
        if k not in keys:
            keys.append(k)
    return [(k, [r for r in rows if (r['sheet'], r['gpu'], r['res'], r['map']) == k]) for k in keys]


def svg(h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{escape(title)}">'
            + rect(0, 0, W, h, C['bg'], 10) + ''.join(body) + '</svg>\n')


def legend(y):
    return [rect(24, y - 10, 12, 12, C['w'], 2), text(42, y, 'WindyGI', 13, C['ink']),
            rect(112, y - 10, 12, 12, C['l'], 2), text(130, y, 'Lumen', 13, C['ink'])]


def gi_cost(sheet):
    ps = panels([r for r in ROWS if r['sheet'] == sheet])
    body = [text(24, 36, f'GI cost per tier: {SHEET[sheet]}', 20, C['ink'], 600),
            text(24, 58, 'Frame time with GI on minus GI off, mean over the views, ms. Shorter is cheaper.', 13, C['muted'])] + legend(84)
    y = 104
    x0, x1 = 120, 690
    for (sh, gpu, res, mp), rows in ps:
        rows = sorted(rows, key=lambda r: list(TN).index(r['tier']))
        ph = 40 + 46 * len(rows) + 8
        body.append(rect(16, y, W - 32, ph, C['panel'], 8))
        body.append(text(32, y + 26, f'{gpu} · {res} · {mp}', 15, C['ink'], 600))
        body.append(text(W - 32, y + 26, f'{rows[0]["views"]} views', 12, C['muted'], 400, 'end'))
        vmax = max(max(r['w_gi'] or 0, r['l_gi'] or 0) for r in rows) * 1.08
        yy = y + 44
        for r in rows:
            body.append(text(32, yy + 19, TN[r['tier']], 14, C['ink'], 600))
            for i, (k, col) in enumerate((('w_gi', C['w']), ('l_gi', C['l']))):
                by = yy + 2 + i * 18
                v = r[k]
                if v is None:
                    body.append(text(x0, by + 12, 'Lumen Low: no GI', 12, C['muted'], 400, font=MONO))
                    continue
                bw = (x1 - x0) * v / vmax
                body.append(rect(x0, by, bw, 14, col, 2))
                body.append(text(x0 + bw + 6, by + 12, f'{v:.2f} ms', 12, C['ink'], 400, font=MONO))
            if r['w_gi'] is not None and r['l_gi']:
                ratio = r['w_gi'] / r['l_gi']
                body.append(text(W - 32, yy + 21, f'{ratio:.2f}x Lumen', 13, C['good'] if ratio < 1 else C['bad'], 600, 'end', MONO))
            yy += 46
        y += ph + 12
    body.append(text(24, y + 14, 'Bars are scaled per panel. Source: data/summary.json, built from the sheets.', 11, C['muted']))
    return svg(y + 30, body, f'GI cost per tier, {SHEET[sheet]}')


def fps_gain():
    ps = panels([r for r in ROWS if r['tier'] != 'low'])
    tiers = ['med', 'high', 'epic']
    body = [text(24, 36, 'WindyGI FPS against Lumen', 20, C['ink'], 600),
            text(24, 58, 'WindyGI FPS / Lumen FPS - 1, mean over the views, same GI tier. Right of the line: WindyGI is faster.', 13, C['muted'])]
    lab, cw = 250, (W - 250 - 24) / len(tiers)
    y = 92
    for i, t in enumerate(tiers):
        body.append(text(lab + cw * i + 28, y, TN[t], 14, C['ink'], 600))
    y += 12
    gmax = max(abs(r['w_fps'] / r['l_fps'] - 1) for _, rows in ps for r in rows) * 1.15
    for (sh, gpu, res, mp), rows in ps:
        body.append(rect(16, y, W - 32, 40, C['panel'], 6))
        body.append(text(32, y + 17, f'{"Hardware" if sh == "hw" else "Software"} · {gpu}', 13, C['ink'], 600))
        body.append(text(32, y + 33, f'{res} · {mp}', 12, C['muted']))
        for i, t in enumerate(tiers):
            r = next((r for r in rows if r['tier'] == t), None)
            # zero line near the cell's left edge (WindyGI is mostly faster): the right side holds the bar, 28 px are left for a loss
            cx = lab + cw * i + 28
            half = cw - 28 - 64
            body.append(rect(cx - 0.5, y + 6, 1, 28, C['muted']))
            if r is None:
                continue
            g = r['w_fps'] / r['l_fps'] - 1
            bw = half * abs(g) / gmax if g >= 0 else min(24, half * abs(g) / gmax)
            col = C['good'] if g >= 0 else C['bad']
            body.append(rect(cx if g >= 0 else cx - bw, y + 13, bw, 14, col, 2))
            tx = cx + bw + 5 if g >= 0 else cx - bw - 5
            body.append(text(tx, y + 25, f'{g * 100:+.0f} %', 12, C['ink'], 400, 'start' if g >= 0 else 'end', MONO))
        y += 46
    body.append(text(24, y + 14, 'Source: data/summary.json, built from the sheets.', 11, C['muted']))
    return svg(y + 30, body, 'WindyGI FPS against Lumen per tier')


files = {'gi-cost-hw.svg': gi_cost('hw'), 'gi-cost-sw.svg': gi_cost('sw'), 'fps-gain.svg': fps_gain()}
for name, s in files.items():
    (OUT / name).write_text(s, encoding='utf-8')
    print(f'charts/{name}: {len(s)} bytes')
