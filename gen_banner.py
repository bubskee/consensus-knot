import random, math

W, H = 1584, 396
random.seed(111)

# --- Design parameters -----------------------------------------------
# Node field occupies the left ~65% of the canvas (x: 60-1050), leaving
# clear space on the right for the logo motif and for LinkedIn's name/
# headline text overlay (which sits roughly x:260-950, y:300-380).
#
# LinkedIn's circular profile photo overlaps the bottom-left corner of
# the banner on desktop (~center x:170, y:420, radius ~190 relative to
# this canvas). We exclude that zone so the busiest nodes aren't hidden
# behind the photo.
PROFILE_EXCLUDE_CENTER = (170, 420)
PROFILE_EXCLUDE_RADIUS = 190

TEAL = "#3a9b8f"
COPPER = "#b87333"
OFFWHITE = "#e8e8e6"

def in_exclusion_zone(x, y):
    cx, cy = PROFILE_EXCLUDE_CENTER
    return math.hypot(x - cx, y - cy) < PROFILE_EXCLUDE_RADIUS

def sample_x():
    # Exponential decay so node density falls off toward the right,
    # matching the "becoming sparser toward the logo" brief.
    u = random.random()
    x = -450 * math.log(1 - u * (1 - math.exp(-1050/450)))
    return 60 + x

def generate_nodes(n=42, min_dist=42):
    nodes = []
    attempts = 0
    while len(nodes) < n and attempts < 4000:
        attempts += 1
        x = sample_x()
        if x > 1030:
            continue
        y = random.uniform(30, H - 30)
        if in_exclusion_zone(x, y):
            continue
        # keep the text band (where name/headline overlay sits) a bit
        # emptier so the field doesn't compete with LinkedIn's UI text
        if 260 < x < 950 and y > 300 and random.random() < 0.7:
            continue
        if any(math.hypot(x - nx, y - ny) < min_dist for nx, ny, *_ in nodes):
            continue
        # depth cue: nodes further right / more sparse are drawn smaller
        # and fainter, reinforcing the "dissolving toward the logo" read
        depth = max(0.0, 1 - x / 1050)
        r = 2.5 + depth * 3.5 + random.uniform(-0.5, 0.5)
        opacity = 0.35 + depth * 0.55 + random.uniform(-0.05, 0.05)
        opacity = min(0.95, max(0.25, opacity))
        nodes.append((x, y, r, opacity))
    return nodes

nodes = generate_nodes()

# Accent scheme: "split-brain" pairs, echoing two nodes in a distributed
# log disagreeing about leadership while sitting right next to each
# other. A handful of field nodes are colored teal (5-10 range); most of
# them get a small copper companion spawned at a short random offset.
# The companion is a genuinely separate node (not reused from the field
# pool), and it's added AFTER field-edge selection below so it can never
# be wired into the graph -- visually close, but disconnected, which is
# the point of the metaphor.
TEAL_COUNT = 12
SPLIT_PAIR_COUNT = 8  # how many teal nodes get a copper split companion

accent_idx = set(random.sample(range(len(nodes)), TEAL_COUNT))

# Pick a few nearby node pairs to connect with thin edges, so the field
# reads as a graph rather than pure scatter -- kept minimal (per note).
# Computed here, before copper companions exist, so split-brain pairs
# are guaranteed edge-free.
edges = []
for i, (x1, y1, *_ ) in enumerate(nodes):
    for j in range(i+1, len(nodes)):
        x2, y2, *_ = nodes[j]
        d = math.hypot(x1 - x2, y1 - y2)
        if d < 70:
            edges.append((i, j, d))
edges.sort(key=lambda e: e[2])
edges = edges[:10]  # keep it sparse -- a handful of real connections, not a web

split_pair_src = random.sample(sorted(accent_idx), SPLIT_PAIR_COUNT)
copper_idx = set()
for src_idx in split_pair_src:
    sx, sy, sr, sop = nodes[src_idx]
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(16, 26)
    cx = min(max(sx + dist * math.cos(angle), 12), W - 12)
    cy = min(max(sy + dist * math.sin(angle), 12), H - 12)
    if in_exclusion_zone(cx, cy):
        continue
    nodes.append((cx, cy, sr * 0.85, min(0.95, sop + 0.05)))
    copper_idx.add(len(nodes) - 1)

# --- Logo: equilateral triangle graph motif, matching the reference ---
# icon's proportions and rotation. In the reference, the three vertices
# sit at roughly -45, 75, and 195 degrees around the centroid (i.e. an
# equilateral triangle rotated so one vertex points up-and-right at a
# 45-degree offset from horizontal, rather than sitting flat-bottomed).
# Reconstructed here via polar coordinates around a centroid so the
# triangle is provably equilateral rather than hand-fit.
logo_center = (1270, 178)
logo_R = 58  # circumradius -> side length = R * sqrt(3) ~= 100.5
logo_node_r = 11

def polar(cx, cy, r, deg):
    rad = math.radians(deg)
    return (cx + r * math.cos(rad), cy + r * math.sin(rad))

logo = {
    "teal":   polar(*logo_center, logo_R, -45),
    "bottom": polar(*logo_center, logo_R, 75),
    "left":   polar(*logo_center, logo_R, 195),
}
logo = {k: (x, y, logo_node_r) for k, (x, y) in logo.items()}

# --- Build SVG ----------------------------------------------------------
svg_parts = []
svg_parts.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">')
svg_parts.append('''<defs>
  <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#12312c"/>
    <stop offset="55%" stop-color="#0a1a18"/>
    <stop offset="100%" stop-color="#060707"/>
  </linearGradient>
  <filter id="softGlow" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="4" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>''')
svg_parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bgGrad)"/>')

# field edges (drawn first, under nodes)
svg_parts.append('<g stroke="' + TEAL + '" stroke-width="1.2" stroke-opacity="0.45">')
for i, j, _ in edges:
    x1, y1, *_ = nodes[i]
    x2, y2, *_ = nodes[j]
    svg_parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
svg_parts.append('</g>')

# field nodes
svg_parts.append('<g>')
for idx, (x, y, r, op) in enumerate(nodes):
    if idx in accent_idx:
        color = TEAL
    elif idx in copper_idx:
        color = COPPER
    else:
        color = OFFWHITE
    svg_parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color}" fill-opacity="{op:.2f}"/>')
svg_parts.append('</g>')

# logo group
lt, ll, lb = logo["teal"], logo["left"], logo["bottom"]
svg_parts.append('<g filter="url(#softGlow)">')
svg_parts.append(f'<line x1="{ll[0]}" y1="{ll[1]}" x2="{lt[0]}" y2="{lt[1]}" stroke="{TEAL}" stroke-width="3"/>')
svg_parts.append(f'<line x1="{ll[0]}" y1="{ll[1]}" x2="{lb[0]}" y2="{lb[1]}" stroke="{TEAL}" stroke-width="3"/>')
svg_parts.append(f'<line x1="{lt[0]}" y1="{lt[1]}" x2="{lb[0]}" y2="{lb[1]}" stroke="{TEAL}" stroke-width="3"/>')
svg_parts.append(f'<circle cx="{lt[0]}" cy="{lt[1]}" r="{lt[2]}" fill="{TEAL}"/>')
svg_parts.append(f'<circle cx="{ll[0]}" cy="{ll[1]}" r="{ll[2]}" fill="{OFFWHITE}"/>')
svg_parts.append(f'<circle cx="{lb[0]}" cy="{lb[1]}" r="{lb[2]}" fill="{OFFWHITE}"/>')
svg_parts.append('</g>')

svg_parts.append('</svg>')

svg = "\n".join(svg_parts)
with open("banner111.svg", "w") as f:
    f.write(svg)

print(f"Generated {len(nodes)} field nodes, {len(edges)} field edges, "
      f"{len(accent_idx)} teal accents, {len(copper_idx)} copper accents.")
