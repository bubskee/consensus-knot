import math

W = H = 500

TEAL = "#3a9b8f"
OFFWHITE = "#e8e8e6"
BG = "#0d1a17"  # deep teal-black, matches the darkest stop of the
                # banner's background gradient for brand consistency

# --- Equilateral triangle construction ---------------------------------
# Same approach as the banner logo: vertices placed at -45, 75, and 195
# degrees around a centroid via polar coordinates, so the triangle is
# provably equilateral and matches the reference icon's rotation (one
# vertex pointing up-and-right at a 45-degree offset from horizontal).
center = (W / 2, H / 2)
R = 150          # circumradius -> side length = R * sqrt(3) ~= 260
node_r = 28       # kept at the same ratio to R as the banner logo (~0.19)
stroke_w = 8      # kept at the same ratio to R as the banner logo (~0.052)
glow_blur = 10    # kept at the same ratio to node_r as the banner logo

def polar(cx, cy, r, deg):
    rad = math.radians(deg)
    return (cx + r * math.cos(rad), cy + r * math.sin(rad))

logo = {
    "teal":   polar(*center, R, -45),
    "bottom": polar(*center, R, 75),
    "left":   polar(*center, R, 195),
}
logo = {k: (x, y, node_r) for k, (x, y) in logo.items()}

# --- Build SVG ------------------------------------------------------------
svg_parts = []
svg_parts.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">')
svg_parts.append(f'''<defs>
  <filter id="softGlow" x="-100%" y="-100%" width="300%" height="300%">
    <feGaussianBlur stdDeviation="{glow_blur}" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>''')
svg_parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>')

lt, ll, lb = logo["teal"], logo["left"], logo["bottom"]
svg_parts.append('<g filter="url(#softGlow)">')
svg_parts.append(f'<line x1="{ll[0]:.1f}" y1="{ll[1]:.1f}" x2="{lt[0]:.1f}" y2="{lt[1]:.1f}" stroke="{TEAL}" stroke-width="{stroke_w}"/>')
svg_parts.append(f'<line x1="{ll[0]:.1f}" y1="{ll[1]:.1f}" x2="{lb[0]:.1f}" y2="{lb[1]:.1f}" stroke="{TEAL}" stroke-width="{stroke_w}"/>')
svg_parts.append(f'<line x1="{lt[0]:.1f}" y1="{lt[1]:.1f}" x2="{lb[0]:.1f}" y2="{lb[1]:.1f}" stroke="{TEAL}" stroke-width="{stroke_w}"/>')
svg_parts.append(f'<circle cx="{lt[0]:.1f}" cy="{lt[1]:.1f}" r="{lt[2]}" fill="{TEAL}"/>')
svg_parts.append(f'<circle cx="{ll[0]:.1f}" cy="{ll[1]:.1f}" r="{ll[2]}" fill="{OFFWHITE}"/>')
svg_parts.append(f'<circle cx="{lb[0]:.1f}" cy="{lb[1]:.1f}" r="{lb[2]}" fill="{OFFWHITE}"/>')
svg_parts.append('</g>')

svg_parts.append('</svg>')

with open("/mnt/user-data/outputs/github_logo.svg", "w") as f:
    f.write("\n".join(svg_parts))

print("Wrote github_logo.svg")
