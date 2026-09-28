# Out of Context

Static site for **Out of Context**, a Helsinki meetup for people who build with
AI. "Ilta sinulle joka luot AI:lla. Demoja, ei kalvoja." It lives at
`out-of-context.dev` and is one page: who the evening is for, when and where the
next one is, and a registration link. The event's own rule is the content's
north star: if you talk, you show something running; no slides; crashing demos
welcome. A good change to this site keeps that voice and gets the facts right,
because the page is live and people plan an evening around what it says.

The repository is public (`github.com/jarimustonen/out-of-context`) and meant
to become community-owned with PRs. Commit messages, issue text, and anything
committed are public. The one secret, the Cloudflare API token, is
SOPS-encrypted; `operations/secrets/AGENTS.md` explains what it can do, how the
zone is set up, and how to handle decrypted values.

## How the site is built

Zola renders a single template, `templates/index.html`, into a self-contained
HTML document with inline CSS and a small language-toggle script.
`content/_index.md` exists only to select that template; every word of the
page, including the event facts, lives in the template. `config.toml` supplies
the base URL and the meta description (reused for the Open Graph and Twitter
descriptions); the template does not use its `title`. `zola serve` previews
at `http://127.0.0.1:1111`, `zola build` writes `public/`, and `./deploy.sh`
builds and publishes to Cloudflare Pages. Deploying is cheap and reversible,
since Pages keeps every deployment; the secrets document covers the token and
the domain, redirect, and email routing that sit in front of the site.

The page tells its readers, in its own text, that it collects no data and uses
no cookies. There is no backend, no analytics, and no third-party script; the
only external request is Google Fonts for Archivo. A tracker or an embedded
widget would break a promise printed on the page.

Finnish is the primary language and the default. Both languages ship in the
one document: the `#lang-fi` block is shown, `#lang-en` is hidden, and
`setLang()` swaps them client-side and updates `<html lang>`. The two blocks
are complete parallel copies of the page, including the hero grid SVG, so a
change to one is half a change until the other has it too. Nothing checks
that they agree, and nothing renders the page in a test; look at it in
`zola serve` in both languages.

## Where the event facts live

The event number, date, time, venue, seat count, and Lu.ma URL are literal
strings in several places with no shared source:

- `templates/index.html`: the `<title>` and the Open Graph and Twitter meta
  in the head, then the FI block and the EN block (hero eyebrow, headline and
  sign-up button, the seats cell of the facts row, and the registration box).
- `tools/og-image/generate.py` and `tools/og-image/luma_cover.py`, which
  render the share card `static/og-image.png` and the Lu.ma cover.
- `README.md`'s status line and the "Current event" section below.

When the event changes, all of these move together. The images are the
easiest to forget because nothing compares them with the page;
`tools/og-image/AGENTS.md` covers rendering them and the font trap, and the
Lu.ma cover has to be uploaded to Lu.ma by hand, which an agent cannot do. The
page also states the recurrence rule, "joka kuun se keskiviikko joka osuu
päiville 12.–18.", so a new date should satisfy it or the rule text has to
change with it. Social platforms cache link previews per URL: the origin
serves the latest card, but a link shared earlier shows the old one until it
is re-scraped (Facebook's Sharing Debugger) or shared with a changed query
string such as `/?v=2`.

## Current event

The site went public on 2026-08-04. It now promotes **Demoilta #2** on
Wednesday 14 October 2026 at 17:00, Vilhonkatu 4 B 18, Helsinki, free, about
30 seats; registration is at `luma.com/tf4w6epb`. The page is indexable,
`hei@out-of-context.dev` forwards to Jari, and `www` redirects to the apex.
Other documents in this repo treat this section as the statement of what the
site currently promotes, so it changes together with the event.

## Design

Deliberately not the generic AI-generated look. A modernist red grid: accent
`#ec3013` on warm off-white `#f3f2f2`, Archivo with 800-weight headings, no
rounded corners, 2px dividers, a hard grid. The signature element is the
"context window" in the hero: a grid seven tiles wide and five tall that
spells OUT OF CONTEXT in braille, one letter per tile, as inline SVG. Each
tile is the favicon, a red square with off-white square dots, so the same
motif carries across `favicon.svg`, the hero, the share card, and the Lu.ma
cover. On red surfaces the marks are off-white; on the off-white field the
tiles are red. The braille letter map and tile geometry are duplicated in the
two hero SVGs and in both image scripts, so a change to the motif has four
homes.

The editorial rule that governs everything: *one bold choice, everything else
quiet.* Copy is short and direct, written in Finnish first; the English is a
translation of equal standing, not a summary. Wording and layout decisions
inside this language are yours to make and to say you made. A departure from
it, such as a new colour, rounded corners, a second bold element, or a
different typeface, is a matter of taste that Jari owns; raise it before it
goes live rather than after.

## Repository conventions

- Every directory with agent guidance, apart from the issuectl-managed
  `issues/` and `.issuectl/`, has `AGENTS.md` as the file and `CLAUDE.md` as a
  symlink to it, so every harness reads the same text. Long topics split into
  `AGENTS-<TOPIC>.md`.
- `AGENTS-AI-FIRST-CLI.md` is a copy of the CLI canon shared across Jari's
  repositories, maintained upstream in `project-canon`. This repo has no CLI; the
  copy is here so that a CLI added later follows the family conventions. Edits
  belong upstream, because a local edit diverges silently from every other
  copy.
- Issues live in `issues/` and are managed by `issuectl` through the `/issue`
  skill; `issues/AGENTS.md` and `.issuectl/AGENTS.md` are the references.
  Plans, analyses, and designs live under the issue they belong to.
- `history/` is gitignored scratch space for an agent's ephemeral notes.
  Durable knowledge goes in the most specific `AGENTS.md` or in an issue.
  `public/` and `.wrangler/` are build and deploy output.

## Provenance

The page began as a hidden demo inside the Frondeo Zola site at
`frondeo.ai/out-of-context/` and was spun out into this repo so it could have
its own domain and community. That is why the deploy script and the secrets
setup mirror frondeo.ai's, and why the Cloudflare account is shared with
Frondeo while the token is not. The Frondeo copy's source was removed from the
Frondeo monorepo when this repo was created on 2026-08-02.
