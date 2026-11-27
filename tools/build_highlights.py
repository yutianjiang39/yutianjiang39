"""Build the visual performance highlight for Multisource HL Copy.

Writes a light and a dark SVG into assets/. Figures come from the project's
published performance summary; each panel keeps its own scope in the footer.

    python tools/build_highlights.py
"""

from xml.sax.saxutils import escape

from build_diagrams import ASSETS, FONT, THEMES

W, H = 1200, 480
PANEL_Y, PANEL_H, PANEL_W = 92, 296, 357
PANEL_X = (40, 421, 802)

# Extra colours on top of the shared diagram themes.
EXTRA = {
    "light": {"glow": "#3FB8AF", "hi": "#1B7F79", "lo": "#5FCFC4", "panel_top": "#FFFFFF", "panel_bot": "#F3F7F7", "shadow": "#1F2328", "shadow_op": 0.06},
    "dark": {"glow": "#3FB8AF", "hi": "#7CE0D6", "lo": "#2A9D94", "panel_top": "#1A2129", "panel_bot": "#12171E", "shadow": "#000000", "shadow_op": 0.35},
}


def build(theme):
    t = {**THEMES[theme], **EXTRA[theme]}
    defs, out = [], []

    def text(x, y, s, size=13, weight=400, fill="text", anchor="middle", extra=""):
        colour = fill if fill.startswith("url(") else t[fill]
        out.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{colour}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'
        )

    defs.append(
        f'<linearGradient id="num" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["text"]}"/><stop offset="1" stop-color="{t["hi"]}"/></linearGradient>'
        f'<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["hi"]}"/><stop offset="1" stop-color="{t["lo"]}"/></linearGradient>'
        f'<linearGradient id="area" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["glow"]}" stop-opacity="0.35"/><stop offset="1" stop-color="{t["glow"]}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="wire" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["glow"]}" stop-opacity="0.25"/><stop offset="1" stop-color="{t["glow"]}" stop-opacity="0.9"/></linearGradient>'
        f'<linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["panel_top"]}"/><stop offset="1" stop-color="{t["panel_bot"]}"/></linearGradient>'
        f'<radialGradient id="halo"><stop offset="0" stop-color="{t["glow"]}" stop-opacity="0.45"/>'
        f'<stop offset="1" stop-color="{t["glow"]}" stop-opacity="0"/></radialGradient>'
        f'<filter id="soft" x="-10%" y="-10%" width="120%" height="130%">'
        f'<feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="{t["shadow"]}" flood-opacity="{t["shadow_op"]}"/></filter>'
        f'<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>'
    )

    # frame + header
    out.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t["bg"]}" stroke="{t["frame"]}"/>')
    out.append(f'<rect x="40" y="38" width="4" height="18" rx="2" fill="{t["accent"]}"/>')
    text(54, 53, "MULTISOURCE HL COPY", 13, 700, "accent", "start", ' letter-spacing="1.4"')
    text(W - 40, 53, "Performance · 性能", 13, 500, "muted", "end")

    def panel(px, eyebrow):
        out.append(
            f'<rect x="{px}" y="{PANEL_Y}" width="{PANEL_W}" height="{PANEL_H}" rx="14" '
            f'fill="url(#panel)" stroke="{t["node_stroke"]}" filter="url(#soft)"/>'
        )
        out.append(f'<rect x="{px + 24}" y="{PANEL_Y}" width="56" height="3" rx="1.5" fill="{t["accent"]}"/>')
        text(px + 24, PANEL_Y + 36, eyebrow, 13, 600, "muted", "start")

    def big(px, value, unit, unit_x):
        text(px + 22, PANEL_Y + 112, value, 68, 800, "url(#num)", "start", ' letter-spacing="-2"')
        text(px + unit_x, PANEL_Y + 112, unit, 18, 600, "accent", "start")

    # -- panel 1: latency scale -------------------------------------------------
    px = PANEL_X[0]
    panel(px, "Local submit latency · 本地提交延迟")
    big(px, "23", "ms  p99", 106)
    x0, x1, ty = px + 32, px + PANEL_W - 32, PANEL_Y + 200
    scale = lambda ms: x0 + (x1 - x0) * ms / 30
    out.append(f'<rect x="{x0}" y="{ty - 6}" width="{x1 - x0}" height="12" rx="6" fill="{t["inner"]}" stroke="{t["node_stroke"]}"/>')
    out.append(f'<rect x="{x0}" y="{ty - 6}" width="{scale(23) - x0:.1f}" height="12" rx="6" fill="url(#bar)" filter="url(#glow)" opacity="0.6"/>')
    out.append(f'<rect x="{x0}" y="{ty - 6}" width="{scale(23) - x0:.1f}" height="12" rx="6" fill="url(#bar)"/>')
    for ms in (0, 10, 20, 30):
        out.append(f'<line x1="{scale(ms):.1f}" y1="{ty + 14}" x2="{scale(ms):.1f}" y2="{ty + 19}" stroke="{t["node_stroke"]}"/>')
        text(scale(ms), ty + 34, f"{ms}", 11, 500, "muted")
    for ms, label in ((14, "p50 · 14"), (23, "p99 · 23")):
        x = scale(ms)
        out.append(f'<rect x="{x - 34:.1f}" y="{ty - 46}" width="68" height="24" rx="12" fill="{t["accent_fill"]}" stroke="{t["accent_stroke"]}"/>')
        text(x, ty - 29.5, label, 12, 700, "accent")
        out.append(f'<circle cx="{x:.1f}" cy="{ty}" r="8" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="3.5"/>')

    # -- panel 2: burst waveform ------------------------------------------------
    px = PANEL_X[1]
    panel(px, "Two-source bursts · 双来源信号脉冲")
    big(px, "150", "signals / s", 140)
    bx0, bx1, base, top = px + 28, px + PANEL_W - 28, PANEL_Y + 232, PANEL_Y + 146
    seg = (bx1 - bx0) / 7
    path = f"M{bx0:.1f},{base}"
    for i in range(3):
        a = bx0 + seg * (2 * i + 0.5)
        b = a + seg
        path += (
            f" L{a:.1f},{base} C{a + 8:.1f},{base} {a + 4:.1f},{top} {a + 14:.1f},{top}"
            f" L{b - 14:.1f},{top} C{b - 4:.1f},{top} {b - 8:.1f},{base} {b:.1f},{base}"
        )
    path += f" L{bx1:.1f},{base}"
    out.append(f'<path d="{path} Z" fill="url(#area)"/>')
    out.append(f'<path d="{path}" fill="none" stroke="{t["glow"]}" stroke-width="6" opacity="0.35" filter="url(#glow)"/>')
    out.append(f'<path d="{path}" fill="none" stroke="{t["accent"]}" stroke-width="2.5" stroke-linejoin="round"/>')
    out.append(f'<line x1="{bx0}" y1="{top}" x2="{bx1}" y2="{top}" stroke="{t["accent_stroke"]}" stroke-dasharray="3 5"/>')
    for i in range(3):
        text(bx0 + seg * (2 * i + 1), base + 24, "5 s", 11, 500, "muted")

    # -- panel 3: fan-in of targets ---------------------------------------------
    px = PANEL_X[2]
    panel(px, "Multi-source following · 多来源跟随")
    big(px, "8", "targets", 68)
    cx, cy = px + 214, PANEL_Y + 200
    for i in range(8):
        sx, sy = px + 44, PANEL_Y + 142 + i * (116 / 7)
        out.append(
            f'<path d="M{sx + 8:.1f},{sy:.1f} C{sx + 90:.1f},{sy:.1f} {cx - 96:.1f},{cy} {cx - 30:.1f},{cy}" '
            f'fill="none" stroke="url(#wire)" stroke-width="1.8"/>'
        )
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="6" fill="{t["accent"]}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="52" fill="url(#halo)"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="28" fill="{t["inner"]}" stroke="{t["accent"]}" stroke-width="3.5"/>')
    out.append(f'<path d="M{cx - 7},{cy - 12} L{cx + 12},{cy} L{cx - 7},{cy + 12} Z" fill="{t["accent"]}"/>')
    hx = cx + 52
    out.append(f'<line x1="{cx + 32}" y1="{cy}" x2="{hx}" y2="{cy}" stroke="{t["accent"]}" stroke-width="2.5"/>')
    out.append(f'<rect x="{hx}" y="{cy - 15}" width="64" height="30" rx="15" fill="{t["accent"]}"/>')
    text(hx + 32, cy + 5, "HL", 13, 800, "bg")

    # -- footer: scope of each figure -------------------------------------------
    text(40, H - 48, "p99: local submission, 1,765 mainnet orders  ·  Bursts: 3 × 5 s per run, 10 runs, not sustained  ·  8: configured limit  ·  3 targets ≈ 144 h live", 11.5, 400, "muted", "start")
    text(40, H - 27, "p99 仅为本地提交；脉冲为短时峰值，非持续吞吐；8 为配置上限；3 个目标约 144 小时实盘", 11.5, 400, "muted", "start")

    desc = (
        "Multisource HL Copy performance: local submission p99 23 ms and p50 14 ms over 1,765 mainnet orders; "
        "two-source signal bursts of 150 per second in three 5-second bursts per run; up to 8 configurable targets "
        "converging into one engine; 3 targets run about 144 hours live."
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="title desc" font-family="{FONT}">\n'
        f'<title id="title">Multisource HL Copy · Performance · 性能</title>\n'
        f'<desc id="desc">{escape(desc)}</desc>\n'
        f'<defs>{"".join(defs)}</defs>\n' + "\n".join(out) + "\n</svg>\n"
    )


def main():
    for theme in THEMES:
        path = ASSETS / f"multisource-hl-copy-performance-{theme}.svg"
        path.write_text(build(theme), encoding="utf-8")
        print(f"wrote {path.relative_to(ASSETS.parent)}")


if __name__ == "__main__":
    main()
