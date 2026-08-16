# AI-First CLI Design Principles

These principles apply to all CLI tools in this repo unless otherwise
mentioned. The primary caller is often an AI agent (Claude Code), not
a human typing in a terminal. Some conventions differ from
human-oriented software — follow these deliberately.

## 1. Strict input validation — no silent fixups

Validate strictly. Reject malformed, empty, whitespace-only, or otherwise
suspicious inputs with clear errors. Do not coerce, trim silently, or fall
back to defaults for obviously-wrong inputs. The AI caller is responsible
for sending well-formed input — surface problems as errors so it can fix
its output and retry.

Concretely:

- Empty or whitespace-only required arguments → error, not default
- Unknown options/flags → error, not ignored
- Out-of-range values → error, not coerced
- Report the actual invalid value in the error message — the AI can parse
  it and fix its input

Rationale: a lenient parser hides the caller's mistakes. An AI caller can
read the error, correct its output, and retry. Surfacing defects is
cheaper than papering over them.

## 2. Structured, parseable output

CLI tools should support machine-readable output alongside human-readable
output:

- Provide `--json` flag for structured JSON output where applicable
- Errors go to stderr, data to stdout — keep them separate
- Include metadata in output (status codes, URLs, counts) so the caller
  doesn't need to infer them
- Exit codes must be meaningful: 0 = success, 1 = user error, 2 = system error

Rationale: AI agents parse stdout programmatically. Mixed human/machine
output forces format sniffing.

### Logs: JSONL, one event per line

Logs (whether emitted to stderr, a file, or a journal) must be
**JSONL** — one self-contained JSON object per line, one event per
line. No multi-line records, no plain-text fallback in production
mode, no human-formatted prefixes wrapping JSON payloads. A grep, a
`jq`, or a `tail -F | jq 'select(...)'` is the canonical reading
tool.

Each log line carries **trace-shaped context** so logs are filterable
by the actors and resources involved:

- `user_id` / `tenant_id` whenever a request, job, or message is
  attributable to a user or tenant
- `trace_id` / `run_id` / `request_id` so multiple log lines from one
  logical operation can be correlated
- `message_id`, `receipt_id`, `attachment_id`, etc. — domain entity
  ids relevant to the event
- The originating subsystem/module (`target`, `component`) so cross-
  cutting filters work

Avoid embedding user-identifying context into free-form `message`
strings only — put it in dedicated fields. `grep '"user_id":42'` and
`jq 'select(.tenant_id == 7 and .level == "ERROR")'` should both work
without parsing prose.

Rationale: production debugging looks like "what happened to user
X's message Y" — that question is answered by structured filters,
not by reading prose. Per-line JSON also keeps logs streamable
(every line is a complete record) and resilient to truncation.

## 3. No interactive prompts

No `press y to continue`, no confirmation dialogs, no interactive Y/N
prompts, no TTY-dependent behavior. All commands must be non-interactive:
valid input succeeds, invalid input fails with a clear diagnostic and
non-zero exit.

- Destructive actions opted in via explicit flags (e.g. `--force`, `--yes`)
- One-shot execution: all inputs via arguments, output to stdout/stderr
- No pagers, no `less`, no `$EDITOR` invocations

Rationale: AI agents cannot respond meaningfully to interactive prompts.

## 4. Informative error messages

Error messages should contain enough context for the AI caller to
understand and fix the problem without additional investigation:

- Include the actual invalid value: `"Invalid target 'foobar'. Available: local, staging, demo, prod"`
- Include the expected format: `"URL must start with / or http"`
- For multi-step failures, indicate which step failed and why
- Stack traces and internal details go to stderr with `--verbose`, not by default

## 5. Composable commands

Design commands to work well in pipelines and with other tools:

- Fetch commands output to stdout by default (pipe-friendly)
- `--output FILE` as an alternative to stdout redirection
- Support stdin where it makes sense (e.g. reading URLs from a list); accept
  `-` as a filename to mean stdin
- Consistent flag naming across commands (`--target`, `--output`, `--json`)

## 6. CLI surface: noun-verb imperative, declarative `apply` as opt-in

Default to a **noun-verb imperative** surface: the resource comes first, the
action second (`<tool> job create ...`, `<tool> node list`, `<tool> job show
<id>`). This matches `gh` (`gh pr create`, `gh issue list`). For tools with
a single dominant resource (`cargo build`, `npm install`) a flat verb-first
surface is fine — don't invent a noun layer for a one-resource CLI.

A **declarative manifest** surface (`<tool> apply -f run.yaml`) belongs as an
*additional* entry point, not the primary one. Add it only when:

- The resource has enough fields that a file is easier than flags, **and**
- Convergent reconciliation (apply repeatedly → same state) is a real
  requirement, not aesthetic Kubernetes-mimicry

This restriction applies to the declarative verb `apply`, not to file-based
input generally. Imperative commands may and should accept `--file`,
`--body-file`, or `-` (stdin) when the payload is too large, structured,
or quoting-sensitive for flags (large markdown, JSON bodies, batch
creates). That is plain composition, not declarative state.

Rationale: AI callers compose CLI calls one at a time from a planning step;
each call should be self-describing in the argv. `gh pr create --title X
--body Y` is one transcript line the agent reads back to itself. A manifest
file splits intent across argv + file contents and adds a stat/parse step
for the agent. Manifests *are* the right answer when state-convergence is
the actual semantics (Terraform, kubectl) — just don't make them mandatory
when the operation is genuinely imperative.

## 7. Subcommand verbs: pick one set, no synonyms

Use exactly this verb vocabulary across all subcommands:

- `list` (zero-or-more, filterable) — never `ls`, `index`, `all`
- `show` (one, by id/slug) — never `get`, `view`, `describe`, `cat`
- `create` (new resource) — never `new`, `add`, `make`
- `update` (mutate existing) — never `edit`, `set`, `patch`, `modify`
- `delete` (remove) — never `rm`, `remove`, `destroy`

No verb may mean both "list many" and "show one" (the `kubectl get pods` /
`kubectl get pod foo` overload is exactly the ambiguity this rule rejects).

Exceptions need a written reason: `apply` (declarative convergence — see §6),
`exec` (executes something rather than mutating state), `skill` (companion-
skill installer — see §15), domain verbs that have no CRUD equivalent
(`commit`, `push`, `fetch` in git).

`update` semantics: by default a `update` command mutates only the fields
named on the command line (selective patch). A full-resource replace is
opt-in via `--replace-file` / `--replace` and must be documented as such.
This is patch semantics under one verb — there is no separate `patch`
command.

Rationale: AI callers guess subcommand names from training-set patterns.
Even though `get` dominates the training corpus, the cost of one wrong-guess
retry is much smaller than the cost of an inconsistent verb vocabulary
across our own tools. The agent learns the rule once per tool family and
hits it every time after. We bias toward strictness over corpus-familiarity.

## 8. Configuration precedence: flag > env > file > built-in default

For **persistent configuration values** (API URLs, profiles, default
targets, timeouts, credentials), precedence is resolved **per configuration
key**: an explicit flag for that key overrides the environment variable for
that same key, which overrides the config file's value for that key, which
overrides the built-in default. Two independent keys may legitimately come
from different layers; one layer does not displace another wholesale.

- Lists and maps **replace** rather than deep-merge — the highest-priority
  source for that key wins in full
- Env var name mirrors the flag: `--api-url` ↔ `<TOOL>_API_URL`
- Config file location is **inspectable at runtime** via `<tool> config
  path`. The path itself may follow platform conventions (XDG on Linux,
  `~/Library` on macOS, `%APPDATA%` on Windows) — what matters is that
  the caller never has to guess
- `<tool> config show --json` prints the effective resolved config and
  where each value came from (`source: "flag" | "env" | "file" |
  "default"`). **Secret-valued keys are redacted by default**
  (`value: "<redacted>", secret: true`) — explicit `--show-secrets` is
  required to dump them, and emits a warning to stderr

**Invocation-behavior flags** (`--json`, `--dry-run`, `--force`, `--yes`,
`--verbose`, `--output`, positional resource identifiers) are **not**
config-file settings unless explicitly documented per command. They are
per-invocation choices, not persistent configuration.

Rationale: AI callers need to reason about *why* a value is what it is —
"the agent set `--api-url` but the run still hit prod" is debuggable only
if the source is inspectable. Mirroring flag↔env names removes a lookup
step. Reference: `aws` documents this precedence and exposes it via
`aws configure list`; copy that pattern. The secret-redaction default is
non-negotiable: AI agents routinely paste tool output into transcripts and
issue comments.

## 9. Output format is fixed, not TTY-detected

Output format is determined **only** by explicit flags (`--json`,
`--output=text|json|jsonl`), never by `isatty()`. Given the same inputs
and external state, stdout/stderr formatting does not change merely because
stdout/stderr is or is not a terminal. No color, no table-vs-line
switching, no progress bars based on terminal detection.

- Default format is human-readable text; `--json` opts into structured
  output; `--output=jsonl` opts into streaming events (see §12)
- Color is off by default; only `--color=always` and `--color=never`
  exist — there is no `--color=auto` (it would be either dead syntax or
  TTY-sniffing under another name)
- Pagination is never automatic — see §3

Rationale: TTY-sniffing makes CLIs non-reproducible. The agent's local
invocation, the CI invocation, and the user's terminal invocation must all
produce the same bytes given the same flags, or transcripts and tests
diverge from reality. `gh` and `kubectl` both ship TTY-detection that has
bitten users; avoid the trap.

## 10. Schema versioning, errors, warnings, and deprecation

JSON output is a versioned API surface, not free-form. Treat it
accordingly:

- Every `--json` payload (top-level and event-level for streaming) carries
  a `schema_version` field (integer, monotonic)
- Additive changes (new fields) do not bump the version. Breaking changes
  do: removing/renaming fields, changing field types, changing enum
  semantics, making optional fields required, changing nullability,
  changing event ordering guarantees, or changing the meaning of an
  existing field
- Every CLI implements `<tool> version --json` returning at least
  `{version, commit, schema_version, supported_schemas}` so the agent can
  detect drift between trained expectations and reality

**Error envelope under `--json`.** Failures emit a structured error
object to **stderr** (not stdout — see §2):

```json
{
  "schema_version": 1,
  "error": {
    "code": "invalid_target",
    "message": "Invalid target 'foobar'. Available: local, staging, demo, prod",
    "invalid_value": "foobar",
    "expected": ["local", "staging", "demo", "prod"]
  }
}
```

**Warnings are not errors.** Under `--json`, non-fatal warnings (e.g.
deprecation) belong in a `warnings: []` array inside the **stdout** JSON
payload — not on stderr. This keeps stderr a fatal-only channel and avoids
forcing the agent to format-sniff. In text mode, warnings go to stderr
prefixed with `warning: ` so they're trivially distinguishable.

**Deprecation policy.** Deprecated flags and commands emit a structured
warning on every use, naming the removal version (or commit/tag window if
the tool has no semver releases). Suppress with
`<TOOL>_NO_DEPRECATION_WARNINGS=1`. Deprecations live for at least one
release window before removal. A deprecation alone never changes exit
code.

Rationale: agents pin against observed CLI behavior. Without a schema
version, the agent can't tell "field missing because absent" from "field
missing because renamed in v2". The error envelope makes failure parseable
the same way success is parseable.

## 11. Dry-run, idempotency, and retry safety

**Dry-run.** Every command that creates, updates, or deletes a resource
supports `--dry-run`. Dry-run:

- Performs all input validation and read-only checks that the real run does
- Emits the planned mutations using a **planning envelope** distinct from
  the real-run result envelope:
  ```json
  {
    "schema_version": 1,
    "dry_run": true,
    "would": [
      {"action": "create", "resource": "run", "input": {...},
       "known_effects": {"status": "would_create"},
       "unknown_until_apply": ["id", "created_at", "url"]}
    ]
  }
  ```
- Never partially applies — either prints the full plan or errors

If a truthful dry-run is not possible (token rotation, OAuth login,
race-sensitive ops, commands whose result depends on server-generated
state the dry-run cannot reserve), the command **fails explicit**:
exit 1 with `{schema_version, error: {code: "dry_run_unsupported",
reason: "..."}}`. A fake dry-run is worse than no dry-run — it gives
the AI caller false confidence.

**Idempotency and retry safety.** AI callers retry. The retry path must
not turn a successful first call into a confusing failure.

- For network-backed `create`, **support a caller-supplied idempotency
  key** (`--idempotency-key <opaque>`): the second call with the same key
  returns the original result, not a conflict. Echo the key in the JSON
  output. Recommend this pattern wherever the backend supports it (Stripe,
  AWS, and most modern APIs do)
- Where idempotency keys are not available, offer symmetric opt-ins:
  `--if-not-exists` on `create` (succeed silently if it already exists,
  return the existing resource) and `--if-exists` on `delete` (succeed
  silently if absent)
- `delete` of a missing resource defaults to a clear error, but the
  `--if-exists` flag exists for the AI retry use case
- `update` is selective by default (only fields named — see §7); a retried
  update is naturally idempotent

The point is the agent should always have a way to say "I don't care
whether you already did this; converge to this state and tell me the
final result." Different commands offer that affordance through
different mechanisms; offer at least one.

Rationale: "did my last call succeed?" must be answerable without
ambiguity-prone error-message string matching. Idempotency keys are the
industry-standard answer where the network is involved; the symmetric
flags are the local-tool answer.

## 12. Long-running operations: streaming events and progress queries

Operations that take more than a few seconds need a way for the caller —
human or agent — to know they are still alive and how far along they are.
The format is part of the command contract, not a runtime decision.

**Streaming mode.** A long-running command declares its output format up
front:

- `--output=jsonl` (or `--jsonl`) emits one JSON event per line to stdout,
  each carrying `schema_version`, `event` (`"progress"`, `"log"`,
  `"result"`, `"error"`, `"cancelled"`), and a monotonic `seq`
- Terminal events are mutually exclusive: exactly one of `result`,
  `cancelled`, or `error` ends the stream. The absence of a terminal
  event means the process crashed mid-stream; consumers treat that as
  `error`
- `--json` (single document) is forbidden for primarily long-running
  commands — pick `--output=jsonl` or design the command around a
  separate progress query (below). A command must not silently switch
  format based on elapsed runtime
- Text mode prints brief one-line-per-step progress to stderr — **never**
  spinners, ANSI cursor movement, or carriage-return-overwrite progress
  bars. These rules apply in both human and agent modes; we deliberately
  forfeit the spinner UX for format predictability

**Progress query.** For commands that run as a daemon, background job, or
detached process — where the caller is not streaming the output — every
such command exposes a paired progress query:

- `<tool> <noun> show <id>` (or `<tool> <noun> status <id>`) returns the
  current state, `schema_version`, the last `seq` emitted, and a recent
  event window
- Agents poll this instead of waiting on a stream. Human callers run it
  on demand

**Signals.** The streaming process traps both `SIGINT` and `SIGTERM`
(AI sandbox timeouts use `SIGTERM`, terminal Ctrl-C uses `SIGINT`) and
emits a final `{"event": "cancelled"}` event before exit when feasible.
Exit codes for cancellation: **130 for SIGINT, 143 for SIGTERM**. These
are declared exceptions to §2's `0/1/2` policy; document them in the
tool's `--help`.

Rationale: AI callers read incrementally and need to distinguish "still
working" from "hung". A spinner is invisible to a subprocess reader; a
JSONL event is parseable, filterable, and survives `tee` to a log. For
background jobs the agent can't stream, the progress-query subcommand is
the same answer in pull form.

## 13. Large outputs go to a file the agent can query

A `list` command that returns 10 000 rows blows out an AI agent's context
window. The conventional answer in human CLIs is paging or
`--limit`/`--cursor`; both push complexity onto the caller and force
repeated calls. The AI-first answer is different:

**Default to inline output for small results, and offer
`--output FILE.jsonl` or `--output FILE.db` (SQLite) for results that
might not be small.** When writing to a file:

- JSONL: one record per line, each carrying `schema_version` — agent
  reads with `jq`, `grep`, `head`, `wc -l`
- SQLite: structured schema with primary keys and indexes the command
  documents — agent reads with `sqlite3 file.db "SELECT ... WHERE ..."`
- The command prints to stdout (or `--json` stdout) only metadata about
  the file: path, count, schema_version, optionally a SQL/jq query hint
  the agent can use as a starting point

This replaces traditional pagination entirely for the AI use case. The
agent never gets the full result blob into context; it issues targeted
queries against the file. For genuinely huge results, SQLite is
preferred (indexed lookups, `LIMIT/OFFSET`, joins across multiple
exports). For moderate streaming results, JSONL is enough.

`--limit` is still useful as a guardrail against accidentally requesting
huge inline output, but it is not the primary mechanism.

Rationale: AI context is the binding resource. Twenty agent turns asking
`tool list --cursor abc123` is worse than one turn that writes a SQLite
file and three turns of focused SQL. The standard `--output FILE` from
§5 already exists; this section makes it the recommended pattern for any
result that might be large.

## 14. `--help` is agent-first, structured, and drill-down

`--help` is the first thing an AI agent reads when it doesn't know a
command. Optimize it for that reader. Humans benefit too.

- **Top-level `<tool> --help`** lists subcommands with one-line
  descriptions, and the small set of global flags (`--json`,
  `--output`, `--verbose`, `--version`). It does **not** dump every
  flag of every subcommand
- **Drill-down**: `<tool> <subcommand> --help` is the next layer —
  full flag list, accepted values, defaults, the env-var name for each
  flag (per §8), and exit-code semantics. Further nesting works the
  same way: `<tool> job create --help` is independent of
  `<tool> job --help`
- **Machine-readable help**: every `<tool> ... --help` accepts `--json`
  and emits a structured description of subcommands, flags, args,
  defaults, env-var mappings, accepted-value enums, deprecation status,
  and the `schema_version` of the help payload itself
- **Examples**: each subcommand's help includes at least one working
  example as text (humans), and an `examples: []` array of
  `{description, argv}` pairs under `--json` (agents). Examples are
  copy-pasteable and use the canonical verb vocabulary from §7

Rationale: agents lookup a command, fail, retry — this loop is much
shorter if the help they read is structured (no prose scraping) and
drilled (no flag-firehose). For humans, the same drill-down is just good
UX. The schema-versioned `--help --json` is what makes §10's "schema as
API surface" promise complete: now the *surface itself* is queryable, not
just the data.

## 15. `skill` subcommand: install companion AI-skills

Every CLI ships with a `skill` subcommand whose job is to install
Claude-Code-style skills (`SKILL.md` files with frontmatter) that teach
an AI agent how to drive this CLI in real workflows. The skill files are
the agent's *operating manual* for the tool — distinct from `--help`
(reference) and the schema (data shape).

- `<tool> skill list` — shows available skills shipped with this tool,
  one-line descriptions
- `<tool> skill install [<name>]` — copies the skill(s) into the active
  Claude Code installation (`~/.claude/skills/` by default,
  `--target <dir>` for other agent runtimes); installs all when no name
  given
- `<tool> skill show <name> --json` — prints the skill content without
  installing, so an agent can read it inline if needed

The skills themselves live alongside the tool's source (in-repo) so they
version with the binary. The CLI is responsible for keeping skill text
and CLI surface in sync (a tool whose `skill list` references a removed
flag is a release-blocker, same as a broken `--help`).

Rationale: `--help` tells an agent *what* a command does; a skill tells
it *when and how to use it in a multi-step workflow* — when to combine
with which other commands, which gotchas to avoid, what the success
criteria look like. The skill is also the natural place to encode
non-obvious idioms (e.g. "always pass `--output FILE.jsonl` when the
result might exceed N rows" — §13). Shipping skills from the tool itself
means every agent that installs the tool gets the operating manual in
one step, rather than asking the agent to discover patterns by trial.

## 16. `skill print`: stream skill content without installing

Pair the installer of §15 with a print subcommand that streams the
canonical skill text to stdout:

- `<tool> skill print <name>` — writes the `SKILL.md` (frontmatter +
  body) for `<name>` to stdout, exit 0. Unknown name → §10 error
  envelope on stderr, exit 1
- `<tool> skill print <name> --json` — emits a structured payload
  `{schema_version, name, cli_version, schema_version_skill, content,
  path_in_repo}` so the agent can route the body separately from the
  metadata
- Output is byte-identical to what `skill install` would have written
  to disk for that name. There is no "rendered" vs "raw" distinction
- No side effects: no file writes, no network. Print is the read-only
  twin of install

This is the natural complement to `<tool> skill install` (§15):
*install* persists the operating manual on the agent's runtime so it
loads on every future session; *print* streams it once into the
current conversation. Use install for the agent's own machine; use
print in CI, sandboxes, ad-hoc remote shells, or when the agent
discovers the tool mid-task and needs the workflow guidance
immediately without modifying the runtime.

Concretely, an agent that has just learned `<tool>` exists and wants
to drive it correctly runs `<tool> skill print <main-skill>` once and
reads the body into its working context — no install step, no
filesystem mutation, and (by §17) the version it gets matches the
binary it is about to invoke.

Rationale: `skill install` is the right answer when the skill should
persist across sessions, but it requires write access to a runtime
directory the agent may not own (CI runners, locked sandboxes, remote
shells). `skill print` makes the same operating manual available as
pure stdout — composable with `cat`, `jq`, `tee`, and the agent's
own context-loading mechanisms. It also gives `<tool> skill install`
a trivial reference implementation: install is `print | write-to-disk`.

## 17. Skill–CLI version synchronization

The companion skill of §15/§16 is a versioned artifact. Its workflow
guidance, flag names, and example invocations must match the CLI
surface that will execute them — a skill that references a removed
flag is no better than a broken `--help`. Treat skill text and CLI
surface as one release unit.

- **Frontmatter version fields.** Every shipped `SKILL.md` declares
  two versions in its frontmatter:
  - `cli_version:` — the CLI release the skill body was written
    against (e.g. `cli_version: "0.6.3"`)
  - `schema_version:` — the skill-format version (the §10 contract
    applied to the skill payload itself, so agents can detect breaking
    changes to the skill format independently of the tool's data
    schema)
- **`skill print` is version-pinned to the running binary.** `<tool>
  skill print <name>` always returns the skill that ships *with the
  currently installed binary* — i.e. its `cli_version` equals
  `<tool> --version`. It never reads a stale copy from disk. If the
  binary cannot resolve a matching skill (corrupt install, partial
  upgrade), it errors with `{code: "skill_version_mismatch"}` rather
  than serving an older copy
- **`skill install` warns on drift.** `<tool> skill install <name>`
  compares the target directory's existing skill (if any) against the
  CLI's bundled version. If the on-disk `cli_version` is older than
  the running binary's version, install proceeds but emits a §10
  warning naming both versions; if it is *newer* (agent upgraded the
  skill ahead of the binary), install errors unless `--force` is
  passed
- **`<tool> version --json` exposes the contract.** Per §10 the
  version payload already carries `version`, `commit`, and
  `schema_version`. Extend it with `skills: [{name, cli_version,
  schema_version}]` so the agent can audit skill freshness against
  the running binary in one call, no filesystem walk needed
- **CI gate.** A release pipeline that ships a CLI surface change
  (added/removed/renamed flags, changed verb vocabulary, changed
  `--help --json` payload) must regenerate or bump the bundled
  skill(s) in the same commit. The check is mechanical: diff the
  `--help --json` snapshot against the previous release, and fail the
  build if any skill's `cli_version` is older than the new binary's
  version. This is the same release-blocker discipline §15 already
  imposes on `skill list`

The principle is one-way: the **binary is the source of truth, the
skill follows it.** Skills never drift ahead of the binary in
production; they may lag by one bump only inside an active development
loop, never across a release tag.

Rationale: an agent that reads a stale skill will compose calls
against flags that no longer exist, then debug against a `--help`
that contradicts the skill — a worst-case loop that burns context and
produces wrong commits. Pinning `skill print` to the running binary
removes the discrepancy at read time; the frontmatter version fields
let the agent reason explicitly about which release it is following;
the install-time warning catches the offline case where the agent
installed a skill once and the CLI has since moved on. Together these
make "is my workflow guidance current?" a one-call question instead
of a multi-step audit.

## 18. `doctor` subcommand: read-only self-diagnostic

Every CLI ships a `doctor` subcommand that runs the tool's full
internal self-check and reports each check's status. Doctor is the
agent's first move when a command fails for non-obvious reasons —
"is the install broken, is the data corrupt, is the config wrong, is
a dependency missing?" — and it must answer that question without the
agent having to know which subsystem to interrogate.

- `<tool> doctor` — runs all checks; one human-readable line per
  check (`OK`, `WARN`, `FAIL` + short message) and a final summary
  `summary: N ok, M warn, K fail`
- `<tool> doctor --json` — emits the §10 structured form:
  ```json
  {
    "schema_version": 1,
    "checks": [
      {"id": "schema.issues", "status": "ok",
       "message": "12 issues validated"},
      {"id": "skill.sync", "status": "warn",
       "message": "skill 'issue' is cli_version 0.6.2, binary is 0.6.3",
       "fix_suggestion": "tool skill install issue --force"}
    ],
    "summary": {"ok": 11, "warn": 1, "fail": 0}
  }
  ```
- Exit code: **0** if all checks are `ok` or `warn` only; **1** if any
  check is `fail`. Deprecation-style warnings never flip the exit code
  (consistent with §10)
- **Read-only by default.** Doctor never mutates state. The corrective
  twin is `<tool> doctor --fix`, which runs the same checks and then
  applies the safe subset of `fix_suggestion`s. `--fix` is opt-in per
  invocation, never the default, and emits the planning envelope from
  §11 first if combined with `--dry-run`

The canonical set of check categories is small and stable:

- **Schema validation** — every on-disk data file the tool owns
  validates against its declared schema (e.g. `issuectl doctor` walks
  `issues/*/item.md` frontmatter against `issues/.schema.yaml`)
- **Dependencies** — every binary the tool shells out to is on `PATH`
  at a supported version; missing or out-of-range versions
  `FAIL` with `fix_suggestion` naming the install command
- **Skill sync** — for every installed companion skill (§17), the
  on-disk `cli_version` matches the running binary; mismatch is
  `WARN` with `<tool> skill install <name> --force` as the suggestion
- **Configuration integrity** — every required key from §8 resolves
  (flag/env/file/default), no orphan references (e.g. a config
  pointing at a deleted profile), no secret-shaped values stored in
  non-secret keys
- **Data integrity** — domain-specific structural checks: orphan
  files, broken cross-references, stale lock/marker files, indices
  that disagree with the underlying records

Every check has a stable `id` (so the agent can pin which checks it
expects to see), a `status`, a one-line `message` naming the actual
state observed, and — for `WARN`/`FAIL` — a `fix_suggestion` that is
either a concrete command the agent can run, or a brief diagnostic
hint when no automated fix is safe.

Rationale: AI agents debug by hypothesis testing, and `doctor` is the
cheapest hypothesis: "is the tool itself healthy?" One command, one
structured answer, with per-check `id`s the agent can correlate
against the failure it just saw. The read-only default matters
because the agent will run `doctor` reflexively after errors — it
must not have side effects in that loop. The `--fix` twin exists for
the explicit "yes, apply the suggested repairs" case, separated by a
flag so neither use accidentally triggers the other. The structured
output makes `doctor` composable with the rest of the agent's
toolchain (`jq '.checks[] | select(.status == "fail")'`), the same
way every other §10-conformant payload is.
