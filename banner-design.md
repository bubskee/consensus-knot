## Banner Design

This visual identity — a node/graph motif in teal and copper on a dark
teal-black field — was built iteratively through a series of generated
SVGs, starting from a hand-drawn sketch and refined through a few rounds
of feedback.

### Starting point

The concept began as a rough sketch for a LinkedIn banner (1584×396px):
a field of scattered, loosely-connected nodes on the left, thinning out
toward a small logo mark on the right, over a dark gradient background.

### Establishing the visual language

Early feedback settled a few core principles that carried through the
rest of the process:

- **Sparse over dense.** A handful of real graph edges (not a fully
  connected web) reads as intentional; too many looks like generic
  stock "network" art.
- **Accent color used sparingly.** A small number of colored nodes
  against a mostly off-white/dark field reads as deliberate; full color
  reads as decorative.
- **Design around the platform.** LinkedIn's circular profile photo
  overlaps the bottom-left of the banner on desktop — the densest part
  of the node field was kept clear of that zone, and the horizontal
  band where LinkedIn overlays name/headline text was thinned out too.

### Building the generator

Rather than hand-placing nodes, the field is generated programmatically
(`gen_banner.py`):

- Node x-positions are sampled from an exponentially decaying
  distribution, so the "dense → sparse" gradient toward the logo is a
  real falloff rather than an eyeballed approximation.
- Node size and opacity both scale with the same depth factor, so
  smaller/fainter nodes read as further into the fade.
- A small number of nearest-neighbor pairs are connected with thin
  edges, keeping the graph reading sparse and deliberate.

### Iterating on accent color and pattern

The accent scheme went through a few rounds:

1. Started with a single teal accent color on a few nodes.
2. Added copper as a second, contrasting accent in equal measure.
3. Landed on the final pattern: **teal/copper node pairs placed a short
   random distance apart, deliberately *not* connected by a graph
   edge** — evoking split-brain nodes in a distributed consensus log
   (two nodes disagreeing at close range, out of sync with the rest of
   the network). Copper companions are generated *after* the field's
   edges are chosen, so they're structurally guaranteed to stay
   unconnected.
