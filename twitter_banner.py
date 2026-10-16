import random
import math
import cairosvg

# X/Twitter recommended header size.
W, H = 1500, 500
SEED = 111
random.seed(SEED)

# --- Design parameters -----------------------------------------------
#
# Keep the interesting material away from the extreme top/bottom edges,
# since X may crop the banner somewhat depending on viewport.
#
# The profile avatar overlaps the lower-left portion of the header, so
# leave that region relatively quiet. This doesn't need to be exact.
PROFILE_EXCLUDE_CENTER = (175, 465)
PROFILE_EXCLUDE_RADIUS = 135

TEAL = "#3a9b8f"
COPPER = "#b87333"
OFFWHITE = "#e8e8e6"


def in_exclusion_zone(x, y):
    cx, cy = PROFILE_EXCLUDE_CENTER
    return math.hypot(x - cx, y - cy) < PROFILE_EXCLUDE_RADIUS


def sample_x():
    """
    Exponential-ish falloff from left to right.

    Produces x in roughly [60, 1110], with much greater density
    toward the left side.
    """
    u = random.random()
    span = 1050
    scale = 450

    x = -scale * math.log(
        1 - u * (1 - math.exp(-span / scale))
    )

    return 60 + x


def generate_nodes(n=42, min_dist=42):
    nodes = []
    attempts = 0

    while len(nodes) < n and attempts < 4000:
        attempts += 1

        x = sample_x()

        # Keep the field concentrated on the left ~2/3.
        if x > 1030:
            continue

        # A little vertical breathing room.
        y = random.uniform(40, H - 40)

        if in_exclusion_zone(x, y):
            continue

        if any(
            math.hypot(x - nx, y - ny) < min_dist
            for nx, ny, *_ in nodes
        ):
            continue

        # Nodes get smaller/fainter toward the right.
        depth = max(0.0, 1 - x / 1050)

        r = 2.5 + depth * 3.5 + random.uniform(-0.5, 0.5)

        opacity = (
            0.35
            + depth * 0.55
            + random.uniform(-0.05, 0.05)
        )
        opacity = min(0.95, max(0.25, opacity))

        nodes.append((x, y, r, opacity))

    return nodes


nodes = generate_nodes()

# --- Accent nodes ----------------------------------------------------

TEAL_COUNT = 12
SPLIT_PAIR_COUNT = 8

accent_idx = set(
    random.sample(range(len(nodes)), TEAL_COUNT)
)

# Connect a few nearby field nodes before adding copper companions.
edges = []

for i, (x1, y1, *_) in enumerate(nodes):
    for j in range(i + 1, len(nodes)):
        x2, y2, *_ = nodes[j]

        d = math.hypot(x1 - x2, y1 - y2)

        if d < 70:
            edges.append((i, j, d))

edges.sort(key=lambda e: e[2])
edges = edges[:10]


# Add disconnected copper companions near some teal nodes.
split_pair_src = random.sample(
    sorted(accent_idx),
    min(SPLIT_PAIR_COUNT, len(accent_idx)),
)

copper_idx = set()

for src_idx in split_pair_src:
    sx, sy, sr, sop = nodes[src_idx]

    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(16, 26)

    cx = sx + dist * math.cos(angle)
    cy = sy + dist * math.sin(angle)

    # Keep companion comfortably inside canvas.
    cx = min(max(cx, 12), W - 12)
    cy = min(max(cy, 12), H - 12)

    if in_exclusion_zone(cx, cy):
        continue

    nodes.append((
        cx,
        cy,
        sr * 0.85,
        min(0.95, sop + 0.05),
    ))

    copper_idx.add(len(nodes) - 1)


# --- Logo ------------------------------------------------------------

# Keep the logo comfortably inside the crop-safe middle of the banner.
logo_center = (1270, 250)
logo_R = 58
logo_node_r = 11


def polar(cx, cy, r, deg):
    rad = math.radians(deg)
    return (
        cx + r * math.cos(rad),
        cy + r * math.sin(rad),
    )


logo = {
    "teal": polar(*logo_center, logo_R, -45),
    "bottom": polar(*logo_center, logo_R, 75),
    "left": polar(*logo_center, logo_R, 195),
}

logo = {
    key: (x, y, logo_node_r)
    for key, (x, y) in logo.items()
}


# --- Build SVG -------------------------------------------------------

svg_parts = []

svg_parts.append(
    f'<svg viewBox="0 0 {W} {H}" '
    f'width="{W}" height="{H}" '
    'xmlns="http://www.w3.org/2000/svg">'
)

svg_parts.append(
    """
<defs>
  <linearGradient id="bgGrad"
                  x1="0%" y1="0%"
                  x2="100%" y2="100%">
    <stop offset="0%" stop-color="#12312c"/>
    <stop offset="55%" stop-color="#0a1a18"/>
    <stop offset="100%" stop-color="#060707"/>
  </linearGradient>

  <filter id="softGlow"
          x="-100%" y="-100%"
          width="300%" height="300%">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>
"""
)

svg_parts.append(
    f'<rect x="0" y="0" width="{W}" height="{H}" '
    'fill="url(#bgGrad)"/>'
)


# --- Field edges -----------------------------------------------------

svg_parts.append(
    f'<g stroke="{TEAL}" '
    'stroke-width="1.2" '
    'stroke-opacity="0.45">'
)

for i, j, _ in edges:
    x1, y1, *_ = nodes[i]
    x2, y2, *_ = nodes[j]

    svg_parts.append(
        f'<line '
        f'x1="{x1:.1f}" y1="{y1:.1f}" '
        f'x2="{x2:.1f}" y2="{y2:.1f}"/>'
    )

svg_parts.append("</g>")


# --- Field nodes -----------------------------------------------------

svg_parts.append("<g>")

for idx, (x, y, r, op) in enumerate(nodes):
    if idx in accent_idx:
        color = TEAL
    elif idx in copper_idx:
        color = COPPER
    else:
        color = OFFWHITE

    svg_parts.append(
        f'<circle '
        f'cx="{x:.1f}" cy="{y:.1f}" '
        f'r="{r:.1f}" '
        f'fill="{color}" '
        f'fill-opacity="{op:.2f}"/>'
    )

svg_parts.append("</g>")


# --- Logo ------------------------------------------------------------

lt = logo["teal"]
ll = logo["left"]
lb = logo["bottom"]

svg_parts.append('<g filter="url(#softGlow)">')

svg_parts.append(
    f'<line '
    f'x1="{ll[0]:.1f}" y1="{ll[1]:.1f}" '
    f'x2="{lt[0]:.1f}" y2="{lt[1]:.1f}" '
    f'stroke="{TEAL}" stroke-width="3"/>'
)

svg_parts.append(
    f'<line '
    f'x1="{ll[0]:.1f}" y1="{ll[1]:.1f}" '
    f'x2="{lb[0]:.1f}" y2="{lb[1]:.1f}" '
    f'stroke="{TEAL}" stroke-width="3"/>'
)

svg_parts.append(
    f'<line '
    f'x1="{lt[0]:.1f}" y1="{lt[1]:.1f}" '
    f'x2="{lb[0]:.1f}" y2="{lb[1]:.1f}" '
    f'stroke="{TEAL}" stroke-width="3"/>'
)

svg_parts.append(
    f'<circle cx="{lt[0]:.1f}" cy="{lt[1]:.1f}" '
    f'r="{lt[2]}" fill="{TEAL}"/>'
)

svg_parts.append(
    f'<circle cx="{ll[0]:.1f}" cy="{ll[1]:.1f}" '
    f'r="{ll[2]}" fill="{OFFWHITE}"/>'
)

svg_parts.append(
    f'<circle cx="{lb[0]:.1f}" cy="{lb[1]:.1f}" '
    f'r="{lb[2]}" fill="{OFFWHITE}"/>'
)

svg_parts.append("</g>")
svg_parts.append("</svg>")


# --- Output ----------------------------------------------------------

svg = "\n".join(svg_parts)

# Keep the SVG too; handy while iterating.
svg_filename = f"banner-{SEED}.svg"
png_filename = f"banner-{SEED}.png"

with open(svg_filename, "w", encoding="utf-8") as f:
    f.write(svg)

cairosvg.svg2png(
    bytestring=svg.encode("utf-8"),
    write_to=png_filename,
    output_width=W,
    output_height=H,
)

print(
    f"Generated {png_filename}: "
    f"{len(nodes)} nodes, "
    f"{len(edges)} edges, "
    f"{len(accent_idx)} teal accents, "
    f"{len(copper_idx)} copper accents."
)
