"""Build the visual performance highlight for Multisource HL Copy.

Three columns, left to right: source wallets -> execution engine -> Hyperliquid.
Each column has an icon card in the flow row and its figure directly beneath.
Writes a light and a dark SVG into assets/. Figures come from the project's
published performance summary; their scope is stated in the footer.

    python tools/build_highlights.py
"""

from xml.sax.saxutils import escape

from build_diagrams import ASSETS, FONT, THEMES

W, H = 1200, 500
COLS = (190, 600, 1010)
CARD_W, CARD_H, CARD_Y = 230, 168, 92
ICON_Y = 150

EXTRA = {
    "light": {"hi": "#1B7F79", "down": "#CF222E"},
    "dark": {"hi": "#7CE0D6", "down": "#F85149"},
}


def build(theme):
    t = {**THEMES[theme], **EXTRA[theme]}
    out = []

    def text(x, y, s, size=13, weight=400, fill="text", anchor="middle", extra=""):
        out.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{t[fill]}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'
        )

    def card(cx, title, subtitle):
        x = cx - CARD_W / 2
        out.append(
            f'<rect x="{x}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="14" '
            f'fill="{t["node"]}" stroke="{t["node_stroke"]}" stroke-width="1.2"/>'
        )
        text(cx, CARD_Y + 128, title, 16, 700, "text")
        text(cx, CARD_Y + 150, subtitle, 13, 400, "muted")

    def metric(cx, value, unit, caption):
        out.append(
            f'<text x="{cx}" y="346" text-anchor="middle" font-weight="800" fill="{t["text"]}">'
            f'<tspan font-size="56" letter-spacing="-1.5">{escape(value)}</tspan>'
            f'<tspan font-size="20" font-weight="600" fill="{t["accent"]}" dx="8">{escape(unit)}</tspan></text>'
        )
        text(cx, 376, caption, 14, 500, "muted")

    def wallet(cx, cy):
        x, y = cx - 15, cy - 11
        out.append(f'<rect x="{x}" y="{y}" width="30" height="22" rx="4" fill="{t["accent_fill"]}" stroke="{t["accent"]}" stroke-width="2"/>')
        out.append(f'<path d="M{x + 3},{y} L{x + 22},{y - 5} L{x + 24},{y}" fill="none" stroke="{t["accent"]}" stroke-width="2" stroke-linejoin="round"/>')
        out.append(f'<rect x="{x + 18}" y="{cy - 5}" width="12" height="10" rx="3" fill="{t["node"]}" stroke="{t["accent"]}" stroke-width="2"/>')
        out.append(f'<circle cx="{x + 23}" cy="{cy}" r="1.8" fill="{t["accent"]}"/>')

    def chip(cx, cy):
        s = 52
        x, y = cx - s / 2, cy - s / 2
        for k in (-14, 0, 14):
            out.append(f'<line x1="{cx + k}" y1="{y - 9}" x2="{cx + k}" y2="{y}" stroke="{t["accent"]}" stroke-width="3" stroke-linecap="round"/>')
            out.append(f'<line x1="{cx + k}" y1="{y + s}" x2="{cx + k}" y2="{y + s + 9}" stroke="{t["accent"]}" stroke-width="3" stroke-linecap="round"/>')
            out.append(f'<line x1="{x - 9}" y1="{cy + k}" x2="{x}" y2="{cy + k}" stroke="{t["accent"]}" stroke-width="3" stroke-linecap="round"/>')
            out.append(f'<line x1="{x + s}" y1="{cy + k}" x2="{x + s + 9}" y2="{cy + k}" stroke="{t["accent"]}" stroke-width="3" stroke-linecap="round"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="9" fill="{t["accent_fill"]}" stroke="{t["accent"]}" stroke-width="3"/>')
        out.append(
            f'<path d="M{cx + 3},{cy - 15} L{cx - 9},{cy + 3} L{cx - 1},{cy + 3} L{cx - 3},{cy + 15} L{cx + 9},{cy - 3} L{cx + 1},{cy - 3} Z" '
            f'fill="{t["accent"]}"/>'
        )

    def candles(cx, cy):
        spec = ((-30, 6, 22, 14, True), (-10, -8, 26, 12, False), (10, -14, 30, 16, True), (30, -26, 34, 18, True))
        out.append(f'<line x1="{cx - 46}" y1="{cy + 30}" x2="{cx + 46}" y2="{cy + 30}" stroke="{t["node_stroke"]}" stroke-width="2"/>')
        for dx, top, wick, body, up in spec:
            colour = t["accent"] if up else t["down"]
            x = cx + dx
            out.append(f'<line x1="{x}" y1="{cy + top - 4}" x2="{x}" y2="{cy + top + wick}" stroke="{colour}" stroke-width="2"/>')
            out.append(f'<rect x="{x - 6}" y="{cy + top + (wick - body) / 2 - 2}" width="12" height="{body}" rx="2" fill="{colour}"/>')

    # canvas + header
    out.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t["bg"]}" stroke="{t["frame"]}"/>')
    out.append(f'<rect x="40" y="36" width="4" height="18" rx="2" fill="{t["accent"]}"/>')
    text(54, 51, "MULTISOURCE HL COPY", 13, 700, "accent", "start", ' letter-spacing="1.4"')
    text(W - 40, 51, "Performance · 性能", 13, 500, "muted", "end")

    # connectors (behind cards)
    a_x, b_x = COLS[0] + CARD_W / 2, COLS[1] - CARD_W / 2
    for i in range(8):
        sy = ICON_Y - 28 + i * 8
        out.append(
            f'<path d="M{a_x},{sy} C{a_x + 90},{sy} {b_x - 90},{ICON_Y} {b_x},{ICON_Y}" '
            f'fill="none" stroke="{t["accent_stroke"]}" stroke-width="1.6"/>'
        )
    c_x, d_x = COLS[1] + CARD_W / 2, COLS[2] - CARD_W / 2
    out.append(f'<line x1="{c_x}" y1="{ICON_Y}" x2="{d_x - 12}" y2="{ICON_Y}" stroke="{t["accent"]}" stroke-width="3"/>')
    out.append(f'<path d="M{d_x - 14},{ICON_Y - 8} L{d_x},{ICON_Y} L{d_x - 14},{ICON_Y + 8} Z" fill="{t["accent"]}"/>')

    # cards
    card(COLS[0], "Source wallets", "来源钱包")
    for r in range(2):
        for c in range(4):
            wallet(COLS[0] - 66 + c * 44, ICON_Y - 20 + r * 40)
    card(COLS[1], "Execution engine", "执行引擎 · Rust")
    chip(COLS[1], ICON_Y)
    card(COLS[2], "Hyperliquid", "交易所 · Exchange")
    candles(COLS[2], ICON_Y - 4)

    # figures, one per column
    metric(COLS[0], "8", "targets", "Followed in parallel · 同时跟随")
    metric(COLS[1], "150", "/ s", "Signal bursts · 信号脉冲")
    metric(COLS[2], "23", "ms p99", "Local submit · 本地提交")

    # footer: scope of each figure
    out.append(f'<line x1="40" y1="{H - 82}" x2="{W - 40}" y2="{H - 82}" stroke="{t["frame"]}"/>')
    text(40, H - 52, "8: configured limit  ·  150/s: 3 × 5 s bursts per run, 10 runs, not sustained  ·  23 ms: local submission p99 (p50 14 ms), 1,765 mainnet orders", 12, 400, "muted", "start")
    text(40, H - 30, "8 为配置上限；150/s 为短时脉冲，非持续吞吐；23 ms 为本地提交 p99 (p50 14 ms)，基于 1,765 笔主网订单", 12, 400, "muted", "start")

    desc = (
        "Multisource HL Copy: up to 8 source wallets are followed in parallel by a Rust execution engine that "
        "handles signal bursts of 150 per second and submits to Hyperliquid with local submission latency of "
        "p99 23 ms (p50 14 ms) over 1,765 mainnet orders."
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="title desc" font-family="{FONT}">\n'
        f'<title id="title">Multisource HL Copy · Performance · 性能</title>\n'
        f'<desc id="desc">{escape(desc)}</desc>\n' + "\n".join(out) + "\n</svg>\n"
    )


def main():
    for theme in THEMES:
        path = ASSETS / f"multisource-hl-copy-performance-{theme}.svg"
        path.write_text(build(theme), encoding="utf-8")
        print(f"wrote {path.relative_to(ASSETS.parent)}")


if __name__ == "__main__":
    main()
