# Unitree documentation API contract

Unitree's documentation frontend separates discovery from page content:

| Capability | Official endpoint |
| --- | --- |
| Discover spaces | `GET https://robot-api.unitree.com/doc/spaces2?locale={locale}` |
| Search all spaces | `GET https://robot-api.unitree.com/doc/search?key={query}&locale={locale}` |
| Read a space tree | `GET https://robot-api.unitree.com/doc?space={space}&locale={locale}` |
| Read page Markdown | Use the `url` returned by a tree node; it must be on `doc-cdn.unitree.com` |

Successful API responses currently use `{"code": 100, "data": ...}`. Space and search responses may add grouping fields, so the CLI traverses them defensively instead of requiring a fixed product list.

Canonical browser routes use:

```text
https://support.unitree.com/home/{locale}/{space}/{path}
```

The locale must come from the requested URL, an explicit user preference, or the language of the user's question. Agent callers should pass it explicitly instead of relying on the CLI default. Match the question language to an edition published by the service. The current public directory exposes `zh` and `en`; use `zh` for predominantly Chinese questions and `en` for English or when no matching localized edition exists. Identifiers and code tokens do not determine the natural-language locale.

The API is protected by an edge service that may return nonstandard HTTP errors. The default transport uses an isolated off-screen Chrome/Chromium session. The explicit `http` transport uses system `curl` with HTTP/2 when available and uses the standard-library client only when `curl` is unavailable before a request. Every transport disables application proxy discovery. Once a transport makes a request, any HTTP or transport error is final: the CLI must not retry through another transport or fall back to stale/local data. Error output preserves the HTTP status, `EO-LOG-UUID` response header, and a bounded response-body summary. Never follow a page-content URL to a host outside Unitree's documented domains.

Edge policy can evaluate transport, protocol, client identity, and network-path signals independently. Consequently, different clients on the same host can receive different results, while transparent routing can remain in effect even when an application bypasses configured proxies. Treat a restriction response as an upstream access failure, not a missing document or empty search result.

Fresh cache entries may satisfy ordinary non-refresh reads without contacting the API. Cached page-body search is otherwise opt-in through `--offline`; this is an explicit source selection, not an error fallback. A refresh failure must never return an older catalog or page.

Cache entries retain the official source URL, canonical URL, page update time, retrieval time, and SHA-256 digest. Images, videos, archives, and executable examples are not mirrored.
