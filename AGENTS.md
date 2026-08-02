# Out of Context

Static site for **Out of Context** — a Helsinki meetup / community for people who
build with AI. "Ilta sinulle joka luot AI:lla. Demoja, ei kalvoja." Lives at
`out-of-context.dev`. This repo is Jari's personal repo for now
(`github.com/jarimustonen/out-of-context`, private) and goes **public at launch**;
the intent is a community-owned public repo with PRs.

## Technology

- **Generator**: [Zola](https://www.getzola.org/) (Rust static site generator, v0.22+).
- **No backend, no build step beyond Zola, no cookies, no analytics.** The page
  is a single self-contained HTML document with inline CSS + a tiny FI/EN toggle
  script. Only external dependency is Google Fonts (Archivo).
- **Deployment**: static hosting (Cloudflare Pages, same pattern as frondeo.ai) —
  not yet wired up.

## Structure

```
out-of-context/
├── config.toml            # Zola config (base_url, title, description)
├── content/
│   └── _index.md          # Homepage — template = "index.html", holds meta
├── templates/
│   └── index.html         # THE page. Bespoke design, FI+EN content inline.
└── static/
    └── favicon.svg        # Red square favicon
```

The homepage is rendered from `templates/index.html`, driven by `content/_index.md`
(`section` in Tera). `config.title` / `config.description` fill `<title>` and the
meta description. `zola build` → `public/` (gitignored).

## Development

```bash
zola serve      # local hot-reload at http://127.0.0.1:1111
zola build      # production build → public/
```

## Design

Deliberately **not** the generic AI-generated look. Modernist red grid:

- **Accent**: `#ec3013` (red) on a warm off-white `#f3f2f2`.
- **Type**: Archivo (800 headings), no rounded corners, 2px dividers, hard grid.
- Signature element: the "context window" seat grid in the hero (filled = taken).
- Bilingual: FI shown by default, EN toggled client-side (`setLang()`); no routing,
  both languages ship in one document.

Editorial rule that governs everything: *one bold choice, everything else quiet.*
The event's own rule — **if you talk, you show something running; no slides;
crashing demos welcome** — is the content's north star.

## Pre-launch placeholders (swap before going live)

All live in `templates/index.html`:

- `https://lu.ma/out-of-context` — real Lu.ma event URL
- `hei@out-of-context.dev` — real contact address
- `github.com/out-of-context/site` (footer) — final public repo URL
- venue / time / `11 / 30` seat count — confirmed nearer the date
- `noindex, nofollow` meta — **remove when the event is public**

## Provenance

The page was first built as a hidden team-demo inside the Frondeo Zola site
(`frondeo.ai/out-of-context/`). It was spun out here into its own repo so it can
grow into a community-owned site on its own domain. The Frondeo copy is being
retired now that this standalone repo exists.

## CLI Design Principles

This project follows the AI-first CLI conventions in
[`AGENTS-AI-FIRST-CLI.md`](AGENTS-AI-FIRST-CLI.md) — shared canon copied from
`homebase`; treat it as read-only reference, not a project-local doc to edit.
(This repo currently ships no CLI, but the conventions apply if one is added.)

## Documentation Pattern

Every directory follows this structure:

- `CLAUDE.md` — symlink to `AGENTS.md`
- `AGENTS.md` — all AI-relevant info (consolidated)
- `AGENTS-<TOPIC>.md` — complex topics split out (optional)

## Issues & Planning

Issue tracking is managed by [`issuectl`](https://github.com/jarimustonen/issuectl).
Use the `/issue` skill (installed by `issuectl init`) to create, search, update,
and close issues.

- `issues/<slug>/item.md` — every issue and epic (flat layout)
- Status lives in the `status:` frontmatter field, not in the path
- All planning docs (plans, analyses, designs) live under their parent issue directory

## Gitignored directories

- `history/` — agent scratchpad and ephemeral planning docs (not tracked)
- `public/` — Zola build output
