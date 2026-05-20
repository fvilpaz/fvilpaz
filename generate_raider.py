import os
import requests
from datetime import datetime, timezone, timedelta

USERNAME = os.environ.get("GITHUB_USERNAME", "fvilpaz")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

CELL = 12
GAP = 3
STEP = CELL + GAP  # 15px per cell
PADDING_X = 30
PADDING_Y = 40
SCAN_COLS = 3       # width of scanner in columns
DURATION = "3.5s"


def fetch_contributions():
    now = datetime.now(timezone.utc)
    one_year_ago = now - timedelta(weeks=52)

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
                weekday
              }
            }
          }
        }
      }
    }
    """
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {
            "login": USERNAME,
            "from": one_year_ago.isoformat(),
            "to": now.isoformat(),
        }},
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def base_color(count):
    if count == 0:  return "#1c1c2a"
    if count <= 3:  return "#2a3448"
    if count <= 6:  return "#344060"
    if count <= 9:  return "#3e4e78"
    return "#485a90"


def lit_color(count):
    # Squares light up red as the scanner passes
    if count == 0:  return "#2a0000"
    if count <= 3:  return "#5a0000"
    if count <= 6:  return "#880000"
    if count <= 9:  return "#aa1100"
    return "#cc2200"


def generate_svg(weeks):
    n_weeks = len(weeks)
    grid_w = n_weeks * STEP - GAP
    grid_h = 7 * STEP - GAP
    total_w = PADDING_X * 2 + grid_w
    total_h = PADDING_Y + 20 + grid_h + 20  # top label + grid + bottom padding

    label_y = PADDING_Y - 8
    grid_y = PADDING_Y + 10

    scan_w = SCAN_COLS * STEP - GAP
    scan_x_start = PADDING_X
    scan_x_end = PADDING_X + grid_w - scan_w

    lines = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_w}" height="{total_h}" '
        f'viewBox="0 0 {total_w} {total_h}">'
    )

    # ── Defs ──────────────────────────────────────────────
    lines.append("  <defs>")

    # Glow filter for the scanner bar
    lines.append("""    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>""")

    # Clip path that moves with the scanner — reveals the lit grid
    lines.append(f'    <clipPath id="scan-clip">')
    lines.append(
        f'      <rect x="{scan_x_start}" y="{grid_y}" '
        f'width="{scan_w}" height="{grid_h}">'
    )
    lines.append(
        f'        <animate attributeName="x" '
        f'values="{scan_x_start};{scan_x_end};{scan_x_start}" '
        f'dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/>'
    )
    lines.append("      </rect>")
    lines.append("    </clipPath>")
    lines.append("  </defs>")

    # ── Background ────────────────────────────────────────
    lines.append(
        f'  <rect width="{total_w}" height="{total_h}" fill="#0a0a0f" rx="10"/>'
    )

    # ── Label ─────────────────────────────────────────────
    lines.append(
        f'  <text x="{PADDING_X}" y="{label_y}" '
        f'font-family="JetBrains Mono,Courier New,monospace" '
        f'font-size="9" fill="#333" letter-spacing="3">COMMIT RAIDER // {USERNAME}</text>'
    )

    # ── Base grid (always visible, dark colors) ───────────
    lines.append('  <g id="base">')
    for w_i, week in enumerate(weeks):
        for day in week["contributionDays"]:
            x = PADDING_X + w_i * STEP
            y = grid_y + day["weekday"] * STEP
            color = base_color(day["contributionCount"])
            lines.append(
                f'    <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'fill="{color}" rx="2"/>'
            )
    lines.append("  </g>")

    # ── Lit grid (clipped to scanner — squares glow red as it passes) ─
    lines.append('  <g id="lit" clip-path="url(#scan-clip)">')
    for w_i, week in enumerate(weeks):
        for day in week["contributionDays"]:
            x = PADDING_X + w_i * STEP
            y = grid_y + day["weekday"] * STEP
            color = lit_color(day["contributionCount"])
            lines.append(
                f'    <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'fill="{color}" rx="2"/>'
            )
    lines.append("  </g>")

    # ── Scanner bar (red glow on top) ─────────────────────
    lines.append(
        f'  <rect x="{scan_x_start}" y="{grid_y}" '
        f'width="{scan_w}" height="{grid_h}" '
        f'fill="#ff1a00" opacity="0.18" rx="2" filter="url(#glow)">'
    )
    lines.append(
        f'    <animate attributeName="x" '
        f'values="{scan_x_start};{scan_x_end};{scan_x_start}" '
        f'dur="{DURATION}" repeatCount="indefinite" calcMode="linear"/>'
    )
    lines.append("  </rect>")

    lines.append("</svg>")
    return "\n".join(lines)


def main():
    print(f"Fetching contributions for {USERNAME}...")
    weeks = fetch_contributions()
    print(f"Got {len(weeks)} weeks of data.")
    svg = generate_svg(weeks)
    os.makedirs("assets", exist_ok=True)
    with open("assets/commit-raider.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Saved assets/commit-raider.svg")


if __name__ == "__main__":
    main()
