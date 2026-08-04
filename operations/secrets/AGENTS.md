# Secrets & deployment

SOPS with age encryption (config in `/.sops.yaml`), plus the site deploy to
Cloudflare Pages (`/deploy.sh`).

## Deploy in one line

```bash
./deploy.sh
```

It builds the Zola site (`public/`) and runs `wrangler pages deploy` to the
Cloudflare Pages project `out-of-context`. The token comes from
`CLOUDFLARE_API_TOKEN` (env) or, if unset, from the SOPS-encrypted
`operations/secrets/cloudflare.enc.yaml` (`api_token` key). The first deploy
creates the project and serves it at `https://out-of-context.pages.dev`.

## Put the real Cloudflare token in place

The encrypted secret already exists with a placeholder. Drop in the real token:

```bash
sops operations/secrets/cloudflare.enc.yaml
# replace:  api_token: REPLACE_WITH_REAL_CLOUDFLARE_API_TOKEN
# with:     api_token: <real token>
```

Then `./deploy.sh`. Nothing else to wire up. (`sops` decrypts with your age key
at `~/.config/sops/age/keys.txt` — the same key already used for the frondeo repo.)

Verify without printing the value:

```bash
sops -d operations/secrets/cloudflare.enc.yaml >/dev/null && echo OK
```

## Cloudflare API token — required permissions

Create the token at **Cloudflare dashboard → My Profile → API Tokens → Create
Token → Create Custom Token**. This site is deployed with Cloudflare Pages via
wrangler, so scope the token to exactly what that needs:

| Scope | Resource | Permission | Why |
|-------|----------|------------|-----|
| **Account** | Cloudflare Pages | **Edit** | Create the Pages project and push deployments (the core permission — wrangler needs it) |
| **Account** | Account Settings | **Read** | Lets wrangler enumerate/confirm the account when the account id isn't pinned |
| **Zone** | Zone | **Read** | `deploy.sh` resolves the account id from the `out-of-context.dev` zone; also needed to attach the custom domain |
| **Zone** | DNS | **Edit** | Attach the custom domain (records + verification); create the email-routing MX/TXT |
| **Zone** | Email Routing Rules | **Edit** | Create the `hei@` forward rule via API (added 2026-08-04) |
| **Zone** | Dynamic Redirect | **Edit** | Create the `www`→apex 301 Single Redirect via API (added 2026-08-04) |

**Account Resources**: include your Cloudflare account (the same one that hosts
frondeo.ai).
**Zone Resources**: `out-of-context.dev` once the domain is on Cloudflare;
until then just leave the Account-level Pages:Edit — that alone is enough to
deploy to `*.pages.dev`.

Minimal to get a first `*.pages.dev` deploy: **Account → Cloudflare Pages →
Edit** only. The Zone rows matter once you point the real domain at it.

> Keep this token distinct from the frondeo `cloudflare.enc.yaml` token. This
> one only needs Pages + the out-of-context.dev zone, not the full frondeo.ai /
> frondeo.cloud DNS surface.

## Custom domain + email + redirect — DONE (2026-08-04)

All live on the `out-of-context.dev` Cloudflare zone. Recorded here so the setup
is reproducible / debuggable, not because it needs redoing.

- **Custom domain**: `out-of-context.dev` (apex) and `www` are attached to the
  Pages project; both are `CNAME → out-of-context.pages.dev` (proxied). Apex uses
  CNAME flattening. TLS auto-issued. Attaching via API needed the domains POSTed
  to the project **and** the CNAME records created by hand (Cloudflare did not
  auto-create them).
- **`www` → apex**: a Single Redirect (an `http_request_dynamic_redirect`
  ruleset) 301s `www.out-of-context.dev/*` → `out-of-context.dev/*`, path + query
  preserved. Created via API (needs Dynamic Redirect: Edit). Rulesets take a
  minute to propagate across edges.
- **Email routing**: `hei@out-of-context.dev` → `jari@itsellesi.fi` (only `hei@`;
  catch-all is **off**). The forward *rule* is API-creatable (Email Routing
  Rules: Edit). But **enabling routing** (creates the MX/SPF/DKIM records) and
  **adding + verifying the destination address** are account-level dashboard
  steps the deploy token can't do — the destination needs a click on Cloudflare's
  verification email. **Gotcha**: Cloudflare Email Routing has its own spam
  filter (Email Routing → Settings) that can silently hold inbound mail — a Lu.ma
  sign-in code got stuck there once; it was neither in the M365 inbox, junk, nor
  quarantine because Cloudflare held it upstream.

## SOPS / age model

Single admin tier: every `*.enc.{yaml,json,env}` is encrypted to Jari's two age
keys (see `/.sops.yaml`). To add a maintainer as the project goes
community-owned:

1. They generate an age keypair **to a file** (never bare `age-keygen`, which
   prints the private key to stdout):
   ```bash
   mkdir -p ~/.config/sops/age && age-keygen -o ~/.config/sops/age/keys.txt
   age-keygen -y ~/.config/sops/age/keys.txt   # prints only the public age1... key
   ```
2. They append their public `age1...` key to the `age:` list in `/.sops.yaml`
   and commit + push (never the private key).
3. An existing key holder re-encrypts: `sops updatekeys operations/secrets/cloudflare.enc.yaml`
   and commits the result. (`updatekeys` only rewrites recipients once run — it
   is not a live ACL.)

**Never** let a decrypted secret reach the console — always pipe to a subshell
or `>/dev/null`. Never commit a private key (`AGE-SECRET-KEY-...`).

## Reference

- **SOPS config**: `/.sops.yaml`
- **Encrypted Cloudflare token**: `operations/secrets/cloudflare.enc.yaml`
- **Deploy script**: `/deploy.sh`
- **Private age key**: `~/.config/sops/age/keys.txt` (or `SOPS_AGE_KEY_FILE`)
