# Hero Art Direction

The first hero pass follows the generated visual target in `assets/reference/hero-concept.png`.

Core identity:

- Pointed hood/cap with the tip falling to the hero's left.
- Pale diagonal stripe across the hood, kept as a signature read at small size.
- Compact cloak/tunic silhouette with a tiny belt and dark boots.
- Round shield mass with a light emblem.
- Simple sword/tool shape for attack and side-facing readability.
- Four visible Game Boy-inspired colors plus transparent sprite pixels.

Implementation choice:

- The playable visual sprite is `128x128` so the game can keep the generated concept's level of detail.
- Recommended world tile size is `64x64`; the hero frame is larger than a tile, with a smaller foot hitbox.
- Recommended logical viewport starts at `640x360`, then scales up with nearest-neighbor rendering.
- Collision should use the smaller hitbox in `assets/hero/hero.json`.
- The source of truth is `scripts/generate-hero.py`; regenerate with `npm run generate:hero`.
