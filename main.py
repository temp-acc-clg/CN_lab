"""
HTTP Request Analyzer - Command Line Interface (CLI)
Provides an interactive menu and CLI argument parser for analyzing HTTP requests.
"""

import sys
import argparse
import json
from typing import Dict, Optional

# Attempt to import colorama for colored terminal output; fallback gracefully if not available
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    GREEN = Fore.GREEN
    CYAN = Fore.CYAN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    MAGENTA = Fore.MAGENTA
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL
except Exception:
    GREEN = ""
    CYAN = ""
    YELLOW = ""
    RED = ""
    MAGENTA = ""
    BRIGHT = ""
    RESET = ""

from analyzer import analyze_request, normalize_url


def print_banner():
    """Prints a styled ASCII header banner."""
    print(f"\n{CYAN}{BRIGHT}{'=' * 60}")
    print(f"{CYAN}{BRIGHT}          HTTP REQUEST ANALYZER (CN Project)")
    print(f"{CYAN}{BRIGHT}    Inspect HTTP Requests, Headers, Timings & Errors")
    print(f"{CYAN}{BRIGHT}{'=' * 60}{RESET}\n")


def display_results(result: Dict, max_body_chars: int = 1200, show_full_body: bool = False):
    """Formats and prints the analysis result matching the expected project output format."""
    print(f"\n{CYAN}{BRIGHT}========== HTTP REQUEST ANALYZER =========={RESET}\n")

    if not result.get("success"):
        error_type = result.get("error_type", "Error")
        error_message = result.get("error_message", "An error occurred while executing the request.")
        timing = result.get("timing", {}).get("total_time_ms", 0.0)

        print(f"{RED}{BRIGHT}Request Failed!{RESET}")
        print(f"{YELLOW}Error Type    :{RESET} {RED}{error_type}{RESET}")
        print(f"{YELLOW}Error Details :{RESET} {error_message}")
        if "details" in result:
            print(f"{YELLOW}Technical Log :{RESET} {result['details']}")
        if timing:
            print(f"{YELLOW}Elapsed Time  :{RESET} {timing} ms")
        print(f"\n{CYAN}{'=' * 43}{RESET}\n")
        return

    req = result["request"]
    resp = result["response"]
    timing = result["timing"]
    insights = result.get("network_insights", {})

    status_code = resp["status_code"]
    status_reason = resp["status_reason"]
    # Color-code status code based on HTTP classification
    if 200 <= status_code < 300:
        status_color = GREEN
    elif 300 <= status_code < 400:
        status_color = CYAN
    elif 400 <= status_code < 500:
        status_color = YELLOW
    else:
        status_color = RED

    # Core Summary (as requested in spec)
    print(f"{BRIGHT}URL           {RESET}: {req['url']}")
    print(f"{BRIGHT}Method        {RESET}: {req['method']}")
    print(f"{BRIGHT}Status Code   {RESET}: {status_color}{status_code} {status_reason}{RESET} ({resp['status_category']})")
    print(f"{BRIGHT}Response Time {RESET}: {GREEN}{timing['total_time_ms']} ms{RESET}")
    print(f"{BRIGHT}Content Type  {RESET}: {resp['content_type']}")
    print(f"{BRIGHT}Response Size {RESET}: {resp['content_length_human']}")

    # Educational notes / Redirects if present
    if resp.get("is_redirect"):
        print(f"{YELLOW}Redirects     : Followed {len(resp['redirect_chain'])} hop(s) -> Final: {resp['final_url']}{RESET}")

    # Response Headers section
    print(f"\n{CYAN}{BRIGHT}Response Headers:{RESET}")
    for k, v in resp["headers"].items():
        print(f"{BRIGHT}{k}{RESET}: {v}")

    # Response Body section
    print(f"\n{CYAN}{BRIGHT}Response Body:{RESET}")
    body = resp.get("body", "")
    if not body:
        print(f"{YELLOW}[Empty Response Body]{RESET}")
    else:
        if not show_full_body and len(body) > max_body_chars:
            truncated = body[:max_body_chars]
            print(truncated)
            remaining = len(body) - max_body_chars
            print(f"\n{YELLOW}... [Truncated {remaining} characters. Use --full-body or interactive mode to view all] ...{RESET}")
        else:
            print(body)

    # Educational Networking Summary
    print(f"\n{MAGENTA}{BRIGHT}--- Computer Networks Insight ---{RESET}")
    print(f"{insights.get('summary_note', '')}")
    print(f"Status Note: {resp.get('status_description', '')}")
    print(f"{CYAN}{'=' * 43}{RESET}\n")


def interactive_mode():
    """Runs an interactive CLI loop prompting the user for URL, method, and headers/payload."""
    print_banner()
    print("Welcome! Press Ctrl+C or type 'exit' / 'q' at the URL prompt to quit.\n")

    while True:
        try:
            print(f"{YELLOW}------------------------------------------------------------{RESET}")
            url_input = input(f"{BRIGHT}Enter URL (e.g. example.com or httpbin.org/get): {RESET}").strip()
            if not url_input or url_input.lower() in ("exit", "quit", "q"):
                print("\nGoodbye!")
                break

            print(f"\nSelect HTTP Method:")
            print("1. GET (Default)")
            print("2. POST")
            print("3. PUT")
            print("4. DELETE")
            print("5. HEAD")
            print("6. PATCH")
            method_choice = input(f"{BRIGHT}Choose method [1-6, default 1]: {RESET}").strip()

            method_map = {
                "1": "GET",
                "2": "POST",
                "3": "PUT",
                "4": "DELETE",
                "5": "HEAD",
                "6": "PATCH"
            }
            method = method_map.get(method_choice, method_choice.upper() if method_choice else "GET")

            # Headers input (optional)
            custom_headers = {}
            add_headers = input(f"{BRIGHT}Add custom headers? (y/N): {RESET}").strip().lower()
            if add_headers == 'y':
                print("Enter headers in 'Key: Value' format (empty line to finish):")
                while True:
                    hdr_line = input("  > ").strip()
                    if not hdr_line:
                        break
                    if ":" in hdr_line:
                        hk, hv = hdr_line.split(":", 1)
                        custom_headers[hk.strip()] = hv.strip()
                    else:
                        print("    Invalid format. Please use 'Key: Value'.")

            # Body payload input if method in POST/PUT/PATCH
            payload_data = None
            if method in ["POST", "PUT", "PATCH"]:
                print(f"\n{BRIGHT}Enter request body/payload:{RESET}")
                print("(Type or paste body. To submit JSON, ensure valid JSON. Empty line to skip):")
                body_input = input("  Body > ").strip()
                if body_input:
                    payload_data = body_input

            # Timeout input
            timeout_str = input(f"{BRIGHT}Request Timeout in seconds [default 10]: {RESET}").strip()
            try:
                timeout = float(timeout_str) if timeout_str else 10.0
            except ValueError:
                timeout = 10.0

            print(f"\n{CYAN}Sending {method} request to {url_input}...{RESET}")
            
            # Analyze
            # Check if payload is valid JSON to send as JSON or raw data
            json_payload = None
            if payload_data:
                try:
                    json_payload = json.loads(payload_data)
                except Exception:
                    json_payload = None

            result = analyze_request(
                url=url_input,
                method=method,
                headers=custom_headers,
                data=payload_data if not json_payload else None,
                json_data=json_payload,
                timeout=timeout
            )

            display_results(result)

            # Option to inspect full body if it was truncated
            if result.get("success") and result.get("response", {}).get("char_count", 0) > 1200:
                view_all = input(f"{YELLOW}View full untruncated response body? (y/N): {RESET}").strip().lower()
                if view_all == 'y':
                    print(f"\n{CYAN}--- Full Response Body ---{RESET}")
                    print(result["response"]["body"])
                    print(f"{CYAN}--- End of Response Body ---{RESET}\n")

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user. Exiting...")
            break
        except Exception as e:
            print(f"{RED}Unexpected error: {e}{RESET}")


def main():
    """Main CLI entrypoint with argument support."""
    parser = argparse.ArgumentParser(
        description="HTTP Request Analyzer - Inspect HTTP communication, status codes, timings, headers, and responses."
    )
    parser.add_argument("url", nargs="?", help="Target URL to inspect (e.g., https://example.com)")
    parser.add_argument("-m", "--method", default="GET", choices=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                        help="HTTP method to use (default: GET)")
    parser.add_argument("-H", "--header", action="append", help="Custom header in 'Key: Value' format (can be used multiple times)")
    parser.add_argument("-d", "--data", help="Request body data (string or JSON)")
    parser.add_argument("-t", "--timeout", type=float, default=10.0, help="Request timeout in seconds (default: 10.0)")
    parser.add_argument("--full-body", action="store_true", help="Display full untruncated response body")
    parser.add_argument("--json-output", action="store_true", help="Output complete raw analyzer result as JSON")

    args = parser.parse_args()

    # If no URL argument provided, run the friendly interactive mode
    if not args.url:
        interactive_mode()
        return

    # Parse headers from CLI flags
    headers_dict = {}
    if args.header:
        for h in args.header:
            if ":" in h:
                k, v = h.split(":", 1)
                headers_dict[k.strip()] = v.strip()
            else:
                print(f"{YELLOW}Warning: Skipping invalid header format '{h}'. Must be 'Key: Value'.{RESET}")

    # Check if data is JSON
    json_data = None
    if args.data:
        try:
            json_data = json.loads(args.data)
        except Exception:
            json_data = None

    result = analyze_request(
        url=args.url,
        method=args.method,
        headers=headers_dict,
        data=args.data if not json_data else None,
        json_data=json_data,
        timeout=args.timeout
    )

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        display_results(result, show_full_body=args.full_body)


if __name__ == "__main__":
    main()
