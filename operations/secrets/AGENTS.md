# Secrets & deployment

This directory holds the one real secret the site has: the Cloudflare API token
that `deploy.sh` uses to publish to Cloudflare Pages. It is SOPS-encrypted to
age recipients listed in `/.sops.yaml`. The repository is public, so the
encryption is the only thing between the token and the world; the encrypted
file itself is fine to commit, and its `#` comment lines are encrypted too.

## Deploying

`./deploy.sh` builds the site and pushes `public/` to the Pages project
`out-of-context`. Its header comment documents the required tools and how it
finds the token (environment variable first, then this directory's encrypted
file). The script refuses to run with the placeholder token, so a failed token
check is a decryption problem, not a placeholder one. The real token has been
in place since launch on 2026-08-04.

Deploying is routine and cheap. Pages keeps every deployment and the dashboard
can roll back to any of them, so a bad deploy costs a minute, not the site. Do
it whenever the content is ready; nobody needs to be asked.

To check that decryption works on this machine without showing the value:

```bash
sops -d operations/secrets/cloudflare.enc.yaml >/dev/null && echo OK
```

Decryption uses the age key at `~/.config/sops/age/keys.txt` (or
`SOPS_AGE_KEY_FILE`). Jari's two machines hold it; it is the same key used for
the frondeo repo. The account id can optionally be pinned as `account_id` inside
the encrypted file to skip the zone lookup; it is not pinned today and the
lookup works, so this only matters if the zone lookup ever fails.

## What the token can do, and why it matters

The token is a custom token created in the Cloudflare dashboard (My Profile →
API Tokens → Create Custom Token), scoped to the account that also hosts
frondeo.ai and to the `out-of-context.dev` zone. These are the grants and what
each one is for, so that a replacement token can be cut with the same shape:

| Scope | Resource | Permission | Why |
|-------|----------|------------|-----|
| Account | Cloudflare Pages | Edit | Create the project and push deployments. The only grant needed to deploy to `*.pages.dev`. |
| Account | Account Settings | Read | Lets wrangler confirm the account when the id is not pinned. |
| Zone | Zone | Read | `deploy.sh` resolves the account id from the zone; also needed to attach the custom domain. |
| Zone | DNS | Edit | Attach the custom domain and create the email-routing MX/TXT records. |
| Zone | Email Routing Rules | Edit | Create the `hei@` forward rule via API. |
| Zone | Dynamic Redirect | Edit | Create the `www` → apex redirect via API. |

The zone grants mean a leaked token lets someone rewrite this domain's DNS and
mail routing, not just push a deployment. That is why it is a separate token
from frondeo's, whose zone grants cover frondeo.ai and frondeo.cloud: a leak
here should not reach there. If the token is ever exposed, whether in a
transcript, a commit, or an issue, the fix is to revoke and re-create it in the
dashboard, which only Jari can do; removing an age recipient does not help,
because the public git history still holds every earlier encrypted revision.

Things the token deliberately cannot do are account-level dashboard steps:
enabling Email Routing on the zone, and adding or verifying the destination
address (the destination has to click Cloudflare's verification email).

## How the zone is set up

All of this has been live since 2026-08-04 and is recorded for debugging and
rebuilding, not because it needs doing again.

**Custom domain.** `out-of-context.dev` and `www` are attached to the Pages
project. Both are proxied `CNAME → out-of-context.pages.dev`; the apex uses
CNAME flattening; TLS was issued automatically. When this was done via the API,
adding the domains to the project did not create the DNS records, so the CNAMEs
had to be created separately. Expect the same if a domain is ever re-attached.

**`www` → apex.** A Single Redirect (an `http_request_dynamic_redirect` ruleset)
returns 301 from `www.out-of-context.dev/*` to `out-of-context.dev/*` with path
and query preserved. Rulesets take about a minute to reach all edges, so a
just-created redirect that does not work yet is probably not broken.

**Email.** `hei@out-of-context.dev` forwards to `jari@itsellesi.fi`. Only that
address; catch-all is off. Cloudflare Email Routing has its own spam filter
(Email Routing → Settings) that can hold inbound mail silently. A Lu.ma sign-in
code once vanished this way: it was in neither the M365 inbox, junk, nor
quarantine, because Cloudflare held it upstream. If mail to `hei@` seems to be
missing, look there before anywhere downstream.

Changes to DNS, the redirect, or email routing take effect on the live domain
immediately and affect the site and Jari's mail. They are rarely needed; when
they are, say what you are changing and why, since a wrong CNAME takes the site
down for everyone until someone notices.

## Who can decrypt

`/.sops.yaml` lists the recipients (currently Jari's two machines) and contains
the steps for adding a maintainer as the project becomes community-owned; it is
the source for that procedure and is not repeated here. Two things behind those
steps are worth understanding rather than just following:

- Bare `age-keygen` prints the private key to stdout. In an agent session that
  means the key lands in the transcript, and transcripts and terminal logs are
  durable and often synced. Generating to a file avoids that.
- `sops updatekeys` re-encrypts one file to the current recipient list, once,
  when run. It is not a live ACL. Adding a recipient to `.sops.yaml` grants
  nothing until a current key holder runs it and commits the result, and
  removing one revokes nothing from history (see above; rotate the secret
  instead).

The same durability argument applies to decrypted values in general. A token
that scrolls past in a terminal is in the scrollback, the session transcript,
and possibly an issue or commit in a public repository. Extract only the key you
need with `sops -d --extract`, send output to `/dev/null` or a variable, and
never paste a decrypted value or an `AGE-SECRET-KEY-…` line anywhere that
persists.
