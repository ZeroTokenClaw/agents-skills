#!/usr/bin/env python3
"""Read-only CLI for every official Unitree documentation space."""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import http.client
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_ROOT = "https://robot-api.unitree.com/doc"
SUPPORT_HOST = "support.unitree.com"
CDN_HOST = "doc-cdn.unitree.com"
ALLOWED_HOSTS = {SUPPORT_HOST, "robot-api.unitree.com", CDN_HOST}
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
DEFAULT_TTL = 21_600
CURL_STATUS_MARKER = b"\n__UNITREE_HTTP_STATUS__:"
BROWSER_START_TIMEOUT = 10.0
BROWSER_REQUEST_TIMEOUT = 30.0
PROXY_ENVIRONMENT_KEYS = {
    "all_proxy",
    "http_proxy",
    "https_proxy",
    "no_proxy",
}


class DocsError(RuntimeError):
    """A documentation access error that can be serialized by the CLI."""

    error_code = "docs_error"

    def to_dict(self) -> dict[str, Any]:
        return {"error": self.error_code, "message": str(self)}


class UpstreamError(DocsError):
    """A structured failure returned by an official Unitree endpoint."""

    error_code = "upstream_error"

    def __init__(
        self,
        url: str,
        *,
        transport: str,
        reason: str | None = None,
        http_status: int | None = None,
        eo_log_uuid: str | None = None,
        response_summary: str | None = None,
    ):
        self.url = url
        self.transport = transport
        self.reason = reason
        self.http_status = http_status
        self.eo_log_uuid = eo_log_uuid
        self.response_summary = response_summary

        details: list[str] = []
        if http_status is not None:
            details.append(f"HTTP {http_status}")
        if eo_log_uuid:
            details.append(f"EO-LOG-UUID {eo_log_uuid}")
        if reason:
            details.append(reason)
        if response_summary and not details:
            details.append("upstream returned an error response")
        suffix = "; ".join(details) or "unknown upstream failure"
        super().__init__(f"Unitree request failed for {url} via {transport}: {suffix}")

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result.update({"url": self.url, "transport": self.transport})
        optional = {
            "http_status": self.http_status,
            "eo_log_uuid": self.eo_log_uuid,
            "response_summary": self.response_summary,
            "reason": self.reason,
        }
        result.update({key: value for key, value in optional.items() if value is not None})
        return result


def response_summary(body: bytes | str, limit: int = 500) -> str | None:
    """Reduce an HTML/text error body to a bounded diagnostic summary."""
    text = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else body
    text = re.sub(r"(?is)<style\b[^>]*>.*?</style>", " ", text)
    text = re.sub(r"(?is)<!--.*?-->", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    if not text:
        return None
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def header_value(headers: bytes, name: str) -> str | None:
    prefix = name.casefold()
    values: list[str] = []
    for line in headers.decode("iso-8859-1", errors="replace").splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip().casefold() == prefix:
            values.append(value.strip())
    return values[-1] if values else None


def parse_curl_output(output: bytes) -> tuple[bytes, int | None, bytes]:
    """Separate curl's dumped response headers, body, and HTTP status marker."""
    payload, marker, status_tail = output.rpartition(CURL_STATUS_MARKER)
    if not marker:
        return output, None, b""
    status_token = status_tail.splitlines()[0].strip()
    status = int(status_token) if status_token.isdigit() else None

    position = 0
    final_headers = b""
    while payload[position:].startswith(b"HTTP/"):
        remaining = payload[position:]
        separators = [
            (remaining.find(delimiter), delimiter)
            for delimiter in (b"\r\n\r\n", b"\n\n")
            if remaining.find(delimiter) >= 0
        ]
        if not separators:
            break
        header_end, delimiter = min(separators, key=lambda item: item[0])
        block = remaining[:header_end]
        first_line = block.splitlines()[0] if block else b""
        if not re.match(rb"^HTTP/\S+\s+\d{3}(?:\s|$)", first_line):
            break
        final_headers = block
        position += header_end + len(delimiter)

    return payload[position:], status, final_headers


def find_chrome() -> str | None:
    explicit = os.environ.get("UNITREE_DOCS_CHROME")
    if explicit:
        return explicit
    for candidate in (
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "chrome",
    ):
        executable = shutil.which(candidate)
        if executable:
            return executable
    return None


def dict_header(headers: dict[str, Any], name: str) -> str | None:
    expected = name.casefold()
    for key, value in headers.items():
        if key.casefold() == expected:
            return str(value)
    return None


def direct_environment() -> dict[str, str]:
    """Return a child-process environment with proxy variables removed."""
    return {
        key: value
        for key, value in os.environ.items()
        if key.casefold() not in PROXY_ENVIRONMENT_KEYS
    }


class DevToolsConnection:
    """Minimal standard-library WebSocket client for local Chrome DevTools."""

    def __init__(self, url: str):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "ws" or parsed.hostname not in {"127.0.0.1", "localhost"}:
            raise DocsError("refusing a non-local Chrome DevTools endpoint")
        if parsed.port is None:
            raise DocsError("Chrome DevTools endpoint has no port")

        self.socket = socket.create_connection(
            (parsed.hostname, parsed.port), timeout=BROWSER_REQUEST_TIMEOUT
        )
        self.buffer = bytearray()
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        target = parsed.path or "/"
        if parsed.query:
            target += "?" + parsed.query
        request = (
            f"GET {target} HTTP/1.1\r\n"
            f"Host: {parsed.hostname}:{parsed.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).encode("ascii")
        self.socket.sendall(request)
        response = self._read_headers()
        first_line = response.splitlines()[0] if response else b""
        if b" 101 " not in first_line:
            self.close()
            raise DocsError(
                "Chrome DevTools WebSocket handshake failed: "
                + first_line.decode("iso-8859-1", errors="replace")
            )
        expected_accept = base64.b64encode(
            hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")
            ).digest()
        ).decode("ascii")
        if expected_accept.casefold() not in response.decode(
            "iso-8859-1", errors="replace"
        ).casefold():
            self.close()
            raise DocsError("Chrome DevTools WebSocket handshake was not authenticated")

    def _read_headers(self) -> bytes:
        while b"\r\n\r\n" not in self.buffer:
            chunk = self.socket.recv(4096)
            if not chunk:
                raise DocsError("Chrome closed the DevTools handshake")
            self.buffer.extend(chunk)
        headers, _, remaining = bytes(self.buffer).partition(b"\r\n\r\n")
        self.buffer = bytearray(remaining)
        return headers

    def _read_exact(self, size: int) -> bytes:
        while len(self.buffer) < size:
            chunk = self.socket.recv(max(4096, size - len(self.buffer)))
            if not chunk:
                raise DocsError("Chrome closed the DevTools connection")
            self.buffer.extend(chunk)
        result = bytes(self.buffer[:size])
        del self.buffer[:size]
        return result

    def _send_frame(self, payload: bytes, opcode: int = 0x1) -> None:
        mask = os.urandom(4)
        length = len(payload)
        if length < 126:
            header = struct.pack("!BB", 0x80 | opcode, 0x80 | length)
        elif length <= 0xFFFF:
            header = struct.pack("!BBH", 0x80 | opcode, 0x80 | 126, length)
        else:
            header = struct.pack("!BBQ", 0x80 | opcode, 0x80 | 127, length)
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self.socket.sendall(header + mask + masked)

    def _read_frame(self) -> tuple[bool, int, bytes]:
        first, second = self._read_exact(2)
        finished = bool(first & 0x80)
        opcode = first & 0x0F
        masked = bool(second & 0x80)
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self._read_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._read_exact(8))[0]
        mask = self._read_exact(4) if masked else b""
        payload = self._read_exact(length)
        if masked:
            payload = bytes(
                value ^ mask[index % 4] for index, value in enumerate(payload)
            )
        return finished, opcode, payload

    def send_json(self, value: dict[str, Any]) -> None:
        self._send_frame(json.dumps(value, separators=(",", ":")).encode("utf-8"))

    def receive_json(self, timeout: float) -> dict[str, Any]:
        self.socket.settimeout(timeout)
        fragments: list[bytes] = []
        started = False
        while True:
            finished, opcode, payload = self._read_frame()
            if opcode == 0x8:
                raise DocsError("Chrome closed the DevTools connection")
            if opcode == 0x9:
                self._send_frame(payload, opcode=0xA)
                continue
            if opcode == 0x1:
                fragments = [payload]
                started = True
            elif opcode == 0x0 and started:
                fragments.append(payload)
            else:
                continue
            if finished:
                try:
                    value = json.loads(b"".join(fragments).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    raise DocsError(f"invalid Chrome DevTools message: {error}") from error
                if not isinstance(value, dict):
                    raise DocsError("invalid Chrome DevTools message type")
                return value

    def close(self) -> None:
        sock = getattr(self, "socket", None)
        if sock is None:
            return
        try:
            self._send_frame(b"", opcode=0x8)
        except OSError:
            pass
        sock.close()
        self.socket = None


class BrowserTransport:
    """Retrieve official responses through an isolated, off-screen Chrome session."""

    def __init__(self, executable: str | None = None):
        self.executable = executable or find_chrome()
        if not self.executable:
            raise DocsError(
                "browser transport requires Chrome or Chromium; set "
                "UNITREE_DOCS_CHROME when it is not on PATH"
            )
        self.profile = tempfile.TemporaryDirectory(prefix="unitree-docs-chrome-")
        self.process: subprocess.Popen[bytes] | None = None
        self.connection: DevToolsConnection | None = None
        self.next_id = 0
        self.events: list[dict[str, Any]] = []
        try:
            self._start()
        except Exception:
            self.close()
            raise

    @staticmethod
    def _available_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.bind(("127.0.0.1", 0))
            return int(listener.getsockname()[1])

    def _launch_spec(self, port: int) -> tuple[list[str], dict[str, str]]:
        command = [
            self.executable,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={self.profile.name}",
            "--no-proxy-server",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-sync",
            "about:blank",
        ]
        environment = direct_environment()
        if sys.platform.startswith("linux"):
            # Ozone's off-screen platform runs the normal browser engine without
            # attaching a window to the caller's desktop display.
            command[1:1] = ["--ozone-platform=headless", "--disable-gpu"]
            environment.pop("DISPLAY", None)
            environment.pop("WAYLAND_DISPLAY", None)
        else:
            # Other Chrome platforms have no Ozone backend. Keep the explicit
            # browser transport windowless and surface any edge rejection.
            command.insert(1, "--headless=new")
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            command.insert(1, "--no-sandbox")
        return command, environment

    def _start(self) -> None:
        port = self._available_port()
        command, environment = self._launch_spec(port)
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=environment,
        )

        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        endpoint = f"http://127.0.0.1:{port}/json/list"
        deadline = time.monotonic() + BROWSER_START_TIMEOUT
        last_error: Exception | None = None
        targets: Any = None
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise DocsError(
                    f"Chrome exited during startup with status {self.process.returncode}"
                )
            try:
                with opener.open(endpoint, timeout=0.5) as response:
                    targets = json.loads(response.read().decode("utf-8"))
                if isinstance(targets, list):
                    break
            except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
                last_error = error
            time.sleep(0.05)
        else:
            raise DocsError(f"Chrome DevTools did not start: {last_error}")

        pages = [
            item
            for item in targets
            if isinstance(item, dict)
            and item.get("type") == "page"
            and isinstance(item.get("webSocketDebuggerUrl"), str)
        ]
        page = next((item for item in pages if item.get("url") == "about:blank"), None)
        if page is None:
            page = pages[0] if pages else None
        if page is None:
            raise DocsError("Chrome DevTools exposed no page target")
        self.connection = DevToolsConnection(page["webSocketDebuggerUrl"])
        self._command("Page.enable")
        self._command("Network.enable")

    def _receive(self, deadline: float) -> dict[str, Any]:
        if self.connection is None:
            raise DocsError("Chrome DevTools is not connected")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise DocsError("Chrome DevTools request timed out")
        try:
            return self.connection.receive_json(remaining)
        except (OSError, TimeoutError, socket.timeout) as error:
            raise DocsError(f"Chrome DevTools request failed: {error}") from error

    def _command(self, method: str, params: dict[str, Any] | None = None) -> Any:
        if self.connection is None:
            raise DocsError("Chrome DevTools is not connected")
        self.next_id += 1
        command_id = self.next_id
        message: dict[str, Any] = {"id": command_id, "method": method}
        if params is not None:
            message["params"] = params
        self.connection.send_json(message)
        deadline = time.monotonic() + BROWSER_REQUEST_TIMEOUT
        while True:
            response = self._receive(deadline)
            if response.get("id") != command_id:
                self.events.append(response)
                continue
            error = response.get("error")
            if isinstance(error, dict):
                raise DocsError(
                    f"Chrome DevTools {method} failed: {error.get('message', error)}"
                )
            return response.get("result", {})

    def get(self, url: str) -> str:
        self.events.clear()
        navigation = self._command("Page.navigate", {"url": url})
        if not isinstance(navigation, dict):
            raise DocsError("Chrome returned an invalid navigation result")
        if navigation.get("errorText"):
            raise UpstreamError(
                url, transport="browser", reason=str(navigation["errorText"])
            )
        loader_id = navigation.get("loaderId")
        deadline = time.monotonic() + BROWSER_REQUEST_TIMEOUT
        response_data: dict[str, Any] | None = None
        request_id: str | None = None
        loaded = False

        while not (response_data is not None and loaded):
            message = self.events.pop(0) if self.events else self._receive(deadline)
            method = message.get("method")
            params = message.get("params")
            if not isinstance(params, dict):
                continue
            if method == "Network.responseReceived":
                response = params.get("response")
                same_loader = not loader_id or params.get("loaderId") == loader_id
                if (
                    same_loader
                    and params.get("type") == "Document"
                    and isinstance(response, dict)
                ):
                    response_data = response
                    request_id = params.get("requestId")
            elif method == "Network.loadingFinished" and request_id:
                if params.get("requestId") == request_id:
                    loaded = True
            elif method == "Network.loadingFailed" and request_id:
                if params.get("requestId") == request_id:
                    raise UpstreamError(
                        url,
                        transport="browser",
                        reason=str(params.get("errorText") or "navigation failed"),
                    )

        if response_data is None or not request_id:
            raise DocsError("Chrome returned no document response")
        body_result = self._command("Network.getResponseBody", {"requestId": request_id})
        if not isinstance(body_result, dict) or not isinstance(
            body_result.get("body"), str
        ):
            raise DocsError("Chrome returned no document body")
        body = body_result["body"]
        if body_result.get("base64Encoded"):
            try:
                body = base64.b64decode(body).decode("utf-8")
            except (ValueError, UnicodeDecodeError) as error:
                raise DocsError(f"invalid base64 document body: {error}") from error

        status_value = response_data.get("status")
        status = int(status_value) if isinstance(status_value, (int, float)) else None
        headers = response_data.get("headers")
        header_map = headers if isinstance(headers, dict) else {}
        eo_log_uuid = dict_header(header_map, "EO-LOG-UUID")
        if status is None or not 200 <= status < 300:
            raise UpstreamError(
                url,
                transport="browser",
                reason=None if status is not None else "Chrome reported no HTTP status",
                http_status=status,
                eo_log_uuid=eo_log_uuid,
                response_summary=response_summary(body),
            )
        return body

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
            self.process = None
        profile = getattr(self, "profile", None)
        if profile is not None:
            profile.cleanup()


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def cache_root() -> Path:
    explicit = os.environ.get("UNITREE_DOCS_CACHE")
    if explicit:
        return Path(explicit).expanduser()
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".cache"
    return base / "unitree-docs"


def safe_segment(value: str, label: str) -> str:
    if not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise DocsError(f"invalid {label}: {value!r}")
    return urllib.parse.quote(value, safe="-_.~")


def atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def cache_fresh(path: Path, ttl: int = DEFAULT_TTL) -> bool:
    return path.exists() and time.time() - path.stat().st_mtime <= ttl


def flatten_nodes(nodes: Any, parent: str | None = None) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    if not isinstance(nodes, list):
        return flattened
    for node in nodes:
        if not isinstance(node, dict):
            continue
        record = {key: value for key, value in node.items() if key != "children"}
        record["parent"] = parent
        flattened.append(record)
        flattened.extend(flatten_nodes(node.get("children", []), node.get("path")))
    return flattened


def discover_spaces(data: Any) -> list[dict[str, Any]]:
    """Extract space records without mistaking their directory nodes for spaces."""
    groups = data if isinstance(data, list) else [data]
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for group in groups:
        if not isinstance(group, dict):
            continue
        candidates = group.get("spaces")
        if not isinstance(candidates, list):
            candidates = [group]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            path = item.get("spacePath") or item.get("path")
            name = item.get("spaceName") or item.get("name")
            if not isinstance(path, str) or not isinstance(name, str) or path in seen:
                continue
            seen.add(path)
            records.append(
                {
                    "name": name,
                    "path": path,
                    "group_id": group.get("groupId"),
                    "group_name": group.get("groupName"),
                }
            )
    return records


def canonical_url(locale: str, space: str, path: str) -> str:
    pieces = ["home", locale, space]
    if path:
        pieces.append(path)
    encoded = "/".join(urllib.parse.quote(piece, safe="-_.~") for piece in pieces)
    return f"https://{SUPPORT_HOST}/{encoded}"


class UnitreeDocs:
    def __init__(
        self,
        root: Path | None = None,
        offline: bool = False,
        transport: str = "browser",
    ):
        if transport not in {"http", "browser"}:
            raise DocsError(f"unsupported transport: {transport}")
        self.root = root or cache_root()
        self.offline = offline
        self.transport = transport
        self._browser: BrowserTransport | None = None

    def close(self) -> None:
        if self._browser is not None:
            self._browser.close()
            self._browser = None

    def _request(self, url: str, accept: str) -> str:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise DocsError(f"refusing non-Unitree source: {url}")
        if self.transport == "browser":
            if parsed.hostname == "robot-api.unitree.com":
                if self._browser is None:
                    self._browser = BrowserTransport()
                return self._browser.get(url)
            return self._urllib_request(url, accept)
        curl = shutil.which("curl")
        if curl:
            try:
                response = subprocess.run(
                    [
                        curl,
                        "--http2",
                        "--silent",
                        "--show-error",
                        "--max-time",
                        "25",
                        "--noproxy",
                        "*",
                        "--dump-header",
                        "-",
                        "--write-out",
                        CURL_STATUS_MARKER.decode("ascii") + "%{http_code}",
                        "--header",
                        f"Accept: {accept}",
                        "--header",
                        f"Origin: https://{SUPPORT_HOST}",
                        "--header",
                        f"Referer: https://{SUPPORT_HOST}/home/zh/",
                        "--user-agent",
                        USER_AGENT,
                        url,
                    ],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30,
                    env=direct_environment(),
                )
                body, status, headers = parse_curl_output(response.stdout)
                eo_log_uuid = header_value(headers, "EO-LOG-UUID")
                if response.returncode != 0:
                    stderr = response.stderr.decode("utf-8", errors="replace")
                    reason = response_summary(stderr) or (
                        f"curl exited with status {response.returncode}"
                    )
                    raise UpstreamError(
                        url,
                        transport="curl",
                        reason=reason,
                        http_status=status if status else None,
                        eo_log_uuid=eo_log_uuid,
                        response_summary=response_summary(body),
                    )
                if status is None:
                    raise UpstreamError(
                        url,
                        transport="curl",
                        reason="curl did not report an HTTP status",
                        response_summary=response_summary(body),
                    )
                if not 200 <= status < 300:
                    raise UpstreamError(
                        url,
                        transport="curl",
                        http_status=status,
                        eo_log_uuid=eo_log_uuid,
                        response_summary=response_summary(body),
                    )
                try:
                    return body.decode("utf-8")
                except UnicodeDecodeError as error:
                    raise UpstreamError(
                        url,
                        transport="curl",
                        reason=f"response is not UTF-8: {error}",
                        http_status=status,
                        eo_log_uuid=eo_log_uuid,
                        response_summary=response_summary(body),
                    ) from error
            except UpstreamError:
                raise
            except (
                subprocess.SubprocessError,
                OSError,
            ) as error:
                raise UpstreamError(
                    url, transport="curl", reason=str(error)
                ) from error

        # urllib is selected only when curl is unavailable before the request.
        # A failed curl request is never retried through another transport.
        return self._urllib_request(url, accept)

    def _urllib_request(self, url: str, accept: str) -> str:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": accept,
                "Origin": f"https://{SUPPORT_HOST}",
                "Referer": f"https://{SUPPORT_HOST}/home/zh/",
                "User-Agent": USER_AGENT,
            },
        )
        transport = "direct-http"
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(request, timeout=20) as response:
                body = response.read()
                status = getattr(response, "status", None) or response.getcode()
                if not 200 <= status < 300:
                    raise UpstreamError(
                        url,
                        transport=transport,
                        http_status=status,
                        eo_log_uuid=response.headers.get("EO-LOG-UUID"),
                        response_summary=response_summary(body),
                    )
                return body.decode("utf-8")
        except urllib.error.HTTPError as error:
            body = error.read()
            raise UpstreamError(
                url,
                transport=transport,
                http_status=error.code,
                eo_log_uuid=(
                    error.headers.get("EO-LOG-UUID") if error.headers else None
                ),
                response_summary=response_summary(body),
            ) from error
        except UpstreamError:
            raise
        except UnicodeDecodeError as error:
            raise UpstreamError(
                url,
                transport=transport,
                reason=f"response is not UTF-8: {error}",
            ) from error
        except (
            urllib.error.URLError,
            http.client.HTTPException,
            TimeoutError,
            ConnectionError,
            OSError,
        ) as error:
            raise UpstreamError(
                url, transport=transport, reason=str(error)
            ) from error

    def _api(self, suffix: str, **params: str) -> Any:
        if self.offline:
            raise DocsError("offline mode")
        endpoint = API_ROOT + suffix
        if params:
            endpoint += "?" + urllib.parse.urlencode(params)
        payload = json.loads(self._request(endpoint, "application/json, text/plain, */*"))
        if not isinstance(payload, dict) or payload.get("code") != 100:
            raise DocsError(f"unexpected Unitree API response from {endpoint}")
        return payload.get("data")

    def _cached_api(
        self, path: Path, suffix: str, refresh: bool, **params: str
    ) -> tuple[Any, str]:
        if self.offline:
            if path.exists():
                return load_json(path), "offline"
            raise DocsError(f"offline cache is missing: {path}")
        if not refresh and cache_fresh(path):
            return load_json(path), "fresh"
        data = self._api(suffix, **params)
        atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        return data, "refreshed"

    def spaces(self, locale: str, refresh: bool = False) -> dict[str, Any]:
        path = self.root / "spaces" / f"{safe_segment(locale, 'locale')}.json"
        data, status = self._cached_api(
            path, "/spaces2", refresh, locale=locale
        )
        return {
            "locale": locale,
            "cache_status": status,
            "spaces": discover_spaces(data),
        }

    def catalog(
        self, space: str, locale: str, refresh: bool = False
    ) -> tuple[dict[str, Any], str]:
        path = (
            self.root
            / "catalogs"
            / safe_segment(locale, "locale")
            / f"{safe_segment(space, 'space')}.json"
        )
        data, status = self._cached_api(
            path, "", refresh, space=space, locale=locale
        )
        if not isinstance(data, dict):
            raise DocsError(f"invalid catalog for {space}")
        return data, status

    def tree(self, space: str, locale: str, refresh: bool = False) -> dict[str, Any]:
        catalog, status = self.catalog(space, locale, refresh)
        return {
            "space": space,
            "locale": locale,
            "cache_status": status,
            "name": catalog.get("name"),
            "directory": catalog.get("directory", []),
        }

    def get(
        self,
        space: str,
        page_path: str,
        locale: str,
        refresh: bool = False,
    ) -> dict[str, Any]:
        catalog, catalog_status = self.catalog(space, locale, refresh)
        nodes = flatten_nodes(catalog.get("directory", []))
        node = next((item for item in nodes if item.get("path") == page_path), None)
        if node is None:
            raise DocsError(f"page not found: {space}/{page_path}")
        source_url = node.get("url")
        if not isinstance(source_url, str):
            raise DocsError(f"page has no content URL: {space}/{page_path}")

        page_dir = (
            self.root
            / "pages"
            / safe_segment(locale, "locale")
            / safe_segment(space, "space")
        )
        stem = safe_segment(page_path, "path")
        content_path = page_dir / f"{stem}.md"
        metadata_path = page_dir / f"{stem}.json"
        metadata = load_json(metadata_path) if metadata_path.exists() else {}
        same_version = (
            content_path.exists()
            and metadata.get("source_url") == source_url
            and metadata.get("updated_at") == node.get("updateTime")
        )
        page_status = "offline" if same_version and self.offline else (
            "fresh" if same_version else "missing"
        )

        if refresh or not same_version:
            if self.offline:
                raise DocsError(
                    f"offline page cache is missing or does not match the catalog: "
                    f"{space}/{page_path}"
                )
            content = self._request(source_url, "text/plain, */*")
            digest = hashlib.sha256(content.encode()).hexdigest()
            atomic_write(content_path, content)
            metadata = {
                "title": node.get("name"),
                "space": space,
                "path": page_path,
                "locale": locale,
                "updated_at": node.get("updateTime"),
                "canonical_url": canonical_url(locale, space, page_path),
                "source_url": source_url,
                "retrieved_at": now_iso(),
                "sha256": digest,
            }
            atomic_write(
                metadata_path,
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            )
            page_status = "refreshed"

        content = content_path.read_text(encoding="utf-8")
        result = dict(metadata)
        result.update(
            {
                "title": node.get("name"),
                "space": space,
                "path": page_path,
                "locale": locale,
                "updated_at": node.get("updateTime"),
                "canonical_url": canonical_url(locale, space, page_path),
                "source_url": source_url,
                "cache_status": page_status,
                "catalog_cache_status": catalog_status,
                "content": content,
            }
        )
        return result

    def get_url(self, url: str, refresh: bool = False) -> dict[str, Any]:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != SUPPORT_HOST:
            raise DocsError("expected an https://support.unitree.com documentation URL")
        parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
        if len(parts) < 4 or parts[0] != "home":
            raise DocsError("unsupported Unitree documentation URL")
        _, locale, space, page_path, *_ = parts
        return self.get(space, page_path, locale, refresh)

    @staticmethod
    def _normalize_search(data: Any, locale: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        groups = data if isinstance(data, list) else [data]
        for group in groups:
            if not isinstance(group, dict):
                continue
            space = group.get("spacePath") or group.get("space") or group.get("path")
            space_name = group.get("spaceName") or group.get("name")
            candidates = group.get("directory") or group.get("children") or []
            for item in flatten_nodes(candidates):
                path = item.get("path")
                if not isinstance(space, str) or not isinstance(path, str):
                    continue
                key = (space, path)
                if key in seen:
                    continue
                seen.add(key)
                results.append(
                    {
                        "space": space,
                        "space_name": space_name,
                        "path": path,
                        "title": item.get("name"),
                        "updated_at": item.get("updateTime"),
                        "description": item.get("description"),
                        "canonical_url": canonical_url(locale, space, path),
                    }
                )
        return results

    def _local_search(self, query: str, locale: str, limit: int) -> list[dict[str, Any]]:
        terms = [term.casefold() for term in re.split(r"\s+", query.strip()) if term]
        if not terms:
            return []
        scored: list[tuple[int, dict[str, Any]]] = []
        base = self.root / "pages" / safe_segment(locale, "locale")
        for content_path in base.glob("*/*.md") if base.exists() else []:
            content = content_path.read_text(encoding="utf-8", errors="replace")
            folded = content.casefold()
            score = sum(folded.count(term) for term in terms)
            if not score:
                continue
            metadata_path = content_path.with_suffix(".json")
            metadata = load_json(metadata_path) if metadata_path.exists() else {}
            first = min((folded.find(term) for term in terms if term in folded), default=0)
            start = max(0, first - 100)
            excerpt = re.sub(r"\s+", " ", content[start : first + 220]).strip()
            result = {key: value for key, value in metadata.items() if key != "sha256"}
            result["excerpt"] = excerpt
            scored.append((score, result))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [result for _, result in scored[:limit]]

    def _has_local_pages(self, locale: str) -> bool:
        base = self.root / "pages" / safe_segment(locale, "locale")
        return base.exists() and next(base.glob("*/*.md"), None) is not None

    def search(
        self,
        query: str,
        locale: str,
        limit: int = 10,
        refresh: bool = False,
        deep: bool = False,
    ) -> dict[str, Any]:
        if self.offline:
            if not self._has_local_pages(locale):
                raise DocsError(f"offline page cache is empty for locale {locale!r}")
            return {
                "query": query,
                "locale": locale,
                "source": "local-cache",
                "cache_status": "offline",
                "results": self._local_search(query, locale, limit),
            }
        if deep:
            sync = self.sync_all(locale)
            return {
                "query": query,
                "locale": locale,
                "source": "deep-cache",
                "cache_status": "refreshed",
                "results": self._local_search(query, locale, limit),
                "sync_failures": sync["failed"],
            }
        search_path = (
            self.root
            / "search"
            / safe_segment(locale, "locale")
            / f"{hashlib.sha256(query.encode()).hexdigest()}.json"
        )
        data, status = self._cached_api(
            search_path, "/search", refresh, key=query, locale=locale
        )
        return {
            "query": query,
            "locale": locale,
            "source": "official-search",
            "cache_status": status,
            "results": self._normalize_search(data, locale)[:limit],
        }

    def sync_space(self, space: str, locale: str) -> dict[str, Any]:
        catalog, _ = self.catalog(space, locale, refresh=True)
        nodes = [node for node in flatten_nodes(catalog.get("directory", [])) if node.get("url")]
        synced: list[str] = []
        for node in nodes:
            path = node.get("path")
            if not isinstance(path, str):
                continue
            self.get(space, path, locale, refresh=True)
            synced.append(path)
        return {"space": space, "locale": locale, "synced": synced, "failed": []}

    def sync_all(self, locale: str) -> dict[str, Any]:
        spaces = self.spaces(locale, refresh=True)["spaces"]
        results: list[dict[str, Any]] = []
        for item in spaces:
            space = item["path"]
            results.append(self.sync_space(space, locale))
        return {"locale": locale, "spaces": results, "failed": []}

    def status(self) -> dict[str, Any]:
        catalogs = list((self.root / "catalogs").glob("*/*.json"))
        pages = list((self.root / "pages").glob("*/*/*.md"))
        return {
            "cache_root": str(self.root),
            "catalogs": len(catalogs),
            "pages": len(pages),
            "bytes": sum(path.stat().st_size for path in pages),
        }


def emit(value: Any, body: bool = False) -> None:
    if body:
        print(value.get("content", ""), end="")
    else:
        print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, help="override the cache directory")
    parser.add_argument("--offline", action="store_true", help="use cached data only")
    parser.add_argument(
        "--transport",
        choices=("http", "browser"),
        default=os.environ.get("UNITREE_DOCS_TRANSPORT", "browser"),
        help="select one online transport without automatic fallback",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def locale_options(command: argparse.ArgumentParser) -> None:
        command.add_argument("--locale", default="zh")
        command.add_argument("--refresh", action="store_true")

    spaces = subparsers.add_parser("spaces", help="discover every document space")
    locale_options(spaces)

    search = subparsers.add_parser("search", help="search all official documentation")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument(
        "--deep", action="store_true", help="synchronize all spaces before full-text search"
    )
    locale_options(search)

    tree = subparsers.add_parser("tree", help="read a document-space tree")
    tree.add_argument("space")
    locale_options(tree)

    get = subparsers.add_parser("get", help="retrieve a page by space and path")
    get.add_argument("space")
    get.add_argument("path")
    get.add_argument("--body", action="store_true")
    locale_options(get)

    get_url = subparsers.add_parser("get-url", help="retrieve a support.unitree.com URL")
    get_url.add_argument("url")
    get_url.add_argument("--refresh", action="store_true")
    get_url.add_argument("--body", action="store_true")

    sync = subparsers.add_parser("sync", help="mirror one or every document space")
    sync.add_argument("space", nargs="?")
    sync.add_argument("--all", action="store_true", dest="all_spaces")
    sync.add_argument("--locale", default="zh")

    subparsers.add_parser("status", help="show local cache statistics")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    docs = UnitreeDocs(args.cache, args.offline, args.transport)
    try:
        if args.command == "spaces":
            emit(docs.spaces(args.locale, args.refresh))
        elif args.command == "search":
            emit(
                docs.search(
                    args.query, args.locale, args.limit, args.refresh, args.deep
                )
            )
        elif args.command == "tree":
            emit(docs.tree(args.space, args.locale, args.refresh))
        elif args.command == "get":
            emit(docs.get(args.space, args.path, args.locale, args.refresh), args.body)
        elif args.command == "get-url":
            emit(docs.get_url(args.url, args.refresh), args.body)
        elif args.command == "sync":
            if args.all_spaces == bool(args.space):
                raise DocsError("sync requires exactly one of SPACE or --all")
            if args.all_spaces:
                emit(docs.sync_all(args.locale))
            else:
                emit(docs.sync_space(args.space, args.locale))
        elif args.command == "status":
            emit(docs.status())
        return 0
    except DocsError as error:
        print(json.dumps(error.to_dict(), ensure_ascii=False), file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(
            json.dumps(
                {"error": "invalid_json", "message": str(error)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1
    finally:
        docs.close()


if __name__ == "__main__":
    raise SystemExit(main())
