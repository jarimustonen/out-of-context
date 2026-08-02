# OG image generator

Generates `static/og-image.png` — the 1200×630 Open Graph / Twitter card image
used for social-media link previews of `out-of-context.dev`.

## Regenerate

```bash
python3 tools/og-image/generate.py    # rewrites og.svg + static/og-image.png
```

Rerun whenever the **date, seat count, or tagline** baked into the image
changes (they are hardcoded in `generate.py`), then commit the new
`static/og-image.png`.

## Dependencies

- `rsvg-convert` (librsvg) — `brew install librsvg`
- **Archivo Black** TTF, discoverable by fontconfig. It is the heavy static cut
  matching the site's Archivo 800 headings. If `fc-match "Archivo Black"` does
  not resolve it:

  ```bash
  curl -sSL -o ~/Library/Fonts/ArchivoBlack-Regular.ttf \
    https://github.com/google/fonts/raw/main/ofl/archivoblack/ArchivoBlack-Regular.ttf
  ```

  (OFL licensed.) Or point `FONTCONFIG_FILE` at a local `fonts.conf` whose
  `<dir>` contains the TTF, so the user's font set is left untouched.

## Design

Mirrors the homepage: off-white `#f3f2f2` field, dark `#201e1d` headline
("Demoja, ei kalvoja."), red `#ec3013` kicker, and a right-hand red panel
carrying the signature "context window" seat grid. `og.svg` is the rendered
source, kept in git for diff visibility; the PNG is the shipped asset.
