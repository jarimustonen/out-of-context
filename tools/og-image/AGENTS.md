# Brand image generators

Two small Python scripts render the brand's event images from inline SVG via
`rsvg-convert`. Both draw the same composition at different sizes: the
`OUT OF CONTEXT` wordmark, the event headline, a red date line, a muted venue
line, and the braille "context window" grid rendered as favicon tiles.

- `generate.py` writes `og.svg` here and `static/og-image.png` at the repo root.
  The PNG is the 1200×630 Open Graph / Twitter card that `templates/index.html`
  points at, so it ships with the site.
- `luma_cover.py` writes `luma-cover.svg` and `luma-cover.png` here. The PNG is
  the 1080×1080 Lu.ma event cover. The site does not serve it; someone has to
  upload it to the Lu.ma event by hand, which an agent cannot do. Say so when
  you regenerate it.

The SVGs are committed alongside the PNGs so that a change to the composition
shows up as a readable diff rather than a binary blob.

## What the images say, and where else it is said

Event facts (headline, date, time, venue, "ilmainen") are literal strings in
each script, not read from `content/` or `config.toml`. The same facts also
appear in `templates/index.html` in both language blocks. When the event
changes, all of these have to move together, and the images are the easiest to
forget because nothing checks them against the page. The root `AGENTS.md`
"Current event" section is the statement of what the site currently promotes;
the images should agree with it.

The braille letter map and tile geometry (7×5 grid, dot size 0.22 of a tile,
dot positions at 0.34/0.66 and 0.24/0.5/0.76) are duplicated in both scripts
and, as static markup, in the two hero SVGs in `templates/index.html`. There is
no shared source. A change to the motif has to be carried to all four places or
the site and the share cards drift apart.

## Design intent

The root `AGENTS.md` "Design" section describes the brand: red `#ec3013` on
warm off-white `#f3f2f2`, Archivo 800 headings, hard grid, and the favicon tile
as the unifying motif. The images follow it. Two decisions from the history are
worth knowing because they are easy to undo by accident:

- An earlier OG card put the grid on a solid red panel. It was dropped so that
  the grid reads as the same red-on-off-white tiles as the favicon and the hero,
  with off-white gaps between tiles. Red tiles directly on the off-white field
  is the intended look.
- The grid is aligned to the text margins: right edge flush with the text
  column's margin on the OG card, full content width on the square Lu.ma cover
  so the right side is not empty. Text sizes were tuned by eye against real
  renders; check the PNG after any change rather than trusting the numbers.

## Rendering dependencies

`rsvg-convert` comes from librsvg. The type is **Archivo Black**, the heavy
static cut that matches the site's Archivo 800 headings, and it has to be
visible to fontconfig. The trap: if it is not, fontconfig substitutes another
sans-serif and `rsvg-convert` exits zero, so the script reports success and
writes a wrong-looking PNG. Check `fc-match "Archivo Black"` before rendering,
or open the PNG afterwards. Neither machine this repo has been worked on ships
the font by default.

The TTF is OFL-licensed and lives in the Google Fonts repository:

```bash
curl -sSL -o ArchivoBlack-Regular.ttf \
  https://github.com/google/fonts/raw/main/ofl/archivoblack/ArchivoBlack-Regular.ttf
```

Drop it in the platform's user font directory (`~/Library/Fonts` on macOS,
`~/.local/share/fonts` plus `fc-cache` on Linux). If you would rather not add a
font to the user's system for a one-off render, point `FONTCONFIG_FILE` at a
small `fonts.conf` whose `<dir>` contains the TTF; the render sees the font and
the user's font set is untouched.

## After regenerating

Commit the changed SVGs and PNGs together with the content change that
motivated them. Social platforms cache OG previews per URL; the root
`AGENTS.md` "Current event" section explains how to force a fresh preview.
