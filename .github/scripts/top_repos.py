
import json
import os
import urllib.request
import html
from datetime import datetime, timezone

USERNAME = "Sreyank-Bose-Git"
TOKEN = os.environ["GITHUB_TOKEN"]

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      commitContributionsByRepository(maxRepositories: 100) {
        repository {
          nameWithOwner
          url
        }
        contributions {
          totalCount
        }
      }
    }
  }
}
"""

payload = {
    "query": QUERY,
    "variables": {
        "login": USERNAME,
        "from": "2008-01-01T00:00:00Z",
        "to": datetime.now(timezone.utc).isoformat()
    }
}

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": USERNAME
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())

if "errors" in result:
    raise RuntimeError(result["errors"])

user = result["data"]["user"]

if user is None:
    raise RuntimeError("GitHub user not found.")

repositories = user["contributionsCollection"]["commitContributionsByRepository"]

repositories = sorted(
    repositories,
    key=lambda item: item["contributions"]["totalCount"],
    reverse=True
)[:5]

WIDTH = 900
HEIGHT = 115 + max(1, len(repositories)) * 65

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
    '<defs>',
    '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">',
    '<stop offset="0%" stop-color="#050816"/>',
    '<stop offset="100%" stop-color="#17123B"/>',
    '</linearGradient>',
    '<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">',
    '<stop offset="0%" stop-color="#6D28D9"/>',
    '<stop offset="100%" stop-color="#00D4FF"/>',
    '</linearGradient>',
    '</defs>',
    f'<rect width="{WIDTH}" height="{HEIGHT}" rx="18" fill="url(#bg)"/>',
    '<text x="35" y="45" fill="#00D4FF" font-size="23" font-weight="bold" font-family="Arial">TOP CONTRIBUTED REPOSITORIES</text>',
    '<text x="35" y="72" fill="#A5B4FC" font-size="12" font-family="Arial">Ranked by GitHub commit contribution days</text>'
]

max_count = max(
    (item["contributions"]["totalCount"] for item in repositories),
    default=1
)

if not repositories:
    svg.append(
        '<text x="35" y="140" fill="#FFFFFF" font-size="16" font-family="Arial">'
        'No public contribution data available.</text>'
    )

for index, item in enumerate(repositories):
    y = 115 + index * 65

    name = html.escape(item["repository"]["nameWithOwner"])
    url = html.escape(item["repository"]["url"], quote=True)
    count = item["contributions"]["totalCount"]

    bar_width = max(5, int(550 * count / max_count))

    svg.extend([
        f'<a href="{url}">',
        f'<text x="35" y="{y}" fill="#FFFFFF" font-size="15" font-weight="bold" font-family="Arial">{index + 1}. {name}</text>',
        '</a>',
        f'<rect x="35" y="{y + 12}" width="550" height="12" rx="6" fill="#252747"/>',
        f'<rect x="35" y="{y + 12}" width="{bar_width}" height="12" rx="6" fill="url(#bar)"/>',
        f'<text x="610" y="{y + 23}" fill="#00D4FF" font-size="14" font-weight="bold" font-family="Arial">{count} days</text>'
    ])

svg.append("</svg>")

os.makedirs("dist", exist_ok=True)

with open("dist/top-contributed-repos.svg", "w", encoding="utf-8") as file:
    file.write("\n".join(svg))

print("Successfully generated top-contributed-repos.svg")
