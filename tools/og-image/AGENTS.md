# Brand image generators

Two generators for the brand's social/event images. Values (date, venue,
tagline) are hardcoded in each script.

- **`generate.py`** → `og.svg` + `../../static/og-image.png` — the 1200×630
  Open Graph / Twitter card for link previews of `out-of-context.dev` (shipped
  by the site).
- **`luma_cover.py`** → `luma-cover.svg` + `luma-cover.png` — the 1080×1080
  Lu.ma event cover. **Not** shipped by the site; upload `luma-cover.png` to the
  Lu.ma event by hand.

## Regenerate

```bash
python3 tools/og-image/generate.py      # OG card  → commit static/og-image.png
python3 tools/og-image/luma_cover.py    # Lu.ma cover (upload the PNG manually)
```

Rerun whenever the **date, venue, or tagline** changes, then commit the PNG(s).

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

Off-white `#f3f2f2` field, dark `#201e1d` headline ("Demoja, ei kalvoja."), a big
`OUT OF CONTEXT` wordmark, and a large two-line date/location. The braille
"context window" grid spells **OUT OF CONTEXT** as **favicon tiles** — red
squares with off-white square dots, off-white gaps, **no** solid orange panel
behind them (see the root `AGENTS.md` "Design" note for the shared tile motif).
The `.svg` files are the rendered source, kept in git for diff visibility; the
PNGs are the assets.
