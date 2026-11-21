"""Draws assets for the `output` branch: a "telemetry" stats card in the night-sky style.

Runs in GitHub Actions (see .github/workflows/sky.yml) with the workflow's own
GITHUB_TOKEN, so no third-party stats server is involved and nothing can be
rate-limited at view time. If the API call fails, it still writes a card
saying telemetry is offline, so the README never shows a broken image.

    GITHUB_TOKEN=... python3 scripts/telemetry.py <login> <out.svg>
    python3 scripts/telemetry.py <login> <out.svg> --sample   # offline preview
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request

from skylib import (
    AMBER, AMBER_TEXT, DEEP, INK, INK_SOFT, LINE, MINT, MUTED, PANEL, ROUTE, ROUTE_TEXT,
    SIGNAL, VIOLET, esc, pixel_chip, pixel_frame, pixel_star, starfield, svg_doc, text_width,
)

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100, after: $cursor) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

# Languages that describe tooling rather than what the code is written in.
SKIP_LANGS = {"Dockerfile", "Makefile", "Procfile", "Batchfile", "PowerShell", "Smarty", "Mustache"}
LANG_COLORS = [AMBER, ROUTE_TEXT, MINT, "#ff7ab8", "#b892ff", "#5ec8ff", "#8a90b8"]


def fetch(login: str, token: str) -> dict:
    repos, cursor, user = [], None, None
    while True:
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": QUERY, "variables": {"login": login, "cursor": cursor}}).encode(),
            headers={"Authorization": f"bearer {token}", "User-Agent": "profile-telemetry"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = json.load(r)
        if payload.get("errors"):
            raise RuntimeError(payload["errors"])
        user = payload["data"]["user"]
        page = user["repositories"]
        repos += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    user["repositories"]["nodes"] = repos
    return user


def summarize(user: dict, today: dt.date) -> dict:
    repos = user["repositories"]["nodes"]
    langs: dict[str, int] = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            if n not in SKIP_LANGS:
                langs[n] = langs.get(n, 0) + e["size"]
    cc = user["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    days = [d for d in days if dt.date.fromisoformat(d["date"]) <= today]

    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            current += 1
        elif i == 0:
            continue  # today may simply not have a contribution yet
        else:
            break
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    busiest = max(days, key=lambda d: d["contributionCount"]) if days else None
    active = sum(1 for d in days if d["contributionCount"] > 0)

    return {
        "stars": sum(r["stargazerCount"] for r in repos),
        "repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "prs": user["pullRequests"]["totalCount"],
        "issues": user["issues"]["totalCount"],
        "contrib": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "current": current,
        "longest": longest,
        "active": active,
        "busiest": busiest,
        "langs": sorted(langs.items(), key=lambda kv: -kv[1]),
        "spark": [d["contributionCount"] for d in days[-56:]],
    }


def tile(x, y, w, h, value, label, acc, delay):
    return (
        f'<g class="rise" style="animation-delay:{delay:.2f}s">'
        f'<path d="{pixel_chip(x, y, w, h, 6)}" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>'
        f'<rect x="{x + 6}" y="{y}" width="{w - 12}" height="3" fill="{acc}"/>'
        f'<text x="{x + 20}" y="{y + 62}" font-size="52" fill="{INK}">{esc(str(value))}</text>'
        f'<text x="{x + 20}" y="{y + h - 18}" font-size="21" fill="{acc}">{esc(label)}</text></g>'
    )


def render(s: dict | None, login: str, now: dt.datetime) -> str:
    W, H = 1200, 530
    parts = []
    if s is None:
        parts.append(
            f'<text x="{W / 2}" y="250" font-size="40" fill="{INK_SOFT}" text-anchor="middle">telemetry offline</text>'
            f'<text x="{W / 2}" y="290" font-size="22" fill="{MUTED}" text-anchor="middle">the next scheduled run will try again</text>'
        )
        desc = "Telemetry is temporarily unavailable."
    else:
        tiles = [
            (f"{s['contrib']:,}", "contributions (1y)", AMBER),
            (f"{s['current']}d", "current streak", SIGNAL),
            (f"{s['longest']}d", "longest streak", MINT),
            (f"{s['commits']:,}", "commits (1y)", ROUTE_TEXT),
            (s["repos"], "public repositories", "#b892ff"),
            (s["prs"], "pull requests", "#5ec8ff"),
            (s["stars"], "stars earned", AMBER_TEXT),
            (f"{s['active']}", "active days (1y)", "#ff7ab8"),
        ]
        tw, th, gx, gy = 168, 112, 12, 12
        for i, (v, lab, acc) in enumerate(tiles):
            r, c = divmod(i, 4)
            parts.append(tile(40 + c * (tw + gx), 84 + r * (th + gy), tw, th, v, lab, acc, .1 + i * .06))

        # languages: segmented pixel bar plus legend
        lx, lw = 790, 370
        total = sum(v for _, v in s["langs"]) or 1
        top = s["langs"][:6]
        rest = total - sum(v for _, v in top)
        if rest > 0:
            top.append(("Other", rest))
        parts.append(f'<text x="{lx}" y="104" font-size="26" fill="{INK}">Languages by code size</text>')
        bar_y, seg_x = 124, lx
        bar = []
        for i, (name, v) in enumerate(top):
            w = max(4, round(lw * v / total / 4) * 4)
            w = min(w, lx + lw - seg_x)
            bar.append(f'<rect x="{seg_x}" y="{bar_y}" width="{w}" height="20" fill="{LANG_COLORS[i]}"/>')
            seg_x += w
        parts.append(
            f'<rect x="{lx}" y="{bar_y}" width="{lw}" height="20" fill="{PANEL}"/>'
            f'<g class="fill">{"".join(bar)}</g>'
        )
        for i, (name, v) in enumerate(top):
            y = 182 + i * 30
            pct = 100 * v / total
            parts.append(
                f'<g class="rise" style="animation-delay:{.5 + i * .07:.2f}s">'
                f'<rect x="{lx}" y="{y - 13}" width="12" height="12" fill="{LANG_COLORS[i]}"/>'
                f'<text x="{lx + 22}" y="{y}" font-size="22" fill="{INK_SOFT}">{esc(name)}</text>'
                f'<text x="{lx + lw}" y="{y}" font-size="22" fill="{MUTED}" text-anchor="end">{pct:.1f}%</text></g>'
            )

        # last 8 weeks as a pixel skyline
        spark = s["spark"]
        peak = max(spark) or 1
        sx, sy, cw = 40, 498, 1120 / max(1, len(spark))
        cells = []
        for i, v in enumerate(spark):
            h = 0 if v == 0 else 4 + round(56 * v / peak / 4) * 4
            col = AMBER if v == peak and v else (ROUTE if v else LINE)
            hh = h or 4
            cells.append(f'<rect x="{sx + i * cw:.1f}" y="{sy - hh}" width="{cw - 4:.1f}" height="{hh}" fill="{col}" '
                         f'class="bar" style="animation-delay:{.6 + i * .012:.3f}s"/>')
        parts.append(f'<text x="40" y="{sy - 72}" font-size="22" fill="{MUTED}">last 8 weeks</text>'
                     f'<g shape-rendering="crispEdges">{"".join(cells)}</g>')
        if s["busiest"] and s["busiest"]["contributionCount"]:
            b = s["busiest"]
            parts.append(f'<text x="{W - 40}" y="{sy - 72}" font-size="22" fill="{MUTED}" text-anchor="end">'
                         f'busiest day: {b["contributionCount"]} on {b["date"]}</text>')
        desc = (f"{s['contrib']} contributions in the last 12 months, current streak {s['current']} days, "
                f"longest {s['longest']} days, {s['repos']} public repositories, {s['stars']} stars. "
                f"Top languages: {', '.join(n for n, _ in top[:5])}.")

    stamp = (now + dt.timedelta(hours=7)).strftime("%d %b %Y, %H:%M WIB")
    body = f"""
<defs><clipPath id="frame"><path d="{pixel_frame(W, H)}"/></clipPath>
<radialGradient id="nb" cx="1" cy="0" r=".7"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".22"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient></defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="{DEEP}"/><rect width="{W}" height="{H}" fill="url(#nb)"/>
{starfield(404, W, H, 50, sparkle_every=12, opacity=.5)}
{pixel_star(46, 42, 3, SIGNAL)}
<text x="66" y="52" font-size="34" fill="{INK}">Telemetry</text>
<text x="{66 + text_width('Telemetry', 34) + 14}" y="52" font-size="22" fill="{MUTED}">@{esc(login)}</text>
<rect class="blink" x="{W - 40 - text_width('updated ' + stamp, 20) - 20}" y="38" width="8" height="8" fill="{SIGNAL}"/>
<text x="{W - 40}" y="48" font-size="20" fill="{MUTED}" text-anchor="end">updated {stamp}</text>
{''.join(parts)}
</g>
<path d="{pixel_frame(W, H)}" fill="none" stroke="{LINE}" stroke-width="2"/>
"""
    css = (".fill{animation:fill 1.4s steps(25) both .4s;transform-box:fill-box;transform-origin:left}"
           "@keyframes fill{from{transform:scaleX(0)}}"
           ".bar{animation:bar .6s steps(5) both;transform-box:fill-box;transform-origin:bottom}"
           "@keyframes bar{from{transform:scaleY(0)}}")
    return svg_doc(W, H, f"GitHub telemetry for @{login}", desc, css, body)


def sample() -> dict:
    import random
    rnd = random.Random(3)
    start = dt.date.today() - dt.timedelta(days=364)
    days = [{"date": (start + dt.timedelta(days=i)).isoformat(),
             "contributionCount": 0 if i < 200 or rnd.random() < .25 else rnd.randint(1, 18)} for i in range(365)]
    weeks = [{"contributionDays": days[i:i + 7]} for i in range(0, 365, 7)]
    langs = [("TypeScript", 900000), ("Java", 640000), ("Go", 520000), ("JavaScript", 300000),
             ("CSS", 90000), ("Python", 40000), ("Shell", 20000), ("Dockerfile", 5000)]
    return {
        "createdAt": "2024-01-01T00:00:00Z", "followers": {"totalCount": 12},
        "pullRequests": {"totalCount": 64}, "issues": {"totalCount": 9},
        "repositories": {"totalCount": 18, "nodes": [{"stargazerCount": 3, "languages": {"edges": [
            {"size": v, "node": {"name": n}} for n, v in langs]}}]},
        "contributionsCollection": {"totalCommitContributions": 1234, "restrictedContributionsCount": 0,
                                    "contributionCalendar": {"totalContributions": 1580, "weeks": weeks}},
    }


def main() -> None:
    login, out = sys.argv[1], sys.argv[2]
    now = dt.datetime.now(dt.timezone.utc)
    try:
        user = sample() if "--sample" in sys.argv else fetch(login, os.environ["GITHUB_TOKEN"])
        stats = summarize(user, now.date())
    except Exception as exc:  # keep the README image alive whatever happens
        print(f"telemetry: falling back to offline card ({exc})", file=sys.stderr)
        stats = None
    with open(out, "w") as f:
        f.write(render(stats, login, now))
    print(f"telemetry: wrote {out}")


if __name__ == "__main__":
    main()
