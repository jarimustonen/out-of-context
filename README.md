# Out of Context

Website for **Out of Context** — a Helsinki meetup for people who build with AI.

> Ilta sinulle joka luot AI:lla. Demoja, ei kalvoja.
> *An evening for people who build with AI. Demos, not slides.*

A static site built with [Zola](https://www.getzola.org/). One self-contained
page, bilingual (FI/EN), no backend, no cookies, no tracking.

## Develop

```bash
zola serve      # local preview at http://127.0.0.1:1111
zola build      # production build → public/
```

Edit the page in `templates/index.html`; site-wide metadata in `config.toml`.

## Deploy

```bash
./deploy.sh     # zola build → Cloudflare Pages (out-of-context.dev)
```

Put the real Cloudflare token in place once (`sops operations/secrets/cloudflare.enc.yaml`),
then `./deploy.sh`. Token permissions + custom-domain setup: `operations/secrets/AGENTS.md`.

## Status

Private, pre-launch. Goes public — and the `noindex` meta comes off — when the
first event is announced. See `AGENTS.md` for the placeholder checklist.

## License

MIT.
