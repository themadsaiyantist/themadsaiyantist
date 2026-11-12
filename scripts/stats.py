"""Write the profile's stats cards from GitHub's GraphQL API, public repositories only.

Run with: GITHUB_TOKEN=... python3 scripts/stats.py
Reads user(login: LOGIN), never viewer, and keeps only public repositories:
the repository list asks for privacy: PUBLIC, and every contribution is
dropped unless its repository reports isPrivate: false.
Writes assets/stats-{dark,light}.svg, assets/langs-{dark,light}.svg and
assets/repo-{name}-{dark,light}.svg for each featured repository.
Stdlib only. Nothing in the cards depends on the clock beyond the month,
so a rerun on unchanged data writes byte-identical files.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

LOGIN = "themadsaiyantist"
FEATURED = ["runlog", "vectoralis-i"]
ASSETS = Path(__file__).resolve().parent.parent / "assets"
API = "https://api.github.com/graphql"

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,sans-serif"
HEAVY = "'Arial Black','Helvetica Neue',Helvetica,Arial,system-ui,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

THEMES = {
    "dark": {
        "bg0": "#1a1209", "bg1": "#0d1117", "edge": "#ff9f1c", "edge_op": ".28",
        "title": "#ffb547", "num0": "#fff1b8", "num1": "#ff8a1c",
        "text": "#e6edf3", "muted": "#8b949e", "track": "#21262d",
        "bar0": "#ff6a13", "bar1": "#ffd15c", "glow": "#ff9f1c",
    },
    "light": {
        "bg0": "#fff3df", "bg1": "#ffffff", "edge": "#e2580a", "edge_op": ".30",
        "title": "#c2410c", "num0": "#f29a00", "num1": "#c2410c",
        "text": "#1f2328", "muted": "#59636e", "track": "#f1e8dc",
        "bar0": "#e2580a", "bar1": "#f5a524", "glow": "#ff9f1c",
    },
}

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def graphql(query, token):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-stats-script"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.load(resp)
    if body.get("errors"):
        sys.exit(f"GraphQL errors: {body['errors']}")
    return body["data"]


def months_back(now, count):
    """The first instant of each of the last `count` calendar months, oldest first, plus the end."""
    y, m = now.year, now.month
    starts = []
    for _ in range(count):
        starts.append(datetime(y, m, 1, tzinfo=timezone.utc))
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    starts.reverse()
    return starts


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(token):
    now = datetime.now(timezone.utc)
    starts = months_back(now, 12)
    month_fields = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else now
        month_fields.append(
            f'm{i}: contributionsCollection(from: "{iso(start)}", to: "{iso(end)}") {{'
            f" commitContributionsByRepository(maxRepositories: 100) {{"
            f" repository {{ isPrivate }} contributions {{ totalCount }} }} }}"
        )
    featured = "\n".join(
        f'f{i}: repository(owner: "{LOGIN}", name: "{name}") {{ name isPrivate description stargazerCount '
        f"forkCount url primaryLanguage {{ name color }} }}"
        for i, name in enumerate(FEATURED)
    )
    query = f"""
    query {{
      user(login: "{LOGIN}") {{
        repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {{
          nodes {{ name isPrivate stargazerCount
            languages(first: 20, orderBy: {{field: SIZE, direction: DESC}}) {{ edges {{ size node {{ name color }} }} }} }}
        }}
        year: contributionsCollection {{
          commitContributionsByRepository(maxRepositories: 100) {{ repository {{ isPrivate }} contributions {{ totalCount }} }}
          pullRequestContributionsByRepository(maxRepositories: 100) {{ repository {{ isPrivate }} contributions {{ totalCount }} }}
        }}
        {" ".join(month_fields)}
      }}
      {featured}
    }}"""
    data = graphql(query, token)
    user = data["user"]

    def public_total(groups):
        return sum(g["contributions"]["totalCount"] for g in groups if g["repository"]["isPrivate"] is False)

    repos = [r for r in user["repositories"]["nodes"] if r["isPrivate"] is False]
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            name = e["node"]["name"]
            size, color = langs.get(name, (0, e["node"]["color"] or "#8b949e"))
            langs[name] = (size + e["size"], color)

    months = []
    for i, start in enumerate(starts):
        months.append((start.strftime("%b"), public_total(user[f"m{i}"]["commitContributionsByRepository"])))

    featured_repos = []
    for i in range(len(FEATURED)):
        r = data.get(f"f{i}")
        if r and r["isPrivate"] is False:
            featured_repos.append(r)

    return {
        "commits": public_total(user["year"]["commitContributionsByRepository"]),
        "prs": public_total(user["year"]["pullRequestContributionsByRepository"]),
        "repos": len(repos),
        "stars": sum(r["stargazerCount"] for r in repos),
        "langs": sorted(langs.items(), key=lambda kv: (-kv[1][0], kv[0])),
        "months": months,
        "featured": featured_repos,
    }


def defs(c, h):
    return (
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c["bg0"]}"/>'
        f'<stop offset=".6" stop-color="{c["bg1"]}"/></linearGradient>'
        f'<linearGradient id="num" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["num0"]}"/>'
        f'<stop offset="1" stop-color="{c["num1"]}"/></linearGradient>'
        f'<linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{c["bar0"]}"/>'
        f'<stop offset="1" stop-color="{c["bar1"]}"/></linearGradient>'
        f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["edge"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{c["edge"]}"/><stop offset="1" stop-color="{c["edge"]}" stop-opacity="0"/></linearGradient>'
        f"</defs>"
    )


def frame(c, width, h):
    return (
        f'<rect x=".5" y=".5" width="{width - 1}" height="{h - 1}" rx="12" fill="url(#bg)" '
        f'stroke="{c["edge"]}" stroke-opacity="{c["edge_op"]}"/>'
        f'<rect x="40" y=".5" width="{width - 80}" height="1.5" fill="url(#edge)"/>'
    )


def stats_card(s, theme):
    c = THEMES[theme]
    width, h = 840, 210
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" width="{width}" height="{h}" role="img" '
        f'aria-label="Public GitHub stats: {s["commits"]} commits in the last year, {s["prs"]} pull requests, '
        f'{s["repos"]} public repositories, {s["stars"]} stars">',
        "<style>@keyframes blip{0%,100%{opacity:.35}50%{opacity:1}}"
        "@keyframes hum{0%,100%{opacity:.85}50%{opacity:1}}"
        ".b{animation:hum 2.4s ease-in-out infinite}"
        ".d{animation:blip 1.6s ease-in-out infinite}" + REDUCED + "</style>",
        defs(c, h),
        frame(c, width, h),
        f'<circle class="d" cx="30" cy="31" r="4" fill="{c["glow"]}"/>',
        f'<text x="44" y="36" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="3" '
        f'fill="{c["title"]}">SCOUTER READING</text>',
        f'<text x="{width - 24}" y="36" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="2" '
        f'fill="{c["muted"]}">PUBLIC REPOSITORIES ONLY</text>',
    ]
    tiles = [
        (s["commits"], "COMMITS, LAST YEAR"),
        (s["prs"], "PULL REQUESTS, LAST YEAR"),
        (s["repos"], "PUBLIC REPOSITORIES"),
        (s["stars"], "STARS EARNED"),
    ]
    for i, (value, label) in enumerate(tiles):
        x = 30 + (i % 2) * 190
        y = 100 + (i // 2) * 76
        out.append(f'<text x="{x}" y="{y}" font-family="{HEAVY}" font-size="38" font-weight="900" '
                   f'fill="url(#num)">{value:,}</text>')
        out.append(f'<text x="{x}" y="{y + 20}" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" '
                   f'fill="{c["muted"]}">{label}</text>')

    # monthly public commits, the ki gauge
    gx, gy, gw, gh = 430, 62, 386, 112
    out.append(f'<text x="{gx}" y="{gy - 6}" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" '
               f'fill="{c["muted"]}">COMMITS PER MONTH</text>')
    top = max([n for _, n in s["months"]] + [1])
    step = gw / len(s["months"])
    bw = step * 0.62
    out.append(f'<rect x="{gx}" y="{gy + gh}" width="{gw}" height="1" fill="{c["muted"]}" opacity=".4"/>')
    for i, (label, n) in enumerate(s["months"]):
        x = gx + i * step + (step - bw) / 2
        out.append(f'<rect x="{x:.1f}" y="{gy + 6}" width="{bw:.1f}" height="{gh - 6}" rx="3" fill="{c["track"]}" opacity=".7"/>')
        if n:
            bh = max(4.0, (gh - 6) * n / top)
            out.append(f'<rect class="b" x="{x:.1f}" y="{gy + gh - bh:.1f}" '
                       f'width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="url(#bar)"/>')
            out.append(f'<text x="{x + bw / 2:.1f}" y="{gy + gh - bh - 5:.1f}" text-anchor="middle" font-family="{MONO}" '
                       f'font-size="10" fill="{c["text"]}">{n}</text>')
        out.append(f'<text x="{x + bw / 2:.1f}" y="{gy + gh + 16}" text-anchor="middle" font-family="{MONO}" '
                   f'font-size="10" fill="{c["muted"]}">{label[0]}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def langs_card(s, theme, top_n=6):
    c = THEMES[theme]
    width, h = 840, 118
    langs = s["langs"][:top_n]
    total = sum(size for _, (size, _) in s["langs"]) or 1
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" width="{width}" height="{h}" role="img" '
        f'aria-label="Top languages across public repositories: '
        + ", ".join(f"{n} {100 * sz / total:.1f} percent" for n, (sz, _) in langs) + '">',
        "<style>@keyframes sweep{0%,55%{transform:translateX(-160px)}100%{transform:translateX(900px)}}"
        ".sw{animation:sweep 4.5s ease-in-out infinite}" + REDUCED + "</style>",
        defs(c, h),
        frame(c, width, h),
        f'<text x="24" y="34" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="3" '
        f'fill="{c["title"]}">TOP LANGUAGES</text>',
        f'<text x="{width - 24}" y="34" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="2" '
        f'fill="{c["muted"]}">BY BYTES, PUBLIC REPOSITORIES</text>',
        '<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        f'<clipPath id="track"><rect x="24" y="50" width="{width - 48}" height="12" rx="6"/></clipPath>',
        f'<rect x="24" y="50" width="{width - 48}" height="12" rx="6" fill="{c["track"]}"/>',
        '<g clip-path="url(#track)"><g>',
    ]
    x = 24.0
    span = width - 48
    for name, (size, color) in langs:
        seg = span * size / total
        out.append(f'<rect x="{x:.2f}" y="50" width="{seg + 0.5:.2f}" height="12" fill="{color}"/>')
        x += seg
    out.append(f'</g><rect class="sw" x="24" y="50" width="120" height="12" fill="url(#shine)"/></g>')
    col = (width - 48) / max(len(langs), 1)
    for i, (name, (size, color)) in enumerate(langs):
        lx = 24 + i * col
        out.append(f'<circle cx="{lx + 5:.1f}" cy="88" r="5" fill="{color}"/>')
        out.append(f'<text x="{lx + 16:.1f}" y="92" font-family="{SANS}" font-size="13" font-weight="600" '
                   f'fill="{c["text"]}">{escape(name)} <tspan fill="{c["muted"]}" font-weight="400">'
                   f'{100 * size / total:.1f}%</tspan></text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def wrap(text, limit):
    words, lines, line = text.split(), [], ""
    for word in words:
        if len(line) + len(word) + (1 if line else 0) > limit:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        lines.append(line)
    if len(lines) > 3:
        lines = lines[:3]
        lines[2] = lines[2].rstrip(".,") + "..."
    return lines


REPO_ICON = ("M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7"
             ".75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1"
             " .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z")
STAR_ICON = ("M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791"
             "L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z")


def repo_card(r, theme):
    c = THEMES[theme]
    width, h = 410, 150
    lines = wrap(r["description"] or "", 52)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" width="{width}" height="{h}" role="img" '
        f'aria-label="{escape(LOGIN)}/{escape(r["name"])}: {escape(r["description"] or "")}">',
        defs(c, h),
        frame(c, width, h),
        f'<path transform="translate(22 20)" fill="{c["muted"]}" d="{REPO_ICON}"/>',
        f'<text x="46" y="33" font-family="{SANS}" font-size="17" font-weight="700" fill="{c["title"]}">{escape(r["name"])}</text>',
        f'<text x="{width - 22}" y="33" text-anchor="end" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" '
        f'fill="{c["muted"]}">PUBLIC</text>',
    ]
    for i, line in enumerate(lines):
        out.append(f'<text x="22" y="{62 + i * 20}" font-family="{SANS}" font-size="13.5" fill="{c["text"]}">{escape(line)}</text>')
    x = 22
    lang = r.get("primaryLanguage")
    if lang:
        out.append(f'<circle cx="{x + 6}" cy="{h - 25}" r="6" fill="{lang["color"] or c["muted"]}"/>')
        out.append(f'<text x="{x + 18}" y="{h - 20}" font-family="{SANS}" font-size="12.5" fill="{c["muted"]}">{escape(lang["name"])}</text>')
        x += 30 + 8 * len(lang["name"])
    out.append(f'<path transform="translate({x} {h - 33})" fill="{c["muted"]}" d="{STAR_ICON}"/>')
    out.append(f'<text x="{x + 21}" y="{h - 20}" font-family="{SANS}" font-size="12.5" fill="{c["muted"]}">{r["stargazerCount"]:,}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    s = fetch(token)
    ASSETS.mkdir(exist_ok=True)
    written = []
    for theme in THEMES:
        files = {f"stats-{theme}.svg": stats_card(s, theme), f"langs-{theme}.svg": langs_card(s, theme)}
        for r in s["featured"]:
            files[f"repo-{r['name']}-{theme}.svg"] = repo_card(r, theme)
        for name, svg in files.items():
            (ASSETS / name).write_text(svg, encoding="utf-8")
            written.append(name)
    print(f"commits {s['commits']}, pull requests {s['prs']}, public repositories {s['repos']}, stars {s['stars']}")
    print("languages " + ", ".join(f"{n} {sz}" for n, (sz, _) in s["langs"]))
    print("months " + ", ".join(f"{m} {n}" for m, n in s["months"]))
    print("featured " + ", ".join(r["name"] for r in s["featured"]))
    print("wrote " + ", ".join(sorted(written)))


if __name__ == "__main__":
    main()
