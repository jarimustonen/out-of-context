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
| **Zone** | DNS | **Edit** | Only needed when attaching the `out-of-context.dev` custom domain to the Pages project (records + verification) |

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

## Attaching the custom domain (one-time, later)

1. Add `out-of-context.dev` as a zone in the Cloudflare account (register or
   move nameservers).
2. Cloudflare dashboard → Workers & Pages → `out-of-context` → Custom domains →
   add `out-of-context.dev`. Cloudflare creates the CNAME + validates.
3. Re-run `./deploy.sh`; the account-id-from-zone lookup now succeeds
   automatically.

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
