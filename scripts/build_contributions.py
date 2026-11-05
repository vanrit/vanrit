#!/usr/bin/env python3
"""Render the GitHub contribution calendar into a repository-owned SVG.

Uses only Python's standard library. The workflow provides GITHUB_TOKEN.
The calendar SVG is intentionally static: GitHub README does not run CSS/JS.
"""
import json
import os
from datetime import date
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'contributions.svg'
USER = os.environ.get('GH_USER', 'vanrit')
TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')

QUERY = '''query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}'''

COLORS = ['#1d2840', '#155e75', '#0891b2', '#818cf8', '#c084fc']
LEVELS = {
    'NONE': 0,
    'FIRST_QUARTILE': 1,
    'SECOND_QUARTILE': 2,
    'THIRD_QUARTILE': 3,
    'FOURTH_QUARTILE': 4,
}


def fetch():
    if not TOKEN:
        raise RuntimeError('GH_TOKEN / GITHUB_TOKEN is required')
    payload = json.dumps({'query': QUERY, 'variables': {'login': USER}}).encode('utf-8')
    req = Request(
        'https://api.github.com/graphql', data=payload,
        headers={
            'Authorization': 'Bearer ' + TOKEN,
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json',
            'User-Agent': 'vanrit-profile-calendar',
        },
    )
    with urlopen(req, timeout=25) as response:
        data = json.load(response)
    if data.get('errors'):
        raise RuntimeError('GitHub GraphQL returned: ' + json.dumps(data['errors']))
    try:
        return data['data']['user']['contributionsCollection']['contributionCalendar']
    except (KeyError, TypeError) as exc:
        raise RuntimeError('No contribution calendar in GraphQL response') from exc


def make_svg(calendar):
    weeks = calendar['weeks']
    step, cell = 14, 10
    margin_x, top = 45, 93
    w = max(840, margin_x + len(weeks) * step + 45)
    height = 256
    def text(x, y, content, size=12, color='#9aa9c3', extra=''):
        return f'<text x="{x}" y="{y}" fill="{color}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="{size}" {extra}>{escape(str(content))}</text>'

    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{height}" viewBox="0 0 {w} {height}" role="img" aria-label="Contribution calendar for {escape(USER)}; {calendar['totalContributions']} contributions in the past year">
<defs>
  <linearGradient id="background" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#101c34"/><stop offset="0.57" stop-color="#171b35"/><stop offset="1" stop-color="#21162c"/></linearGradient>
  <linearGradient id="edge" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#80eaff" stop-opacity=".48"/><stop offset=".52" stop-color="#a7a7ff" stop-opacity=".18"/><stop offset="1" stop-color="#ffa1d2" stop-opacity=".4"/></linearGradient>
  <radialGradient id="glow"><stop stop-color="#818cf8" stop-opacity=".17"/><stop offset="1" stop-color="#818cf8" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{w}" height="{height}" rx="22" fill="url(#background)"/>
<circle cx="{w-80}" cy="34" r="220" fill="url(#glow)"/>
<rect x="1" y="1" width="{w-2}" height="{height-2}" rx="21" fill="none" stroke="url(#edge)" stroke-width="2"/>
<path d="M24 63H{w-24}" stroke="#ffffff" stroke-opacity=".10"/>
''']
    parts.append(text(28, 36, 'CONTRIBUTIONS', 17, '#e4edf9', 'font-weight="700" letter-spacing="1"'))
    parts.append(text(w-28, 36, f"{calendar['totalContributions']:,} in the last year", 13, '#a5d9e9', 'text-anchor="end"'))
    for d, y in [('Mon', 113), ('Wed', 141), ('Fri', 169)]:
        parts.append(text(14, y, d, 10, '#8a9bb8'))

    last_month = None
    for i, week in enumerate(weeks):
        days = week['contributionDays']
        if days:
            month = date.fromisoformat(days[0]['date']).strftime('%b')
            if month != last_month and (i == 0 or i > 1):
                parts.append(text(margin_x+i*step, 80, month, 11, '#acb9d0'))
                last_month = month
        for day in days:
            wd = date.fromisoformat(day['date']).weekday()
            # github grids run Sun -> Sat. weekday Monday=0; Sun should be top.
            row = (wd + 1) % 7
            x, y = margin_x + i * step, top + row * step
            level = LEVELS.get(day['contributionLevel'], 0)
            color = COLORS[level]
            title = escape(f"{day['date']}: {day['contributionCount']} contributions")
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{color}"><title>{title}</title></rect>')
    legend_y = 223
    parts.append(text(28, legend_y+8, 'less', 11, '#92a4bd'))
    for i, c in enumerate(COLORS):
        parts.append(f'<rect x="{65+i*17}" y="{legend_y}" width="11" height="11" rx="2" fill="{c}"/>')
    parts.append(text(155, legend_y+8, 'more', 11, '#92a4bd'))
    parts.append(text(w-28, legend_y+8, 'github.com/' + USER, 11, '#92a4bd', 'text-anchor="end"'))
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


def main():
    calendar = fetch()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(make_svg(calendar), encoding='utf-8')
    print('Updated', OUT, 'with', calendar['totalContributions'], 'contributions')


if __name__ == '__main__':
    main()
