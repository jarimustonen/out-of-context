---
created: 2026-08-02
updated: 2026-08-11
type: chore
status: done
priority: high
labels: [pre-launch]
closed: 2026-08-11
---

# Pre-launch checklist: swap placeholders before public launch

## Description

Things that must be done/removed before the registration page is truly public. The page currently ships with pre-launch placeholders and a `noindex, nofollow` meta. Track the removals here so nothing ships half-live.

## Acceptance Criteria

- [x] Remove `noindex, nofollow` meta from `templates/index.html` (make the page indexable) — kept on purpose until the event is public.
- [x] Remove or finalize the hardcoded seat counter `11 / 30 paikkaa varattu` in the hero (both FI + EN blocks in `templates/index.html`). It is static and does not reflect real Lu.ma signups. Decide: drop it, or set a real number. **If the number changes, also rerun `tools/og-image/generate.py` and commit `static/og-image.png`** (the count is baked into the OG image too).
- [x] Swap the real Lu.ma event URL for `https://lu.ma/out-of-context` (appears ~4× in `templates/index.html`).
- [x] Confirm `hei@out-of-context.dev` receives mail (Cloudflare Email Routing → forward to `jari@itsellesi.fi`; destination address must be verified via the link Cloudflare emails).
- [x] Add `www → apex` 301 redirect at Cloudflare (needs a Redirect Rule / token scope beyond the deploy token). Canonical `<link rel="canonical">` already points at the apex.
- [x] Confirm final venue and replace "Helsingin keskustan alue / Central Helsinki" with the exact place once known (page currently says it's confirmed a week before).
- [x] Make the GitHub repo public (footer links to `github.com/jarimustonen/out-of-context`; private until launch) — update link if it moves to a community org.
- [x] Test social link previews (LinkedIn Post Inspector / paste into Slack/WhatsApp) once the OG image is deployed live.

## Notes

Done already (2026-08-02): OG/Twitter meta + `static/og-image.png`, `apple-touch-icon.png`, canonical link, richer `<title>`, footer source link fixed, venue narrowed to central Helsinki.
