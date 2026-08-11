# The Consensus Knot: icon design process

A log of how this mark was designed, why each decision was made, and how to
regenerate it (or your own variant of it) from scratch.

## The idea

The mark needed to hold up as a small, abstract personal/brand icon while
carrying meaning across a few domains at once, rather than committing to a
single literal reading:

- **Distributed systems** — a nod to Raft/Paxos-style leader election and consensus
- **Society** — agreement, cooperation, mutual aid
- **Relationships** — interdependence and connectedness
- **Graph theory** — small structures, disproportionately deep implications (a wink toward TREE(3))

Three initial directions were sketched: a **consensus knot** (nodes in a
network, one highlighted as leader), a **rune mark** (an abstract angular
monogram), and an **anvil mark** (a craftsmanship symbol). The consensus knot
won out — it's the only one of the three that speaks to all four domains
above without extra explanation.

## Iteration log

### 1. Node count

Tried 3, 4, 6, and 8 nodes to see how the mark scaled. Beyond 4, a fully
connected graph gets unreadable fast (6 nodes complete = 15 edges, 8 nodes
complete = 28), so higher counts used a ring plus opposite-node "diameter"
connections instead of a true complete graph. At 8 nodes the mark stopped
reading as "consensus network" and drifted toward decorative mandala —
interesting, but a different mark. **Landed on 3 and 4 nodes** as the two
worth refining further; ultimately kept 3, since 4 nodes rotated 45° loses
the diamond's tension and reads as a generic network icon.

### 2. Orientation

Compared each node count at its "natural" upright angle versus a 45°
rotation. The upright 3-node triangle reads like an arrowhead — pointed,
directional. Rotated 45°, it settles onto a flatter base and reads calmer,
more balanced. **Kept the 45° tilt.**

### 3. Color, round one

Tested four treatments on the 4-node version to separate "which node
carries the accent color" from "what the accent color is":

| Variant | Leader | Connections | Read |
|---|---|---|---|
| Copper leader | `#c17d3a` | neutral gray | workshop / craft, literal leader-election |
| Indigo leader | `#6a5a9c` | neutral gray | cooler, more mythic |
| Accent on links | neutral outline | `#c17d3a` | moves the emphasis from *a* node to the *connections* — better fit for "mutual aid," worse fit for "leader election" |
| Mono copper | `#c17d3a` | `#c17d3a` at 35% opacity | quiet, reads as one object rather than hub-and-spoke |

### 4. Color, round two — narrowing on the tilted 3-node

Re-ran indigo and mono-copper on the 45°-tilted 3-node version, plus a new
option: a **celeste** (blue-green) leader, `#3aada0`. Celeste landed in a
sweet spot — calmer than copper, lighter than indigo, and it pairs with
"cooperation" better than either. **Celeste, mono-tone (leader and
connections in the same hue), tilted 3-node — chosen direction.**

### 5. Scale testing

Rendered the chosen mark at favicon (16px, 32px) and avatar (~130px) sizes.
Two problems surfaced:

- At 16–32px, thin unfilled "neutral" node outlines nearly disappear —
  a sub-1px stroke on a 4px circle doesn't render reliably.
- **Transparency is theme-dependent.** On a dark browser tab bar the mark
  pops; on light, it fades — the pale-ish teal and low-opacity connections
  don't have enough contrast against white on their own.

### 6. Fixing the background problem

Transparency assumes control over what's behind the mark, which isn't
available in practice (browser theme, OS theme, whatever platform renders
the avatar). The standard fix — and the one nearly every recognizable app
mark uses (Slack, Discord, VS Code, npm) — is to **bake in a solid
background field** rather than rely on transparency.

Two field options were compared:

| Field | Background | Leader | Connections | Read |
|---|---|---|---|---|
| Neutral dark | `#1c1c1c` | `#3aada0` | `#3aada0` @ 60% | simple, high contrast, works anywhere |
| Branded teal | `#15302d` | `#8fe0d3` (pale celeste) | `#8fe0d3` @ 55% | tonal — dark field, mid accent, pale highlight, all one hue family |

With a fixed, known background, the "neutral" (non-leader) nodes no longer
need an outline to read against an unpredictable backdrop — they're rendered
as solid pale fills instead, which also fixes the small-size legibility
problem from step 5.

**Guidance going forward:** use a background-baked version for anything that
stands alone (favicon, avatar, app icon). Keep a transparent, mark-only
version for contexts that already provide their own container — e.g. inline
next to a heading, where a redundant box-in-a-box would look wrong.

## Final specification

**Geometry** (three nodes, 45° tilt from upright):

- Node angles: `-45°`, `195°`, `75°` around the center (first angle is the leader)
- Orbit radius: `42/65` of the half-canvas
- Node radius: `8/65` of the half-canvas
- Stroke width: `2/130` of the canvas (for edges and any outlines)
- Background field corner radius (when used): `36/200` of the canvas

These ratios are preserved across every size so the mark looks the same
shape whether it's 16px or 500px — only the background/foreground colors
change between variants.

**Color palettes:**

| Palette | Background | Leader | Connections | Neutral nodes |
|---|---|---|---|---|
| `transparent` | none | `#3aada0` | `#3aada0` @ 35% | `#ffffff` fill, `#2b2b2b` stroke |
| `neutral-dark` | `#1c1c1c` | `#3aada0` | `#3aada0` @ 60% | `#e8e8e8`, no stroke |
| `teal-field` | `#15302d` | `#8fe0d3` | `#8fe0d3` @ 55% | `#eef7f5`, no stroke |

## Reproducing it

`consensus_knot.py` (in this repo) renders any of the palettes above at any
size list. It draws at high resolution (1024px by default) and downsamples
with Lanczos filtering — the same supersample-then-shrink approach real
favicon pipelines use — so small sizes stay clean rather than looking like a
naive small-scale vector rasterization.

```bash
pip install pillow
python consensus_knot.py --field teal-field --sizes 16,32,128,512 --out ./out
```

To try your own variant, edit the `PALETTES` dict at the top of the script —
add an entry with your own background/leader/connection/neutral colors and
pass its name to `--field`. To try a different tilt or node count, adjust
`ANGLES` (add a fourth angle for a 4-node version, for example) and update
the edge-drawing loop to connect however many nodes you have.

## Rejected directions, for the record

- **Rune mark** and **anvil mark** — both solid concepts, set aside because
  neither carried more than one or two of the four resonant domains at once.
- **6 and 8 node versions** — visually interesting (the 8-node ring-plus-diameters
  version reads as a small mandala) but drifted away from "consensus network"
  toward generic decorative pattern.
- **4-node, 45°-rotated (square)** — technically the same graph as the diamond,
  just rotated, but loses the diamond's directional tension and reads as a
  generic network/mesh icon rather than something distinctive.
