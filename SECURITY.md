# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this repository — or in the Ebioro Merchant API itself — please report it privately to:

**support@ebioro.com**

Please do **not** open a public GitHub issue for security reports.

Include as much detail as you can: affected file or endpoint, steps to reproduce, and potential impact. You will receive an acknowledgement, and we will keep you informed as the issue is investigated and resolved.

## Scope

This repository contains client libraries and a testing tool. Reports we especially care about:

- Anything that could expose API credentials (in code, logs, debug output, or HTTP responses)
- Weaknesses in the HMAC request-signing or webhook-verification implementations
- Vulnerabilities in the local web testing interface

## Guidelines for Using This Suite Safely

- Never commit credentials. All scripts read `EBIORO_API_KEY` / `EBIORO_API_SECRET` from the environment.
- Use test-environment keys for testing; rotate any key you suspect has been exposed.
- The web interface is for local use only — it binds to `127.0.0.1` by default and should never be exposed to a network.
