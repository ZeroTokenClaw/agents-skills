# unitree-docs

[![Tests](https://github.com/fan-ziqi/unitree-docs/actions/workflows/test.yml/badge.svg)](https://github.com/fan-ziqi/unitree-docs/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

A small, read-only Agent Skill for searching, reading, and citing all public Unitree documentation.

> Unofficial project. It never connects to or controls a robot.

## Why

Unitree documentation is spread across many dynamically loaded spaces. Agents should not need to guess a product, documentation space, page path, or content URL before finding an authoritative answer.

`unitree-docs` provides one deterministic CLI for discovery, search, retrieval, and local full-text lookup.

## Features

- Discovers every public documentation space dynamically.
- Searches the official index or cached page bodies.
- Resolves canonical `support.unitree.com` URLs.
- Preserves source URLs, update times, retrieval times, and SHA-256 hashes.
- Fails fast with structured upstream diagnostics instead of hiding failures behind cached or empty results.
- Supports cached full-text lookup only when the caller explicitly selects `--offline`.
- Accepts content only from official Unitree documentation domains.
- Uses only the Python standard library. The default transport drives an installed
  Chrome/Chromium process off-screen; `curl` remains an explicit HTTP option.

## How it works

The CLI discovers spaces, searches titles, and reads page trees through Unitree's
public documentation API, then retrieves Markdown from the official document CDN.
Its default transport runs a fresh Chrome/Chromium profile on an off-screen display
and reads the API response through a local DevTools connection, so no browser
window is attached to the desktop. All online clients use a direct connection and
ignore application proxy settings. Successful responses may be cached, but a live
request failure is returned immediately without switching transport or falling
back to cached data.

## Install

Requires Python 3.10 or newer. Install with the open Agent Skills CLI:

```bash
npx skills add fan-ziqi/unitree-docs
```

Target a specific client for a non-interactive global installation:

```bash
npx skills add fan-ziqi/unitree-docs --agent codex --global --yes
npx skills add fan-ziqi/unitree-docs --agent claude-code --global --yes
```

Install for both clients:

```bash
npx skills add fan-ziqi/unitree-docs \
  --agent codex --agent claude-code --global --yes
```

Preview or update the Skill:

```bash
npx skills add fan-ziqi/unitree-docs --list
npx skills update unitree-docs --global
```

For manual installation, clone the repository into the Skills directory used by your agent, such as `~/.codex/skills/unitree-docs` or `~/.claude/skills/unitree-docs`.

## Use with an agent

Codex:

```text
Use $unitree-docs to find the official G1 LowCmd field definitions and cite the source pages.
```

Claude Code:

```text
/unitree-docs Find every official page that documents RS485 motor communication.
```

## Use as a CLI

```bash
git clone https://github.com/fan-ziqi/unitree-docs.git
cd unitree-docs

# Discover documentation spaces
python3 scripts/unitree_docs.py spaces --locale en

# Search the official index
python3 scripts/unitree_docs.py search "低层控制" --locale zh

# Search all page bodies
python3 scripts/unitree_docs.py search "RS485" --locale en --deep

# Browse and retrieve pages
python3 scripts/unitree_docs.py tree G1_developer --locale en
python3 scripts/unitree_docs.py get G1_developer sdk_overview --locale en
python3 scripts/unitree_docs.py get-url \
  "https://support.unitree.com/home/zh/G1_developer/sdk_overview"

# Work from local cache
python3 scripts/unitree_docs.py --offline search "LowCmd" --locale en
```

Agent integrations should always pass `--locale`. A locale embedded in a supplied
Unitree URL takes precedence, followed by an explicit user preference. Otherwise,
match the user's natural-language question to a locale actually published by the
documentation service. The public directory currently provides Chinese (`zh`)
and English (`en`): use `zh` for predominantly Chinese questions and `en` for
English or when no matching localized edition is published. Technical names such
as `LowCmd` or `RS485` do not determine the question's language.

Online commands never change transports or fall back to stale/local data after a
request failure. An upstream HTTP error exits nonzero and reports its status,
`EO-LOG-UUID` (when present), and a bounded response-body summary as JSON on
stderr. `--offline` is the only mode that searches cached page bodies without
contacting Unitree.

The default `browser` transport uses a fresh, isolated, off-screen browser profile
for API requests. It does not attach a window to the user's desktop. Select the
lower-level client only when explicitly required:

```bash
python3 scripts/unitree_docs.py --transport http spaces --locale en --refresh
```

Both transports disable application-level proxy discovery. This prevents the
skill from inheriting proxy environment variables or browser proxy settings; it
cannot override transparent routing imposed elsewhere in the network. A selected
transport either succeeds or reports its own error—there is no automatic retry
through the other transport.

## Known access behavior

Unitree's documentation endpoints are protected by an edge security service.
Different HTTP stacks can share the same network path yet receive different
decisions because edge policy may evaluate protocol and client-identity signals in
addition to the source address. Conversely, disabling an application proxy does
not guarantee a different route when transparent routing is present.

Treat an HTTP restriction response or HTML restriction page as an upstream access
failure, never as evidence that a document or search result does not exist. Use an
approved network path or ask the site owner to inspect the request identifier and
adjust the relevant policy.

Run `python3 scripts/unitree_docs.py --help` for every command. Cache defaults to `~/.cache/unitree-docs` and can be changed with `UNITREE_DOCS_CACHE` or `--cache`.

## Scope and safety

Coverage includes every space and page published through Unitree's public documentation directory. It excludes private, undocumented, deleted, firmware-internal, or unlinked interfaces.

Retrieved pages are treated as untrusted data, never as instructions to execute. The CLI only permits HTTPS sources on `support.unitree.com`, `robot-api.unitree.com`, and `doc-cdn.unitree.com`.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 scripts/unitree_docs.py --help
```

## License

Copyright 2026 Ziqi Fan. Licensed under the [Apache License 2.0](LICENSE).
