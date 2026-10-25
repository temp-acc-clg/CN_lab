"""
Unit and Integration Tests for HTTP Request Analyzer
Run via: pytest or python test_analyzer.py
"""

import unittest
from analyzer import normalize_url, format_bytes, analyze_request, STATUS_CODE_INFO
from app import app


class TestHTTPRequestAnalyzer(unittest.TestCase):
    def test_normalize_url(self):
        # Test missing scheme prepends https://
        self.assertEqual(normalize_url("example.com"), "https://example.com")
        self.assertEqual(normalize_url("http://example.com"), "http://example.com")
        self.assertEqual(normalize_url("https://example.com/api/test"), "https://example.com/api/test")
        self.assertEqual(normalize_url("   httpbin.org/get   "), "https://httpbin.org/get")
        self.assertEqual(normalize_url(""), "")

    def test_format_bytes(self):
        self.assertEqual(format_bytes(500), "500 bytes")
        self.assertIn("KB", format_bytes(2048))
        self.assertIn("MB", format_bytes(5 * 1024 * 1024))

    def test_status_code_info(self):
        self.assertEqual(STATUS_CODE_INFO[200][0], "OK")
        self.assertEqual(STATUS_CODE_INFO[404][0], "Not Found")
        self.assertEqual(STATUS_CODE_INFO[500][0], "Internal Server Error")

    def test_analyze_request_empty_url(self):
        result = analyze_request("")
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "InvalidInput")

    def test_analyze_request_success_example_com(self):
        result = analyze_request("https://example.com", method="GET", timeout=10.0)
        self.assertTrue(result["success"])
        self.assertEqual(result["response"]["status_code"], 200)
        self.assertIn("Content-Type", result["response"]["headers"])
        self.assertGreater(result["timing"]["total_time_ms"], 0)
        self.assertIn("example.com", result["network_insights"]["host"])

    def test_analyze_request_invalid_domain(self):
        result = analyze_request("https://this-is-a-completely-fake-domain-12345.xyz", timeout=5.0)
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "Connection Failure")

    def test_analyze_request_timeout(self):
        # A 0.0001s timeout should reliably trigger timeout exception
        result = analyze_request("https://httpbin.org/delay/5", timeout=0.001)
        self.assertFalse(result["success"])
        self.assertIn(result["error_type"], ["Request Timeout", "Connection Failure"])

    def test_flask_health_and_analyze_routes(self):
        client = app.test_client()
        # Test health endpoint
        health_resp = client.get("/api/health")
        self.assertEqual(health_resp.status_code, 200)
        self.assertEqual(health_resp.get_json()["status"], "healthy")

        # Test index page
        index_resp = client.get("/")
        self.assertEqual(index_resp.status_code, 200)
        self.assertIn(b"HTTP Request Analyzer", index_resp.data)

        # Test API analyze endpoint
        api_resp = client.post("/api/analyze", json={
            "url": "https://example.com",
            "method": "GET"
        })
        self.assertEqual(api_resp.status_code, 200)
        data = api_resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["response"]["status_code"], 200)


if __name__ == "__main__":
    unittest.main()
