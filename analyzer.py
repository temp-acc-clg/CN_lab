"""
HTTP Request Analyzer - Core Engine
Handles URL validation, HTTP request execution, response extraction,
timing analysis, network error handling, and networking educational insights.
"""

import time
import json
import urllib.parse
from typing import Dict, Any, Optional, List
import requests
from requests.exceptions import (
    RequestException,
    ConnectionError as ReqConnectionError,
    Timeout,
    TooManyRedirects,
    SSLError,
    MissingSchema,
    InvalidURL,
)

# HTTP Status Code Explanations & Descriptions
STATUS_CODE_INFO = {
    100: ("Continue", "The server has received the request headers and the client should proceed to send the request body."),
    101: ("Switching Protocols", "The requester has asked the server to switch protocols and the server has agreed to do so."),
    200: ("OK", "The request succeeded. Standard response for successful HTTP requests."),
    201: ("Created", "The request succeeded, and a new resource was created as a result."),
    202: ("Accepted", "The request has been accepted for processing, but processing is not yet complete."),
    204: ("No Content", "The server successfully processed the request, but is not returning any content."),
    301: ("Moved Permanently", "The requested resource has been definitively moved to a new permanent URI."),
    302: ("Found (Temporary Redirect)", "The requested resource resides temporarily under a different URI."),
    304: ("Not Modified", "Indicates that the resource has not been modified since the version specified by the request headers."),
    307: ("Temporary Redirect", "The request should be repeated with another URI; future requests should still use original URI."),
    308: ("Permanent Redirect", "The target resource has been assigned a new permanent URI and any future references should use it."),
    400: ("Bad Request", "The server cannot or will not process the request due to perceived client error (e.g. malformed syntax)."),
    401: ("Unauthorized", "Authentication is required and has failed or has not yet been provided."),
    403: ("Forbidden", "The server understands the request but refuses to authorize it."),
    404: ("Not Found", "The requested resource could not be found on the server."),
    405: ("Method Not Allowed", "The HTTP method in the request is known by the server but not supported by the target resource."),
    408: ("Request Timeout", "The server timed out waiting for the request from the client."),
    429: ("Too Many Requests", "The user has sent too many requests in a given amount of time (Rate limiting)."),
    500: ("Internal Server Error", "A generic error message indicating an unexpected condition was encountered on the server."),
    502: ("Bad Gateway", "The server, while acting as a gateway or proxy, received an invalid response from the inbound server."),
    503: ("Service Unavailable", "The server is currently unable to handle the request due to maintenance or overload."),
    504: ("Gateway Timeout", "The server, while acting as a gateway or proxy, did not receive a timely response from an upstream server."),
}

# Educational explanations for common HTTP Headers
HEADER_DESCRIPTIONS = {
    "content-type": "Indicates the original media type (MIME type) of the resource (e.g. application/json, text/html).",
    "content-length": "The size of the response body in bytes.",
    "server": "Describes the software used by the origin server to handle the request.",
    "date": "The date and time at which the message was originated by the server.",
    "cache-control": "Directives for caching mechanisms in both requests and responses.",
    "set-cookie": "Sends a cookie from the server to the user agent to be stored for future requests.",
    "access-control-allow-origin": "Specifies which origins are allowed to access resources in Cross-Origin Resource Sharing (CORS).",
    "location": "Used in redirection (3xx) or when a new resource has been created (201).",
    "connection": "Controls whether the network connection stays open after the current transaction finishes (e.g., keep-alive).",
    "content-encoding": "Specifies the compression algorithm applied to the body (e.g. gzip, br).",
    "strict-transport-security": "Enforces secure (HTTPS) connections to the server (HSTS).",
    "etag": "An identifier for a specific version of a resource, used for cache validation.",
    "x-powered-by": "Specifies the technology supporting the web application (often disabled for security).",
}


def normalize_url(url: str) -> str:
    """
    Ensures that the URL contains a valid scheme (defaults to https://).
    Trims any accidental whitespace.
    """
    clean_url = url.strip()
    if not clean_url:
        return ""
    if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
        clean_url = "https://" + clean_url
    return clean_url


def format_bytes(size: int) -> str:
    """Format bytes into readable units (Bytes, KB, MB)."""
    if size < 1024:
        return f"{size} bytes"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB ({size} bytes)"
    else:
        return f"{size / (1024 * 1024):.2f} MB ({size} bytes)"


def analyze_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    data: Optional[str] = None,
    json_data: Optional[Any] = None,
    timeout: float = 10.0,
    allow_redirects: bool = True,
    verify_ssl: bool = True
) -> Dict[str, Any]:
    """
    Sends an HTTP request using requests library and extracts comprehensive metrics,
    status details, headers, body, redirects, and network insights.
    """
    target_url = normalize_url(url)
    method = method.upper().strip()

    if not target_url:
        return {
            "success": False,
            "error_type": "InvalidInput",
            "error_message": "URL cannot be empty."
        }

    # Prepared output dictionary
    result: Dict[str, Any] = {
        "success": False,
        "request": {
            "url": target_url,
            "method": method,
            "headers": headers or {},
            "params": params or {},
            "payload": data or (json.dumps(json_data) if json_data else None),
            "timeout": timeout,
        },
        "response": None,
        "timing": {},
        "network_insights": {},
        "error_type": None,
        "error_message": None,
    }

    # Default User-Agent if not provided
    req_headers = {"User-Agent": "HTTPRequestAnalyzer/1.0 (Educational CN Tool)"}
    if headers:
        req_headers.update(headers)

    start_time = time.perf_counter()

    try:
        # Execute the HTTP request
        response = requests.request(
            method=method,
            url=target_url,
            headers=req_headers,
            params=params,
            data=data if (data and not json_data) else None,
            json=json_data if json_data else None,
            timeout=timeout,
            allow_redirects=allow_redirects,
            verify=verify_ssl
        )
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Server response elapsed time measured by requests
        server_elapsed_ms = round(response.elapsed.total_seconds() * 1000, 2)

        # Status Code Analysis
        status_code = response.status_code
        status_reason = response.reason or STATUS_CODE_INFO.get(status_code, ("Unknown", ""))[0]
        status_description = STATUS_CODE_INFO.get(status_code, (status_reason, "Custom or unstandardized status code."))[1]

        if 100 <= status_code < 200:
            category = "1xx Informational"
        elif 200 <= status_code < 300:
            category = "2xx Success"
        elif 300 <= status_code < 400:
            category = "3xx Redirection"
        elif 400 <= status_code < 500:
            category = "4xx Client Error"
        else:
            category = "5xx Server Error"

        # Headers analysis with educational explanations
        headers_dict = dict(response.headers)
        headers_analyzed = []
        for key, val in headers_dict.items():
            lower_k = key.lower()
            explanation = HEADER_DESCRIPTIONS.get(lower_k, "Standard or custom HTTP response header.")
            headers_analyzed.append({
                "name": key,
                "value": val,
                "description": explanation
            })

        # Request headers actually sent by requests session
        request_headers_sent = dict(response.request.headers)

        # Content parsing & sizing
        raw_content = response.content
        content_size_bytes = len(raw_content)
        content_type = response.headers.get("Content-Type", "Unknown")

        # Determine formatted body preview
        body_text = response.text
        is_json = False
        formatted_json = None
        if "application/json" in content_type.lower():
            try:
                parsed_json = response.json()
                formatted_json = json.dumps(parsed_json, indent=2)
                is_json = True
            except Exception:
                pass

        # Redirect tracking
        redirect_chain = []
        if response.history:
            for resp in response.history:
                redirect_chain.append({
                    "url": resp.url,
                    "status_code": resp.status_code,
                    "reason": resp.reason,
                    "redirect_to": resp.headers.get("Location", "")
                })

        parsed_target = urllib.parse.urlparse(response.url)

        result["success"] = True
        result["timing"] = {
            "total_time_ms": total_time_ms,
            "server_elapsed_ms": server_elapsed_ms,
        }
        result["response"] = {
            "status_code": status_code,
            "status_reason": status_reason,
            "status_category": category,
            "status_description": status_description,
            "content_type": content_type,
            "content_length": content_size_bytes,
            "content_length_human": format_bytes(content_size_bytes),
            "encoding": response.encoding,
            "final_url": response.url,
            "is_redirect": len(response.history) > 0,
            "redirect_chain": redirect_chain,
            "headers": headers_dict,
            "headers_analyzed": headers_analyzed,
            "request_headers_sent": request_headers_sent,
            "cookies": dict(response.cookies),
            "body": formatted_json if is_json else body_text,
            "is_json": is_json,
            "char_count": len(body_text),
        }

        # Network Education Insights
        result["network_insights"] = {
            "protocol": parsed_target.scheme.upper(),
            "host": parsed_target.netloc,
            "path": parsed_target.path or "/",
            "is_https": parsed_target.scheme.lower() == "https",
            "redirect_count": len(redirect_chain),
            "summary_note": f"A {method} request was transmitted over {parsed_target.scheme.upper()} to host '{parsed_target.netloc}'. "
                           f"The server responded with HTTP {status_code} ({status_reason}) in {total_time_ms} ms."
        }

        return result

    except MissingSchema:
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "success": False,
            "error_type": "Invalid URL Scheme",
            "error_message": f"The URL '{target_url}' lacks a valid protocol scheme (such as http:// or https://).",
            "timing": {"total_time_ms": total_time_ms}
        }
    except InvalidURL as e:
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "success": False,
            "error_type": "Invalid URL",
            "error_message": f"Malformed URL: {str(e)}",
            "timing": {"total_time_ms": total_time_ms}
        }
    except ReqConnectionError as e:
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "success": False,
            "error_type": "Connection Failure",
            "error_message": (
                f"Failed to establish a connection to '{target_url}'. "
                f"Possible causes: DNS lookup failed, hostname does not exist, host is offline, or connection was refused."
            ),
            "details": str(e),
            "timing": {"total_time_ms": total_time_ms}
        }
    except Timeout:
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "success": False,
            "error_type": "Request Timeout",
            "error_message": f"The request exceeded the allotted timeout threshold of {timeout} seconds.",
            "timing": {"total_time_ms": total_time_ms}
        }
    except TooManyRedirects:
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "success": False,
            "error_type": "Redirect Loop Detected",
            "error_message": "Exceeded maximum redirect limit. The server may be configured in an infinite redirect cycle.",
            "timing": {"total_time_ms": total_time_ms}
        }
    except SSLError as e:
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "success": False,
            "error_type": "SSL/TLS Verification Error",
            "error_message": f"Failed to verify the SSL/TLS certificate for '{target_url}'. Certificate may be self-signed, invalid, or expired.",
            "details": str(e),
            "timing": {"total_time_ms": total_time_ms}
        }
    except RequestException as e:
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "success": False,
            "error_type": "HTTP Request Exception",
            "error_message": f"An unexpected network error occurred: {str(e)}",
            "timing": {"total_time_ms": total_time_ms}
        }
