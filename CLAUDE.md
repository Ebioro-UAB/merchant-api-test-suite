# merchant-api-test-suite

Reference client library and live test suite for the Ebioro Merchant API (public repository). Python and Node.js clients cover the full API surface and are tested live against the Ebioro test environment; Java, PHP, and C# clients exist only as HMAC-signing references. A Flask web UI lets you pick a language and exercise endpoints with your own credentials. Merchants integrating without one of the e-commerce plugins start here.

## Architecture
- `clients/python/ebioro_client.py` (primary), `clients/nodejs/ebioro-client.js` — maintained clients.
- `clients/{java,php,csharp}` — auth references only; core payment ops, not kept in sync with new endpoints.
- `main.py` — CLI + `--web` Flask interface (`web_interface.py`); `config.py` reads `EBIORO_API_KEY`, `EBIORO_API_SECRET`, `EBIORO_BASE_URL`.
- Signature: HMAC-SHA256 over `path + timestamp + method + body`, sent as `X-Digest-Key` / `X-Digest-Signature` / `X-Digest-Timestamp`.

## Dev commands
- Python ≥ 3.11, `uv sync` (lockfile `uv.lock`); `python main.py --web --port 5000` for the UI; `python -m pytest` / `python test_suite.py` for tests (live — needs test credentials).
- Node client: `node test_nodejs_client.js` with the same env vars.

## Gotchas
- **The signed path must equal the path actually sent on the wire, including the query string.** The Python client signs `parsed.path + ?query`; if you build URLs differently the server returns 401 with no further hint.
- **`EBIORO_BASE_URL` must be `scheme://host` with no path prefix** — a path-bearing base URL ends up inside the signed string and every request fails.
- **Body bytes must match the signed body.** JSON is serialised with `separators=(',', ':')` for both; pretty-printing one side breaks the signature.
- Path parameters are URL-encoded before use so an untrusted id cannot alter the request path — keep that when adding endpoints.
- The web UI binds to `127.0.0.1` on purpose: it holds API credentials in the session. Don't expose it on `0.0.0.0`.
- Auth headers are redacted in request logs; never add raw header logging.
- Keep the "Last verified" date in the README honest — update it only after a real live run.

<!-- BEGIN ebioro-non-negotiables v2 — master: Ebioro-UAB/documentation -->
## Ebioro non-negotiables

- **GitHub text hygiene — the KU corridor country is never named.** In any
  GitHub-visible text (commit messages, PR titles/bodies, reviews, issues,
  branch names, release notes, code/spec comments) write `KU` — never the
  country's name, demonym, or capital. The ISO code `CU` as functional data
  (string literals, catalog entries, `=== 'CU'` checks) and full-country
  datasets (countries.json, i18n locales) are fine. End-user UI strings may
  carry the real name; keep those literals minimal. Scrub old text on touch.
- **Never merge or push to `main`, never tag a production release, never deploy.**
  Open the PR and stop. Merges and deploys are human-only — no exception for
  "the review passed" or "it's just a patch bump". Never delete `main`,
  `master`, or `development`.
- **Never commit `.env` or any file containing a secret.** `.gitignore` covers
  `.env*` with `.env.example` as the only tracked variant. A secret that lands
  in git is leaked even after the file is removed — rotate it.
- **No AI attribution in git or GitHub text.** No `Co-Authored-By:` lines, no
  "Generated with …" footers in commits, PR bodies, or issues.
- **Error handling: `neverthrow` Result types. Never `try/catch`.**
- **TypeORM migrations: snake_case column identifiers only.** Quoting
  `"customerId"` preserves camelCase; TypeORM then queries `customer_id` and
  crashes at runtime. `build` does not catch it. This has cost two fix
  migrations already.
- **Follow the existing flow in code, not design docs or mockups.** Find the
  nearest equivalent already implemented and match it. Design notes are
  proposals.
- **Money paths**: integer stroops/cents, never floats. Idempotency keys on
  anything that moves money. Stellar sequence numbers fetched fresh. Never log
  or expose a signing key or an API secret.
- **Ebioro never holds keys for customer funds.** Before creating any key or
  account, ask whose funds it will hold. If a customer's, it cannot be a key
  Ebioro can use alone.
- **User-facing copy hides blockchain jargon.** "Payment reference", not
  "transaction hash". "Settled", not "confirmed on ledger N". "Network fee",
  not "XLM base fee". No signing-vendor names. It should read like a bank app,
  not a block explorer.
- **No regulatory claims** in user-facing text — not "licensed", "registered",
  "authorised", "MiCAR-compliant", or any variant. Route legal-sounding copy
  through Ebioro before merging.
- **Soft-delete only** (`deletedAt`). Never hard-delete.
- **Never skip pre-commit hooks** (`--no-verify`). Flag new dependencies in the
  PR description.
- **Never paste production data, customer PII, credentials, or KYC/AML content
  into an AI tool.** Anonymised or synthetic only.
<!-- END ebioro-non-negotiables v2 -->
