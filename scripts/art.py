"""Build the profile's animated art: the banner and the typing line, dark and light.

Run with: python3 scripts/art.py
Writes assets/banner-{dark,light}.svg and assets/typing-{dark,light}.svg.
Stdlib only. Every shape is placed by a seeded generator, so a rerun writes
byte-identical files. Motion is CSS @keyframes inside each SVG, and
prefers-reduced-motion stops all of it.
"""

import math
import random
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

SANS = "'Arial Black','Helvetica Neue',Helvetica,Arial,system-ui,sans-serif"
TEXT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

THEMES = {
    "dark": {
        "bg0": "#1c0e03", "bg1": "#0b0d12", "bg2": "#06070a",
        "grid": "#ffffff", "grid_op": "0.045",
        "aura0": "#ffd15c", "aura1": "#ff8a1c", "aura2": "#ff4d0a",
        "aura_op": "0.55", "glow_op": "0.75",
        "w0": "#fff1b8", "w1": "#ffc53d", "w2": "#ff8a1c", "w3": "#ff5a12",
        "spark": "#ffe08a", "bolt": "#fff6d6",
        "tag": "#e9edf2", "road": "#ffb547", "muted": "#7d8794",
        "rail": "#1d222b", "seg0": "#ff6a13", "seg1": "#ffd15c",
        "site": "#ffd15c", "shine": "#ffffff", "shine_op": "0.85",
    },
    "light": {
        "bg0": "#fff3df", "bg1": "#fffaf3", "bg2": "#ffffff",
        "grid": "#3a2a14", "grid_op": "0.05",
        "aura0": "#ffb020", "aura1": "#ff7a18", "aura2": "#e2450a",
        "aura_op": "0.30", "glow_op": "0.35",
        "w0": "#f29a00", "w1": "#e86a06", "w2": "#d44a07", "w3": "#a8330a",
        "spark": "#f08a00", "bolt": "#ffb020",
        "tag": "#1f2328", "road": "#c2410c", "muted": "#6b7482",
        "rail": "#efe6da", "seg0": "#e2580a", "seg1": "#f5a524",
        "site": "#c2410c", "shine": "#fff8e6", "shine_op": "0.9",
    },
}

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def flame(cx, base, w, h, lean):
    """One tongue of the aura: a closed curve from a base point to a leaning tip."""
    tip_x, tip_y = cx + lean, base - h
    return (
        f"M{cx - w:.1f},{base:.1f}"
        f"C{cx - w * 0.9:.1f},{base - h * 0.45:.1f} {tip_x - w * 0.25:.1f},{tip_y + h * 0.35:.1f} {tip_x:.1f},{tip_y:.1f}"
        f"C{tip_x + w * 0.25:.1f},{tip_y + h * 0.35:.1f} {cx + w * 0.9:.1f},{base - h * 0.45:.1f} {cx + w:.1f},{base:.1f}Z"
    )


def bolt(rng, x, y, length, angle):
    """A jagged lightning polyline, the Super Saiyan 2 crackle."""
    pts = [(x, y)]
    steps = 6
    for i in range(1, steps + 1):
        t = i / steps
        px = x + math.cos(angle) * length * t + rng.uniform(-9, 9)
        py = y + math.sin(angle) * length * t + rng.uniform(-9, 9)
        pts.append((px, py))
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)


def banner(theme):
    c = THEMES[theme]
    rng = random.Random(9001)
    out = []
    w = out.append

    w('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 400" width="1280" height="400" role="img" '
      'aria-label="The Mad Saiyantist. Machine learning, from zero to production. Python to ML to MLOps. '
      '7 modules, 39 sections, 130 lessons, all live at themadsaiyantist.com">')
    w("<style>")
    w("@keyframes flick{0%,100%{transform:scale(1,1);opacity:.85}25%{transform:scale(.94,1.12);opacity:1}"
      "50%{transform:scale(1.04,.9);opacity:.7}75%{transform:scale(.97,1.18);opacity:.95}}")
    w("@keyframes pulse{0%,100%{transform:scale(.94);opacity:.75}50%{transform:scale(1.06);opacity:1}}")
    w("@keyframes rise{0%{transform:translate(0,0);opacity:0}15%{opacity:1}100%{transform:translate(var(--dx),-170px);opacity:0}}")
    w("@keyframes zap{0%,91%,95%,100%{opacity:0}92%,94%{opacity:1}93%{opacity:.25}}")
    w("@keyframes shine{0%,62%{transform:translateX(-360px)}100%{transform:translateX(1500px)}}")
    w("@keyframes charge{0%{transform:translateX(-140px);opacity:0}10%{opacity:1}80%{opacity:1}100%{transform:translateX(560px);opacity:0}}")
    w("@keyframes hum{0%,100%{opacity:.8}50%{opacity:1}}")
    w(".f{transform-box:fill-box;transform-origin:50% 100%;animation:flick var(--d) ease-in-out var(--l) infinite}")
    w(".p{transform-box:fill-box;transform-origin:50% 50%;animation:pulse 4.2s ease-in-out infinite}")
    w(".s{opacity:.55;animation:rise var(--d) linear var(--l) infinite}")
    w(".z{opacity:0;animation:zap var(--d) steps(1,end) var(--l) infinite}")
    w(".sh{animation:shine 7s cubic-bezier(.4,0,.2,1) 1s infinite}")
    w(".c{opacity:0;animation:charge 3.6s ease-in-out infinite}")
    w(".g{animation:hum 2.4s ease-in-out infinite}")
    w(REDUCED)
    w("</style>")

    w("<defs>")
    w(f'<radialGradient id="bg" cx="50%" cy="46%" r="75%"><stop offset="0" stop-color="{c["bg0"]}"/>'
      f'<stop offset=".55" stop-color="{c["bg1"]}"/><stop offset="1" stop-color="{c["bg2"]}"/></radialGradient>')
    w(f'<radialGradient id="core" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{c["aura0"]}" stop-opacity="{c["glow_op"]}"/>'
      f'<stop offset=".45" stop-color="{c["aura1"]}" stop-opacity=".22"/><stop offset="1" stop-color="{c["aura2"]}" stop-opacity="0"/></radialGradient>')
    w(f'<linearGradient id="fl" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{c["aura0"]}" stop-opacity="0"/>'
      f'<stop offset=".22" stop-color="{c["aura0"]}"/><stop offset=".6" stop-color="{c["aura1"]}"/>'
      f'<stop offset="1" stop-color="{c["aura2"]}" stop-opacity="0"/></linearGradient>')
    w(f'<linearGradient id="wd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["w0"]}"/>'
      f'<stop offset=".45" stop-color="{c["w1"]}"/><stop offset=".75" stop-color="{c["w2"]}"/><stop offset="1" stop-color="{c["w3"]}"/></linearGradient>')
    w(f'<linearGradient id="sg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["shine"]}" stop-opacity="0"/>'
      f'<stop offset=".5" stop-color="{c["shine"]}" stop-opacity="{c["shine_op"]}"/><stop offset="1" stop-color="{c["shine"]}" stop-opacity="0"/></linearGradient>')
    w(f'<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["seg0"]}"/><stop offset="1" stop-color="{c["seg1"]}"/></linearGradient>')
    w(f'<linearGradient id="ru" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["aura1"]}" stop-opacity="0"/>'
      f'<stop offset=".5" stop-color="{c["aura1"]}" stop-opacity=".8"/><stop offset="1" stop-color="{c["aura1"]}" stop-opacity="0"/></linearGradient>')
    w('<radialGradient id="fade" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>')
    w('<mask id="gm"><rect width="1280" height="400" fill="url(#fade)"/></mask>')
    w('<filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7"/></filter>')
    w('<filter id="haze" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="12"/></filter>')
    w('<filter id="soft" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="14"/></filter>')
    word = (f'<text x="640" y="172" text-anchor="middle" font-family="{SANS}" font-size="86" font-weight="900" '
            f'textLength="1040" lengthAdjust="spacingAndGlyphs">THE MAD SAIYANTIST</text>')
    w(f'<clipPath id="wc">{word}</clipPath>')
    w("</defs>")

    w('<rect width="1280" height="400" fill="url(#bg)"/>')

    # grid, faded toward the edges
    lines = "".join(f"M0 {y}H1280" for y in range(40, 400, 40)) + "".join(f"M{x} 0V400" for x in range(40, 1280, 40))
    w(f'<path d="{lines}" stroke="{c["grid"]}" stroke-opacity="{c["grid_op"]}" mask="url(#gm)"/>')

    # the core glow, breathing
    w(f'<g opacity="{c["aura_op"]}"><ellipse class="p" cx="640" cy="160" rx="620" ry="190" fill="url(#core)"/></g>')

    # the aura: an outer haze of tall tongues, then a tighter, brighter inner ring
    for layer, count, spread, tall, widths, filt, op in (
        ("outer", 22, 560, (170, 120), (30, 46), "haze", 1.0),
        ("inner", 30, 520, (120, 80), (14, 24), "blur", 1.0),
    ):
        w(f'<g filter="url(#{filt})" opacity="{c["aura_op"]}">')
        for i in range(count):
            cx = 640 - spread + (2 * spread) * i / (count - 1) + rng.uniform(-10, 10)
            dist = abs(cx - 640) / spread
            h = tall[0] * (1 - dist * 0.55) + tall[1] * (1 - dist) + rng.uniform(-20, 20)
            fw = rng.uniform(*widths)
            lean = (cx - 640) * 0.07 + rng.uniform(-12, 12)
            base = 222 - (1 - dist) * 12 + rng.uniform(-8, 8)
            d = rng.uniform(0.9, 1.9) if layer == "inner" else rng.uniform(1.6, 2.6)
            lag = -rng.uniform(0, 2)
            w(f'<path class="f" style="--d:{d:.2f}s;--l:{lag:.2f}s" d="{flame(cx, base, fw, h, lean)}" fill="url(#fl)"/>')
        w("</g>")

    # rising sparks
    w(f'<g fill="{c["spark"]}">')
    for i in range(34):
        x = rng.uniform(70, 1210)
        y = rng.uniform(250, 390)
        r = rng.uniform(1.2, 2.8)
        d = rng.uniform(2.8, 6.0)
        lag = -rng.uniform(0, 6)
        dx = rng.uniform(-18, 18)
        if i % 3 == 0:
            w(f'<path class="s" style="--d:{d:.2f}s;--l:{lag:.2f}s;--dx:{dx:.0f}px" '
              f'd="M{x:.1f},{y - r * 3:.1f}L{x + r:.1f},{y:.1f}L{x:.1f},{y + r * 1.2:.1f}L{x - r:.1f},{y:.1f}Z"/>')
        else:
            w(f'<circle class="s" style="--d:{d:.2f}s;--l:{lag:.2f}s;--dx:{dx:.0f}px" cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>')
    w("</g>")

    # lightning, flashing at odd beats
    w(f'<g fill="none" stroke="{c["bolt"]}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">')
    for x, y, ln, ang, d, lag in [
        (118, 92, 120, 0.9, 3.1, 0.0), (1162, 88, 125, 2.2, 3.7, -1.3),
        (300, 250, 90, -0.6, 4.3, -2.2), (980, 255, 95, -2.5, 4.9, -0.7),
        (60, 230, 80, -1.1, 5.3, -3.1), (1225, 240, 85, -2.0, 4.1, -2.6),
    ]:
        w(f'<polyline class="z" style="--d:{d}s;--l:{lag}s" points="{bolt(rng, x, y, ln, ang)}"/>')
    w("</g>")

    # wordmark: blurred glow copy, solid fill, then a shine sweep clipped to the letters
    w(f'<g class="g" filter="url(#soft)" opacity="{c["glow_op"]}" fill="{c["aura1"]}">{word}</g>')
    w(f'<g fill="url(#wd)">{word}</g>')
    w('<g clip-path="url(#wc)"><g transform="skewX(-20)"><rect class="sh" x="0" y="80" width="220" height="110" fill="url(#sg)"/></g></g>')

    w('<rect x="300" y="196" width="680" height="2" fill="url(#ru)"/>')

    w(f'<text x="640" y="238" text-anchor="middle" font-family="{TEXT}" font-size="26" font-weight="600" '
      f'fill="{c["tag"]}">Machine learning, from zero to production.</text>')
    w(f'<text x="640" y="272" text-anchor="middle" font-family="{MONO}" font-size="17" letter-spacing="5" '
      f'fill="{c["road"]}">PYTHON → ML → DEEP LEARNING → MLOPS</text>')

    # the power rail: seven modules, all lit, with a charge running through
    x0, seg, gap = 430, 54, 6
    w(f'<g font-family="{MONO}" font-size="11" letter-spacing="2" fill="{c["muted"]}">')
    w(f'<text x="{x0 - 16}" y="318" text-anchor="end">POWER</text>')
    w(f'<text x="{x0 + 7 * seg + 6 * gap + 16}" y="318">MAX</text>')
    w("</g>")
    w(f'<rect x="{x0 - 4}" y="304" width="{7 * seg + 6 * gap + 8}" height="20" rx="5" fill="{c["rail"]}"/>')
    segs = "".join(f'<rect x="{x0 + i * (seg + gap)}" y="308" width="{seg}" height="12" rx="3"/>' for i in range(7))
    w(f'<clipPath id="bc">{segs}</clipPath>')
    w(f'<g fill="url(#bar)">{segs}</g>')
    w(f'<g clip-path="url(#bc)"><rect class="c" x="{x0}" y="308" width="110" height="12" fill="url(#sg)"/></g>')
    w(f'<g font-family="{MONO}" font-size="11" letter-spacing="1" fill="{c["muted"]}" text-anchor="middle">')
    for i in range(7):
        w(f'<text x="{x0 + i * (seg + gap) + seg / 2:.0f}" y="342">M{i}</text>')
    w("</g>")

    w(f'<text x="640" y="374" text-anchor="middle" font-family="{MONO}" font-size="15" letter-spacing="3" '
      f'fill="{c["muted"]}">7 MODULES · 39 SECTIONS · 130 LESSONS · '
      f'<tspan fill="{c["site"]}" font-weight="700">THEMADSAIYANTIST.COM</tspan></text>')
    w("</svg>")
    return "\n".join(out) + "\n"


LINES = [
    "7 modules, 39 sections, 130 lessons. Every lesson free.",
    "From your first terminal to a monitored model in production.",
    "Build it. Break it. Observe it. Fix it. Explain it.",
    "Coding Agents: 15 free lessons on Claude Code.",
    "Free to learn, pay to prove it.",
]


def typing(theme):
    c = THEMES[theme]
    size, cw = 20, 12.0
    slot, n = 4.4, len(LINES)
    total = slot * n
    x0, y = 60, 33
    width = 900
    # start the cycle with the first line already typed, so a still frame at t=0 shows a full sentence
    lead = f"{-slot * 0.5:.2f}"
    out = []
    w = out.append
    w(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 50" width="{width}" height="50" role="img" '
      f'aria-label="{" ".join(LINES)}">')
    w("<style>")
    w("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}")
    w(".k{animation:blink 1s steps(1,end) infinite}")
    for i, line in enumerate(LINES):
        k = len(line)
        a = i / n * 100
        b = (i + 1) / n * 100
        span = b - a
        typed = a + span * 0.42
        hold = a + span * 0.86
        gone = a + span * 0.97
        lw = k * cw
        pre = f"0%,{a:.2f}%{{transform:scaleX(0);animation-timing-function:steps({k},end)}}" if a > 0 else \
            f"0%{{transform:scaleX(0);animation-timing-function:steps({k},end)}}"
        w(f"@keyframes t{i}{{{pre}{typed:.2f}%,{hold:.2f}%{{transform:scaleX(1);animation-timing-function:steps({k},end)}}"
          f"{gone:.2f}%,100%{{transform:scaleX(0)}}}}")
        pre = f"0%,{a:.2f}%{{transform:translateX(0);animation-timing-function:steps({k},end)}}" if a > 0 else \
            f"0%{{transform:translateX(0);animation-timing-function:steps({k},end)}}"
        w(f"@keyframes m{i}{{{pre}{typed:.2f}%,{hold:.2f}%{{transform:translateX({lw:.0f}px);animation-timing-function:steps({k},end)}}"
          f"{gone:.2f}%,100%{{transform:translateX(0)}}}}")
        w(f"@keyframes v{i}{{0%{{opacity:0}}{a:.2f}%,{gone:.2f}%{{opacity:1}}{min(gone + 0.01, 100):.2f}%,100%{{opacity:0}}}}")
        w(f".r{i}{{transform-box:fill-box;transform-origin:0 0;animation:t{i} {total:.1f}s {lead}s infinite}}")
        w(f".m{i}{{animation:m{i} {total:.1f}s {lead}s infinite}}")
        w(f".v{i}{{opacity:0;animation:v{i} {total:.1f}s steps(1,end) {lead}s infinite}}")
    # with motion reduced, the first line stands typed in full and the cursor stays put
    w("@media (prefers-reduced-motion: reduce){*{animation:none!important}.v0{opacity:1}.r0{transform:none}"
      f".m0{{transform:translateX({len(LINES[0]) * cw:.0f}px)}}}}")
    w("</style>")
    w("<defs>")
    for i, line in enumerate(LINES):
        w(f'<clipPath id="c{i}"><rect class="r{i}" x="{x0}" y="6" width="{len(line) * cw:.0f}" height="38"/></clipPath>')
    w("</defs>")
    w(f'<text x="{x0 - 26}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="700" fill="{c["road"]}">❯</text>')
    for i, line in enumerate(LINES):
        lw = len(line) * cw
        w(f'<g class="v{i}">')
        w(f'<text clip-path="url(#c{i})" x="{x0}" y="{y}" font-family="{MONO}" font-size="{size}" '
          f'textLength="{lw:.0f}" lengthAdjust="spacingAndGlyphs" fill="{c["tag"]}">{line}</text>')
        w(f'<g class="m{i}"><rect class="k" x="{x0 + 2}" y="{y - 17}" width="11" height="22" fill="{c["road"]}"/></g>')
        w("</g>")
    w("</svg>")
    return "\n".join(out) + "\n"


def main():
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        for name, fn in (("banner", banner), ("typing", typing)):
            path = ASSETS / f"{name}-{theme}.svg"
            path.write_text(fn(theme), encoding="utf-8")
            print(f"{path.relative_to(ASSETS.parent)}  {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
