import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from unitree_docs import (
    BrowserTransport,
    DocsError,
    UpstreamError,
    UnitreeDocs,
    canonical_url,
    direct_environment,
    discover_spaces,
    flatten_nodes,
    main,
)


CATALOG = {
    "name": "Demo",
    "directory": [
        {
            "name": "Guide",
            "path": "guide",
            "url": "https://doc-cdn.unitree.com/1/2/en/page",
            "updateTime": "2026-01-02 03:04:05",
            "children": [
                {
                    "name": "Child",
                    "path": "child",
                    "url": "https://doc-cdn.unitree.com/1/3/en/child",
                    "updateTime": "2026-01-02 03:04:06",
                    "children": [],
                }
            ],
        }
    ],
}


class FakeDocs(UnitreeDocs):
    def __init__(self, root):
        super().__init__(root)
        self.calls = []

    def _api(self, suffix, **params):
        self.calls.append((suffix, params))
        if suffix == "":
            return CATALOG
        if suffix == "/spaces2":
            return [{"name": "Demo", "path": "demo"}]
        if suffix == "/search":
            return [
                {
                    "spaceName": "Demo",
                    "spacePath": "demo",
                    "directory": [{"name": "Guide", "path": "guide"}],
                }
            ]
        raise AssertionError(suffix)

    def _request(self, url, accept):
        self.calls.append((url, accept))
        return "# Official page\n\nLowCmd details.\n"


class UnitreeDocsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.docs = FakeDocs(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_flatten_nodes_preserves_parent(self):
        nodes = flatten_nodes(CATALOG["directory"])
        self.assertEqual([item["path"] for item in nodes], ["guide", "child"])
        self.assertEqual(nodes[1]["parent"], "guide")

    def test_spaces_are_discovered_dynamically(self):
        result = self.docs.spaces("en")
        self.assertEqual(result["spaces"][0]["name"], "Demo")
        self.assertEqual(result["spaces"][0]["path"], "demo")

    def test_space_discovery_excludes_page_directories(self):
        result = discover_spaces(
            [
                {
                    "groupId": "1",
                    "groupName": "Robots",
                    "spaces": [
                        {
                            "name": "G1",
                            "path": "G1_developer",
                            "directory": [{"name": "Guide", "path": "guide"}],
                        }
                    ],
                }
            ]
        )
        self.assertEqual([item["path"] for item in result], ["G1_developer"])

    def test_official_search_is_normalized(self):
        result = self.docs.search("LowCmd", "en")
        self.assertEqual(result["source"], "official-search")
        self.assertEqual(result["results"][0]["space"], "demo")
        self.assertEqual(result["results"][0]["path"], "guide")

    def test_get_caches_content_and_metadata(self):
        result = self.docs.get("demo", "guide", "en")
        self.assertEqual(result["cache_status"], "refreshed")
        self.assertIn("LowCmd", result["content"])
        second = self.docs.get("demo", "guide", "en")
        self.assertEqual(second["cache_status"], "fresh")

    def test_get_url_parses_canonical_route(self):
        result = self.docs.get_url(
            "https://support.unitree.com/home/en/demo/guide?ignored=true"
        )
        self.assertEqual(result["space"], "demo")
        self.assertEqual(result["path"], "guide")

    def test_local_search_works_offline(self):
        self.docs.get("demo", "guide", "en")
        offline = UnitreeDocs(self.root, offline=True)
        result = offline.search("LowCmd", "en")
        self.assertEqual(result["source"], "local-cache")
        self.assertEqual(result["results"][0]["path"], "guide")

    def test_offline_search_rejects_an_empty_cache(self):
        offline = UnitreeDocs(self.root, offline=True)
        with self.assertRaisesRegex(DocsError, "offline page cache is empty"):
            offline.search("LowCmd", "en")

    def test_online_search_does_not_fall_back_to_local_pages(self):
        self.docs.get("demo", "guide", "en")
        failure = UpstreamError(
            "https://robot-api.unitree.com/doc/search",
            transport="curl",
            http_status=567,
        )
        with (
            patch.object(self.docs, "_api", side_effect=failure),
            self.assertRaises(UpstreamError),
        ):
            self.docs.search("LowCmd", "en", refresh=True)

    def test_empty_official_search_does_not_trigger_local_search(self):
        self.docs.get("demo", "guide", "en")
        with patch.object(self.docs, "_api", return_value=[]):
            result = self.docs.search("LowCmd", "en", refresh=True)
        self.assertEqual(result["source"], "official-search")
        self.assertEqual(result["results"], [])

    def test_refresh_does_not_fall_back_to_a_stale_api_cache(self):
        cache_path = self.root / "spaces" / "en.json"
        cache_path.parent.mkdir(parents=True)
        cache_path.write_text('[{"name":"Cached","path":"cached"}]\n')
        failure = UpstreamError(
            "https://robot-api.unitree.com/doc/spaces2?locale=en",
            transport="curl",
            http_status=567,
        )
        with (
            patch.object(self.docs, "_api", side_effect=failure),
            self.assertRaises(UpstreamError),
        ):
            self.docs.spaces("en", refresh=True)

    def test_page_refresh_does_not_fall_back_to_stale_content(self):
        self.docs.get("demo", "guide", "en")
        failure = UpstreamError(
            CATALOG["directory"][0]["url"],
            transport="curl",
            http_status=567,
        )
        with (
            patch.object(self.docs, "_request", side_effect=failure),
            self.assertRaises(UpstreamError),
        ):
            self.docs.get("demo", "guide", "en", refresh=True)

    def test_deep_search_synchronizes_all_spaces(self):
        result = self.docs.search("LowCmd", "en", deep=True)
        self.assertEqual(result["source"], "deep-cache")
        self.assertEqual(
            {item["path"] for item in result["results"]}, {"guide", "child"}
        )

    def test_rejects_non_unitree_url(self):
        with self.assertRaises(DocsError):
            self.docs.get_url("https://example.com/home/en/demo/guide")

    def test_http2_transport_avoids_edge_http11_failures(self):
        docs = UnitreeDocs(self.root, transport="http")
        response = SimpleNamespace(
            stdout=(
                b"HTTP/1.1 200 Connection established\r\n\r\n"
                b"HTTP/2 200\r\ncontent-type: application/json\r\n\r\n"
                b'{"code":100}\n__UNITREE_HTTP_STATUS__:200'
            ),
            stderr=b"",
            returncode=0,
        )
        with (
            patch("unitree_docs.shutil.which", return_value="/usr/bin/curl"),
            patch("unitree_docs.subprocess.run", return_value=response) as run,
            patch("unitree_docs.urllib.request.urlopen") as urlopen,
        ):
            result = docs._request(
                "https://robot-api.unitree.com/doc/spaces2?locale=en",
                "application/json",
            )
        self.assertEqual(result, '{"code":100}')
        self.assertIn("--http2", run.call_args.args[0])
        self.assertIn("--noproxy", run.call_args.args[0])
        self.assertEqual(
            run.call_args.args[0][run.call_args.args[0].index("--noproxy") + 1],
            "*",
        )
        urlopen.assert_not_called()

    def test_direct_environment_removes_proxy_variables(self):
        with patch.dict(
            os.environ,
            {
                "HTTP_PROXY": "http://proxy.invalid:8080",
                "https_proxy": "http://proxy.invalid:8080",
                "ALL_PROXY": "socks5://proxy.invalid:1080",
                "NO_PROXY": "localhost",
                "UNITREE_KEEP": "yes",
            },
            clear=True,
        ):
            environment = direct_environment()
        self.assertEqual(environment, {"UNITREE_KEEP": "yes"})

    def test_linux_browser_transport_is_offscreen_and_direct(self):
        browser = BrowserTransport.__new__(BrowserTransport)
        browser.executable = "/usr/bin/google-chrome"
        browser.profile = SimpleNamespace(name="/tmp/unitree-test-profile")
        with (
            patch("unitree_docs.sys.platform", "linux"),
            patch.dict(
                os.environ,
                {
                    "DISPLAY": ":1",
                    "WAYLAND_DISPLAY": "wayland-0",
                    "HTTPS_PROXY": "http://proxy.invalid:8080",
                },
                clear=True,
            ),
        ):
            command, environment = browser._launch_spec(43123)
        self.assertIn("--ozone-platform=headless", command)
        self.assertNotIn("--headless=new", command)
        self.assertNotIn("--window-position=-10000,-10000", command)
        self.assertIn("--no-proxy-server", command)
        self.assertNotIn("DISPLAY", environment)
        self.assertNotIn("WAYLAND_DISPLAY", environment)
        self.assertNotIn("HTTPS_PROXY", environment)

    def test_edge_error_is_structured_and_not_retried_with_urllib(self):
        docs = UnitreeDocs(self.root, transport="http")
        body = (
            '<html><style>.hidden{display:none}</style><div id="statusCode">567</div>'
            '<script>var message="请求已被站点的安全策略拦截。";</script></html>'
        ).encode()
        response = SimpleNamespace(
            stdout=(
                b"HTTP/1.1 200 Connection established\r\n\r\n"
                b"HTTP/2 567\r\neo-log-uuid: 422135675686286091\r\n"
                b"content-type: text/html; charset=UTF-8\r\n\r\n"
                + body
                + b"\n__UNITREE_HTTP_STATUS__:567"
            ),
            stderr=b"",
            returncode=0,
        )
        with (
            patch("unitree_docs.shutil.which", return_value="/usr/bin/curl"),
            patch("unitree_docs.subprocess.run", return_value=response),
            patch("unitree_docs.urllib.request.urlopen") as urlopen,
            self.assertRaises(UpstreamError) as raised,
        ):
            docs._request(
                "https://robot-api.unitree.com/doc/spaces2?locale=zh",
                "application/json",
            )
        details = raised.exception.to_dict()
        self.assertEqual(details["error"], "upstream_error")
        self.assertEqual(details["http_status"], 567)
        self.assertEqual(details["eo_log_uuid"], "422135675686286091")
        self.assertIn("请求已被站点的安全策略拦截", details["response_summary"])
        urlopen.assert_not_called()

    def test_curl_transport_failure_is_not_retried_with_urllib(self):
        docs = UnitreeDocs(self.root, transport="http")
        response = SimpleNamespace(
            stdout=b"\n__UNITREE_HTTP_STATUS__:000",
            stderr=b"curl: (28) Operation timed out",
            returncode=28,
        )
        with (
            patch("unitree_docs.shutil.which", return_value="/usr/bin/curl"),
            patch("unitree_docs.subprocess.run", return_value=response),
            patch("unitree_docs.urllib.request.urlopen") as urlopen,
            self.assertRaises(UpstreamError) as raised,
        ):
            docs._request(
                "https://robot-api.unitree.com/doc/spaces2?locale=zh",
                "application/json",
            )
        self.assertIn("Operation timed out", raised.exception.to_dict()["reason"])
        urlopen.assert_not_called()

    def test_urllib_http_error_is_structured_without_retry(self):
        docs = UnitreeDocs(self.root, transport="http")
        url = "https://robot-api.unitree.com/doc/spaces2?locale=zh"
        headers = Message()
        headers["EO-LOG-UUID"] = "9988776655"
        failure = urllib.error.HTTPError(
            url,
            567,
            "blocked",
            headers,
            io.BytesIO(b"The security policy has blocked this request."),
        )
        with (
            patch("unitree_docs.shutil.which", return_value=None),
            patch("unitree_docs.urllib.request.build_opener") as build_opener,
            self.assertRaises(UpstreamError) as raised,
        ):
            build_opener.return_value.open.side_effect = failure
            docs._request(url, "application/json")
        details = raised.exception.to_dict()
        self.assertEqual(details["http_status"], 567)
        self.assertEqual(details["eo_log_uuid"], "9988776655")
        self.assertIn("blocked this request", details["response_summary"])
        self.assertEqual(build_opener.return_value.open.call_count, 1)
        proxy_handler = build_opener.call_args.args[0]
        self.assertEqual(proxy_handler.proxies, {})

    def test_cli_emits_upstream_error_and_nonzero_exit(self):
        failure = UpstreamError(
            "https://robot-api.unitree.com/doc/search?key=Go2-W&locale=zh",
            transport="curl",
            http_status=567,
            eo_log_uuid="123456789",
            response_summary="请求已被站点的安全策略拦截。",
        )
        stderr = io.StringIO()
        with (
            patch.object(UnitreeDocs, "search", side_effect=failure),
            contextlib.redirect_stderr(stderr),
        ):
            exit_code = main(
                ["--cache", str(self.root), "search", "Go2-W", "--locale", "zh"]
            )
        payload = json.loads(stderr.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["error"], "upstream_error")
        self.assertEqual(payload["http_status"], 567)
        self.assertEqual(payload["eo_log_uuid"], "123456789")

    def test_canonical_url_escapes_segments(self):
        self.assertEqual(
            canonical_url("zh", "Motor SDK", "quick start"),
            "https://support.unitree.com/home/zh/Motor%20SDK/quick%20start",
        )


if __name__ == "__main__":
    unittest.main()
