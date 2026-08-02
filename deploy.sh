#!/usr/bin/env bash
#
# deploy.sh — Build and deploy out-of-context.dev to Cloudflare Pages
#
# Usage:
#   ./deploy.sh
#
# Requires: zola, wrangler (or npx), curl, jq, sops
# Auth:     CLOUDFLARE_API_TOKEN env var, or the SOPS-encrypted file
#           operations/secrets/cloudflare.enc.yaml (key: api_token)
#
# The very first deploy creates the Cloudflare Pages project and serves it at
# https://out-of-context.pages.dev. Attaching the custom domain out-of-context.dev
# is a separate one-time step (see operations/secrets/AGENTS.md).

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="out-of-context"     # Cloudflare Pages project name
BRANCH="main"
CF_API="https://api.cloudflare.com/client/v4"
ZONE="out-of-context.dev"
SECRETS_FILE="$SCRIPT_DIR/operations/secrets/cloudflare.enc.yaml"

# ---------------------------------------------------------------------------
# Colors & output helpers
# ---------------------------------------------------------------------------
if [[ -t 1 ]]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
    BLUE='\033[0;34m'; BOLD='\033[1m'
    NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; BLUE=''; BOLD=''; NC=''
fi

info()   { echo -e "${BLUE}info${NC}  $*"; }
ok()     { echo -e "${GREEN} ok ${NC}  $*"; }
warn()   { echo -e "${YELLOW}warn${NC}  $*" >&2; }
err()    { echo -e "${RED}fail${NC}  $*" >&2; }

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------
check_deps() {
    local missing=()
    for cmd in zola curl jq; do
        command -v "$cmd" &>/dev/null || missing+=("$cmd")
    done
    if ! command -v wrangler &>/dev/null && ! command -v npx &>/dev/null; then
        missing+=("wrangler")
    fi
    if (( ${#missing[@]} > 0 )); then
        err "Missing required tools: ${missing[*]}"
        echo "  zola:     brew install zola"
        echo "  wrangler: npm install -g wrangler   (or use npx, auto-detected)"
        echo "  curl/jq:  brew install curl jq"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# API token loading (env var wins; else SOPS)
# ---------------------------------------------------------------------------
load_token() {
    if [[ -n "${CLOUDFLARE_API_TOKEN:-}" ]]; then
        info "Using CLOUDFLARE_API_TOKEN from environment"
        return
    fi
    if [[ -f "$SECRETS_FILE" ]] && command -v sops &>/dev/null; then
        info "Loading API token from SOPS"
        CLOUDFLARE_API_TOKEN=$(sops -d --extract '["api_token"]' "$SECRETS_FILE")
        if [[ "$CLOUDFLARE_API_TOKEN" == REPLACE_WITH_REAL* || -z "$CLOUDFLARE_API_TOKEN" ]]; then
            err "The Cloudflare token is still the placeholder."
            echo "  Put the real token in place, then re-run:"
            echo "    sops $SECRETS_FILE      # set api_token: <real token>"
            exit 1
        fi
        export CLOUDFLARE_API_TOKEN
        return
    fi
    err "No Cloudflare API token found."
    echo "  export CLOUDFLARE_API_TOKEN='...'   or   sops $SECRETS_FILE"
    exit 1
}

# ---------------------------------------------------------------------------
# Account ID resolution (env → SOPS account_id → zone lookup → wrangler auto)
# ---------------------------------------------------------------------------
resolve_account_id() {
    if [[ -n "${CLOUDFLARE_ACCOUNT_ID:-}" ]]; then
        return
    fi
    # Optional account_id pinned inside the secrets file
    if [[ -f "$SECRETS_FILE" ]] && command -v sops &>/dev/null; then
        local pinned
        pinned=$(sops -d --extract '["account_id"]' "$SECRETS_FILE" 2>/dev/null || true)
        if [[ -n "$pinned" ]]; then
            CLOUDFLARE_ACCOUNT_ID="$pinned"; export CLOUDFLARE_ACCOUNT_ID
            ok "Account ID (from secrets): $CLOUDFLARE_ACCOUNT_ID"
            return
        fi
    fi
    # Fall back to resolving from the zone (works only once the domain is a
    # Cloudflare zone). Non-fatal: wrangler can auto-detect a single account.
    info "Resolving account ID from zone: $ZONE"
    local response
    response=$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        "$CF_API/zones?name=$ZONE" || true)
    CLOUDFLARE_ACCOUNT_ID=$(echo "$response" | jq -r '.result[0].account.id // empty')
    if [[ -n "$CLOUDFLARE_ACCOUNT_ID" ]]; then
        export CLOUDFLARE_ACCOUNT_ID
        ok "Account ID: $CLOUDFLARE_ACCOUNT_ID"
    else
        warn "Could not resolve account ID from zone '$ZONE' (domain not on"
        warn "Cloudflare yet?). Letting wrangler auto-detect the account."
    fi
}

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
build_site() {
    info "Building site with Zola..."
    cd "$SCRIPT_DIR"
    zola build
    ok "Site built → public/"
}

# ---------------------------------------------------------------------------
# Deploy
# ---------------------------------------------------------------------------
deploy_site() {
    info "Deploying to Cloudflare Pages (project: ${BOLD}$PROJECT_NAME${NC}, branch: ${BOLD}$BRANCH${NC})"
    cd "$SCRIPT_DIR"
    local wr=(wrangler)
    command -v wrangler &>/dev/null || wr=(npx --yes wrangler)
    "${wr[@]}" pages deploy public/ --project-name "$PROJECT_NAME" --branch "$BRANCH"
    ok "Deployed to Cloudflare Pages"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    check_deps
    load_token
    resolve_account_id
    echo ""
    build_site
    echo ""
    deploy_site
    echo ""
    ok "Deployed. Pages URL: ${BOLD}https://$PROJECT_NAME.pages.dev${NC}"
    ok "Custom domain (once attached): ${BOLD}https://$ZONE${NC}"
}

main "$@"
