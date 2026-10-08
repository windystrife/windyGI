# WindyGI

Real-time global illumination for **Unreal Engine 4.27**, compared with **Lumen** from UE 5.8 and the **UE 5.8 path tracer** on the same views with matched settings.

**Live sheets: <https://windystrife.github.io/windyGI/>**

| | Sheet | Against | Maps | GPUs |
|---|---|---|---|---|
| ⚡ | **[WindyGI Hardware](https://windystrife.github.io/windyGI/hw/)** | Lumen with hardware ray tracing | Map_RT_Daylight (24 views) | RX 9070 XT, 4K native |
| 🖥️ | **[WindyGI Software](https://windystrife.github.io/windyGI/sw/)** | Lumen with software ray tracing | Map_RT_Daylight (24 views), TestGIMap (10 views) | RX 9070 XT, 4K · Radeon 680M, 720p |

Each sheet has a drag-to-compare viewer (any two sources, any tier, as played or at a fixed exposure next to the path tracer), the frame time of every view and the GI cost (GI on minus GI off).

<table>
<tr>
<td align="center"><img src="hw/img/PT-v14.webp" width="280" alt="UE 5.8 path tracer, tent view v14"><br><sub>UE 5.8 path tracer, 2048 spp</sub></td>
<td align="center"><img src="hw/img/WH-pt-v14.webp" width="280" alt="WindyGI Hardware High, tent view v14"><br><sub>WindyGI Hardware, High</sub></td>
<td align="center"><img src="hw/img/LH-pt-v14.webp" width="280" alt="Lumen HWRT High, tent view v14"><br><sub>Lumen HWRT, High</sub></td>
</tr>
</table>
<sub>Map_RT_Daylight, view v14, the same fixed exposure for all three.</sub>

## At a glance

![WindyGI FPS against Lumen per GI tier, every GPU and map](charts/fps-gain.svg)

![GI cost per tier, WindyGI Hardware against Lumen HWRT](charts/gi-cost-hw.svg)

![GI cost per tier, WindyGI Software against Lumen SW](charts/gi-cost-sw.svg)

## WindyGI Hardware against Lumen HWRT

RX 9070 XT, 3840x2160 native, Map_RT_Daylight, mean of 24 views, two processes per engine and tier.

| GI tier | WindyGI FPS | Lumen FPS | GI cost, WindyGI | GI cost, Lumen | WindyGI faster at |
|---|--:|--:|--:|--:|--:|
| Low | 87.4 | 100.9 | 1.42 ms | no GI | 0 / 24 views |
| Medium | 86.9 | 87.6 | 1.49 ms | 1.53 ms | 11 / 24 |
| High | **82.6** | 74.3 | **2.08 ms** | 3.56 ms | **24 / 24** |
| Epic | **74.0** | 56.3 | **3.49 ms** | 7.87 ms | **24 / 24** |

Lumen Low has no GI at all, so the Low row is the price of having GI. Build: UE 4.27 branch `4.27-Soliz` at `aa99779c` (package RT_86).

## WindyGI Software against Lumen SW

| GPU | Map | GI tier | WindyGI FPS | Lumen FPS | GI cost, WindyGI | GI cost, Lumen | WindyGI faster at |
|---|---|---|--:|--:|--:|--:|--:|
| RX 9070 XT, 4K | Map_RT_Daylight | Medium | 94.9 | 91.8 | 1.08 ms | 1.11 ms | 23 / 24 |
| | | High | **92.1** | 80.2 | **1.41 ms** | 2.69 ms | **24 / 24** |
| | | Epic | **83.5** | 63.5 | **2.52 ms** | 5.96 ms | **24 / 24** |
| RX 9070 XT, 4K | TestGIMap | Medium | 130.3 | 109.4 | 1.47 ms | 1.32 ms | 10 / 10 |
| | | High | **125.4** | 92.7 | **1.77 ms** | 2.97 ms | **10 / 10** |
| | | Epic | **109.1** | 72.1 | **2.96 ms** | 6.05 ms | **10 / 10** |
| Radeon 680M, 720p | TestGIMap | Medium | 74.9 | 65.8 | 3.09 ms | 2.78 ms | 10 / 10 |
| | | High | **67.1** | 54.3 | **4.63 ms** | 6.00 ms | **10 / 10** |
| | | Epic | **58.7** | 38.5 | **6.79 ms** | 13.58 ms | **10 / 10** |

The Low rows (no GI in Lumen Low) are on the sheet.

## How it was measured

- **Same scene, same views.** Both engines visit the same camera poses in the same order; UE 5.8 takes the FOV converted from UE 4.27's, so the framing matches pixel for pixel.
- **Matched settings.** TAA at 100 % screen percentage, no upscaler or frame generation, fog and motion blur off, UE 5.8 shadows set to UE 4.27's values, no SSAO, Lumen reflections off and screen-space reflections at the same quality in both.
- **Frame time.** Mean of a 400-frame CSV capture per view after settling, in packaged Development builds. FPS is 1000 divided by the mean frame time.
- **GI cost.** The frame time with GI on minus the same package's frame time with GI off, process by process in the same session.
- **The light level is judged against the path tracer**, not against Lumen: the path tracer is shown for the tent views, where its scene is complete.

## Adding a GPU

1. Run the benchmark kit on the new GPU and rebuild the sheet that covers it (`hw/` or `sw/`): its `index.html` embeds the numbers.
2. `python tools/build_summary.py` collects every sheet, GPU and map into `data/summary.json`.
3. `python tools/make_charts.py` redraws `charts/*.svg`; each new GPU or map becomes a new panel.
4. Add its rows to the tables above and commit.

Both scripts are plain Python 3 with no dependencies.

## Layout

```
index.html   landing page
hw/          WindyGI Hardware sheet: index.html (data embedded) + img/*.webp
sw/          WindyGI Software sheet: index.html (data embedded) + img/*.webp
data/        summary.json: the headline numbers of every sheet, GPU, map and tier
charts/      the README infographics (SVG, drawn from data/summary.json)
tools/       build_summary.py, make_charts.py
```

The pages are static and have no build step: open any `index.html` locally or serve the folder.
