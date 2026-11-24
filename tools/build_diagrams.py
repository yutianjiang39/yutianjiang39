"""Build the static architecture diagrams used in README.md.

Writes a light and a dark SVG per diagram into assets/. The files are plain
SVG with system fonts only, so they render the same wherever an <img> does.

    python tools/build_diagrams.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

ASSETS = Path(__file__).resolve().parent.parent / "assets"

FONT = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, "
    "'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif"
)

THEMES = {
    "light": {
        "bg": "#FFFFFF",
        "frame": "#D8DEE4",
        "node": "#F6F8FA",
        "node_stroke": "#CFD6DD",
        "text": "#1F2328",
        "muted": "#59636E",
        "line": "#6E7781",
        "accent": "#1B7F79",
        "accent_fill": "#EEF8F6",
        "accent_stroke": "#8CCDC6",
        "inner": "#FFFFFF",
        "warn": "#9A6700",
        "warn_fill": "#FFF8E5",
        "warn_stroke": "#E3C272",
    },
    "dark": {
        "bg": "#0D1117",
        "frame": "#30363D",
        "node": "#161B22",
        "node_stroke": "#3A424B",
        "text": "#E6EDF3",
        "muted": "#9198A1",
        "line": "#8B949E",
        "accent": "#3FB8AF",
        "accent_fill": "#0F2422",
        "accent_stroke": "#256D68",
        "inner": "#0D1117",
        "warn": "#D29922",
        "warn_fill": "#231B0A",
        "warn_stroke": "#6B5216",
    },
}


class Diagram:
    def __init__(self, width, height, theme, title, desc, eyebrow):
        self.w, self.h, self.t = width, height, THEMES[theme]
        self.title, self.desc = title, desc
        self.back, self.front = [], []
        self._header(eyebrow)

    # -- primitives ---------------------------------------------------------

    def text(self, x, y, s, size=13, weight=400, fill="text", anchor="middle", spacing=None, layer=None):
        extra = f' letter-spacing="{spacing}"' if spacing else ""
        (self.front if layer is None else layer).append(
            f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{self.t[fill]}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'
        )

    def _header(self, eyebrow):
        t = self.t
        self.back.append(
            f'<rect x="0.5" y="0.5" width="{self.w - 1}" height="{self.h - 1}" rx="14" '
            f'fill="{t["bg"]}" stroke="{t["frame"]}"/>'
        )
        self.back.append(f'<rect x="40" y="33" width="4" height="14" rx="2" fill="{t["accent"]}"/>')
        self.text(54, 45, eyebrow, 12, 700, "accent", "start", spacing="1.2")
        self.text(54 + len(eyebrow) * 9.1 + 8, 45, "Architecture · 系统架构", 12.5, 400, "muted", "start")
        # legend, right-aligned
        x = self.w - 40
        self.text(x, 45, "Control · 控制", 12, 400, "muted", "end")
        self.back.append(
            f'<path d="M{x - 122},41 H{x - 92}" stroke="{t["line"]}" stroke-width="1.5" '
            f'stroke-dasharray="5 4" marker-end="url(#a-line)"/>'
        )
        self.text(x - 146, 45, "Data flow · 数据流", 12, 400, "muted", "end")
        self.back.append(
            f'<path d="M{x - 296},41 H{x - 266}" stroke="{t["line"]}" stroke-width="1.5" '
            f'marker-end="url(#a-line)"/>'
        )

    def node(self, x, y, w, h, en, zh=None, kind="node", stacked=False):
        t = self.t
        fill, stroke = {
            "node": (t["node"], t["node_stroke"]),
            "inner": (t["inner"], t["accent_stroke"]),
            "warn": (t["warn_fill"], t["warn_stroke"]),
        }[kind]
        if stacked:
            for d, op in ((8, 0.45), (4, 0.75)):
                self.front.append(
                    f'<rect x="{x + d}" y="{y - d}" width="{w}" height="{h}" rx="10" '
                    f'fill="{fill}" stroke="{stroke}" opacity="{op}"/>'
                )
        self.front.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}"/>'
        )
        cx, cy = x + w / 2, y + h / 2
        title_fill = "warn" if kind == "warn" else "text"
        if zh:
            self.text(cx, cy - 4, en, 15, 600, title_fill)
            self.text(cx, cy + 16, zh, 13, 400, "muted")
        else:
            self.text(cx, cy + 6, en, 17, 600, title_fill)

    def store(self, x, y, w, h, en, zh, kind="node"):
        """Cylinder: a persistent store."""
        t = self.t
        fill, stroke = (t["inner"], t["accent_stroke"]) if kind == "inner" else (t["node"], t["node_stroke"])
        rx, ry = w / 2, 9
        self.front.append(
            f'<path d="M{x},{y + ry} A{rx},{ry} 0 0 1 {x + w},{y + ry} V{y + h - ry} '
            f'A{rx},{ry} 0 0 1 {x},{y + h - ry} Z" fill="{fill}" stroke="{stroke}"/>'
        )
        self.front.append(
            f'<path d="M{x},{y + ry} A{rx},{ry} 0 0 0 {x + w},{y + ry}" fill="none" stroke="{stroke}"/>'
        )
        cx, cy = x + w / 2, y + h / 2 + 6
        self.text(cx, cy - 4, en, 15, 600)
        self.text(cx, cy + 16, zh, 13, 400, "muted")

    def group(self, x, y, w, h, label):
        t = self.t
        self.back.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" '
            f'fill="{t["accent_fill"]}" stroke="{t["accent_stroke"]}"/>'
        )
        self.text(x + 20, y + 29, label, 13.5, 700, "accent", "start", layer=self.back)

    def edge(self, pts, dashed=False, color="line", arrow=True, r=8):
        """Orthogonal polyline with rounded corners."""
        d = [f"M{pts[0][0]},{pts[0][1]}"]
        for i in range(1, len(pts) - 1):
            (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]

            def toward(ax, ay, bx, by):
                dist = abs(bx - ax) + abs(by - ay)
                k = min(r, dist / 2) / dist
                return ax + (bx - ax) * k, ay + (by - ay) * k

            ex, ey = toward(x1, y1, x0, y0)
            fx, fy = toward(x1, y1, x2, y2)
            d.append(f"L{ex:g},{ey:g} Q{x1},{y1} {fx:g},{fy:g}")
        d.append(f"L{pts[-1][0]},{pts[-1][1]}")
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        head = f' marker-end="url(#a-{color})"' if arrow else ""
        self.back.append(
            f'<path d="{" ".join(d)}" fill="none" stroke="{self.t[color]}" stroke-width="1.5" '
            f'stroke-linecap="round"{dash}{head}/>'
        )

    def dot(self, x, y, color="line"):
        self.back.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{self.t[color]}"/>')

    def label(self, x, y, en, zh, anchor="middle"):
        """Two-line edge label; y is the baseline of the first line."""
        self.text(x, y, en, 12.5, 500, "text", anchor)
        self.text(x, y + 16, zh, 12, 400, "muted", anchor)

    # -- output -------------------------------------------------------------

    def render(self):
        t = self.t
        markers = "".join(
            f'<marker id="a-{k}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M1,1.5 L9,5 L1,8.5 Z" fill="{t[k]}"/></marker>'
            for k in ("line", "warn")
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="title desc" '
            f'font-family="{FONT}">\n'
            f'<title id="title">{escape(self.title)}</title>\n'
            f'<desc id="desc">{escape(self.desc)}</desc>\n'
            f"<defs>{markers}</defs>\n" + "\n".join(self.back + self.front) + "\n</svg>\n"
        )


def multisource(theme):
    d = Diagram(
        960, 642, theme,
        "Multisource HL Copy architecture · 系统架构",
        "Source wallets send order and fill events to the Rust execution engine, which holds order "
        "lifecycle mirroring, position following and persistent state. The engine places, modifies and "
        "cancels orders on Hyperliquid and receives its own order and fill updates. A deterministic risk "
        "guard can pause, cancel or flatten. A Python control plane starts, stops and configures the "
        "engine. Engine and risk guard feed alerts and periodic reports.",
        "MULTISOURCE HL COPY",
    )
    # inputs
    d.node(60, 88, 210, 68, "Source wallets", "来源钱包（多个）", stacked=True)
    d.node(290, 88, 210, 68, "Python control plane", "Python 控制面")
    d.edge([(165, 156), (165, 216)])
    d.label(178, 183, "order & fill events", "委托与成交事件", "start")
    d.edge([(395, 156), (395, 216)], dashed=True)
    d.label(408, 183, "start · stop · config", "启停 · 配置", "start")

    # engine
    d.group(40, 216, 480, 258, "Rust execution engine · Rust 执行引擎")
    d.edge([(165, 330), (165, 352), (235, 352), (235, 384)], arrow=False, color="accent_stroke")
    d.edge([(395, 330), (395, 352), (325, 352), (325, 384)], arrow=False, color="accent_stroke")
    d.node(60, 262, 210, 68, "Order lifecycle mirroring", "委托生命周期镜像", kind="inner")
    d.node(290, 262, 210, 68, "Position following", "仓位跟随", kind="inner")
    d.store(170, 372, 220, 76, "Persistent state", "持久化状态", kind="inner")

    # venue
    d.node(700, 262, 220, 186, "Hyperliquid")
    d.edge([(520, 310), (700, 310)])
    d.label(610, 283, "place / modify / cancel", "下单 / 改单 / 撤单")
    d.edge([(700, 414), (520, 414)])
    d.label(610, 387, "own order & fill updates", "本方委托与成交回报")

    # risk guard and outputs
    d.node(40, 534, 210, 68, "Risk guard", "确定性风控", kind="warn")
    d.edge([(100, 474), (100, 534)])
    d.edge([(190, 534), (190, 474)], dashed=True, color="warn")
    d.label(203, 501, "pause · cancel · flatten", "暂停 · 撤单 · 平仓", "start")
    d.node(700, 534, 220, 68, "Alerts & periodic reports", "事件提醒与周期报告")
    d.edge([(250, 568), (700, 568)])
    d.edge([(440, 474), (440, 568)], arrow=False, r=0)
    d.dot(440, 568)
    return d.render()


def monitor(theme):
    d = Diagram(
        960, 748, theme,
        "Hyperliquid Monitor architecture · 系统架构",
        "The official API, the official S3 archive and local JSON or CSV files feed a collector that "
        "deduplicates into a per-wallet SQLite cache. The cache feeds metrics and a mark-to-market "
        "rebuild. The rebuild is reconciled weekly against the official portfolio figures. Metrics and "
        "reconciliation produce an offline HTML report with CSV and audit files. A Textual TUI and CLI "
        "drive the collector and the report.",
        "HYPERLIQUID MONITOR",
    )
    # sources -> collector
    d.node(40, 84, 200, 64, "Official API", "官方 API")
    d.node(260, 84, 200, 64, "Official S3 archive", "官方 S3 归档")
    d.node(480, 84, 200, 64, "Local files (JSON / CSV)", "本地文件导入")
    d.edge([(140, 148), (140, 172), (360, 172)], arrow=False)
    d.edge([(580, 148), (580, 172), (360, 172)], arrow=False)
    d.edge([(360, 148), (360, 196)])
    d.dot(360, 172)
    d.node(260, 196, 200, 64, "Collector", "采集与去重")

    # cache
    d.edge([(360, 260), (360, 308)])
    d.store(250, 308, 220, 68, "Per-wallet SQLite cache", "按钱包的 SQLite 缓存")

    # analysis
    d.edge([(360, 376), (360, 420)])
    d.edge([(360, 398), (140, 398), (140, 420)])
    d.dot(360, 398)
    d.node(40, 420, 200, 64, "Metrics", "收益 · 风险 · 行为 · 成本")
    d.node(260, 420, 200, 64, "Mark-to-market rebuild", "盯市重建")
    d.edge([(360, 484), (360, 532)])
    d.node(260, 532, 200, 64, "Weekly reconciliation", "逐周对账（残差公开）")
    d.node(520, 532, 220, 64, "Official portfolio figures", "官方 portfolio 数据")
    d.edge([(520, 564), (460, 564)])

    # report
    d.edge([(140, 484), (140, 644)])
    d.edge([(360, 596), (360, 644)])
    d.node(40, 644, 420, 64, "Offline HTML report + CSV / audit files", "离线 HTML 报告 + CSV / 审计文件")

    # driver
    d.node(740, 196, 180, 64, "Textual TUI / CLI", "终端界面 / 命令行")
    d.edge([(740, 228), (460, 228)], dashed=True)
    d.text(600, 218, "runs · 驱动", 12.5, 500, "text")
    d.edge([(830, 260), (830, 676), (460, 676)], dashed=True)
    return d.render()


def main():
    ASSETS.mkdir(exist_ok=True)
    for name, build in (("multisource-hl-copy-architecture", multisource), ("hyperliquid-monitor-architecture", monitor)):
        for theme in THEMES:
            path = ASSETS / f"{name}-{theme}.svg"
            path.write_text(build(theme), encoding="utf-8", newline="\n")
            print(path.relative_to(ASSETS.parent))


if __name__ == "__main__":
    main()
