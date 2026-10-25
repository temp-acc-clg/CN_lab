# HTTP Request Analyzer — Computer Networks Project

An educational and diagnostic tool designed to analyze client-server HTTP communication. This project allows users to transmit HTTP requests to web servers or APIs, measure network latency, and inspect status codes, headers, and payload structures.

It provides both a **Command-Line Interface (CLI)** and a **Web Interface (Flask GUI)** with built-in networking concept explanations.

---

## 1. Features

- **Protocol & URL Handling**: Supports standard HTTP and HTTPS requests. Automatically normalizes URLs when schemes are omitted.
- **HTTP Methods Supported**: Full support for `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `HEAD`, and `OPTIONS`.
- **Response Metrics & Analysis**:
  - **Status Code & Reason Phrase**: E.g., `200 OK`, `404 Not Found`, `500 Internal Server Error`, with classification into 1xx, 2xx, 3xx, 4xx, and 5xx categories.
  - **Latency / Response Time**: Precise measurement of request round-trip time (RTT) in milliseconds (`ms`).
  - **Headers Breakdown**: Detailed table displaying response headers alongside explanations of their networking purposes (e.g., `Cache-Control`, `Content-Type`, `Server`, `HSTS`, `CORS`).
  - **Client Headers Sent**: View the actual request headers transmitted across the network.
  - **Payload & Body Inspection**: Auto-formatted JSON viewer, raw text viewer, character and byte sizing, and copy-to-clipboard functionality.
  - **Redirect Tracking**: Detects and displays full redirect hop chains (e.g., `301 Moved Permanently` or `302 Found` redirecting to HTTPS).
- **Network Error Diagnostics**: Clear, user-friendly diagnoses for DNS lookup failures, connection refusals, timeouts, and SSL/TLS certificate errors.
- **Dual Interface**:
  - **CLI Tool** (`main.py`): Interactive menu and quick CLI flags.
  - **Modern Web GUI** (`app.py`): Dark-mode web interface with quick-test preset chips and live history.

---

## 2. Project Architecture

```
CN_project/
├── analyzer.py          # Core networking engine (requests, timing, parsing, error handling)
├── main.py              # Command-line interface (interactive prompt & argument parser)
├── app.py               # Flask web server and REST API (/api/analyze)
├── templates/
│   └── index.html       # Web interface HTML template
├── static/
│   ├── css/
│   │   └── style.css    # Responsive dark-mode stylesheet
│   └── js/
│       └── app.js       # Dynamic frontend logic, header rows, tabs, and history
├── test_analyzer.py     # Automated test suite (unit and integration tests)
├── requirements.txt     # Python package dependencies
├── .gitignore           # Git ignore file for Python/Flask artifacts
└── README.md            # Comprehensive project documentation
```

---

## 3. Prerequisites

- **Python 3.8 or higher** (Python 3.10+ recommended)
- **pip** (Python package installer)

Check your installed versions by running:
```bash
python --version
pip --version
```

---

## 4. Local Machine Setup Guide

Follow these steps to set up and run the project locally on your machine.

### Step 1: Open the Project Directory
Open your terminal or command prompt and navigate to the project directory:
```bash
cd c:\Users\ketha\CN_project
```

### Step 2: Create and Activate a Virtual Environment (Recommended)

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If you encounter a PowerShell execution policy restriction, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, or use Command Prompt: `venv\Scripts\activate.bat`)*

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
Install `requests`, `flask`, and `colorama`:
```bash
pip install -r requirements.txt
```

---

## 5. How to Run the Application

You can use either the **Terminal CLI Application** or the **Web GUI Interface**.

### Option A: Running the Command-Line Interface (CLI)

#### 1. Interactive Mode
Run `main.py` with no arguments to launch the interactive prompt:
```bash
python main.py
```
You will be prompted to enter:
1. Target URL (e.g., `example.com` or `httpbin.org/get`)
2. HTTP Method (`GET`, `POST`, `PUT`, `DELETE`, etc.)
3. Optional custom headers
4. Optional request body payload
5. Custom timeout in seconds

#### 2. Quick Command-Line Flags
You can also run direct commands using CLI arguments:

- **Simple GET Request**:
  ```bash
  python main.py https://example.com -m GET
  ```

- **Inspect JSON API Endpoint**:
  ```bash
  python main.py https://httpbin.org/get
  ```

- **POST Request with JSON Data**:
  ```bash
  python main.py https://httpbin.org/post -m POST -d "{\"name\": \"Alice\", \"role\": \"Admin\"}"
  ```

- **Custom Headers and Timeout**:
  ```bash
  python main.py https://httpbin.org/headers -H "Authorization: Bearer mytoken123" -t 5.0
  ```

- **View Full Untruncated Response Body**:
  ```bash
  python main.py https://example.com --full-body
  ```

- **Output as Raw JSON**:
  ```bash
  python main.py https://example.com --json-output
  ```

---

### Option B: Running the Web Interface (Flask GUI)

1. Start the Flask application server:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```
3. Use the interface to:
   - Click one of the **Quick Presets** (e.g. *Example Domain*, *HTTPBin JSON*, *404 Not Found*, *Latency Delay*) to test immediately.
   - Enter any custom URL and select your desired HTTP method.
   - Configure dynamic headers using the Key-Value row editor.
   - Send requests and inspect the status badge, latency (ms), payload size, headers table, and formatted body.
   - View recent requests in the **History** drawer.
   - Read networking concepts by clicking the **CN Concepts** button.

---

## 6. Running the Automated Test Suite

To verify all core logic, network error handlers, URL normalization, and Flask API endpoints:

```bash
python test_analyzer.py
```
Or using pytest:
```bash
pytest test_analyzer.py -v
```

Expected output:
```
Ran 8 tests in 1.25s
OK
```

---

## 7. Expected Output Example

When running `python main.py https://example.com -m GET`, the tool outputs:

```
========== HTTP REQUEST ANALYZER ==========

URL           : https://example.com
Method        : GET
Status Code   : 200 OK (2xx Success)
Response Time : 396.05 ms
Content Type  : text/html; charset=utf-8
Response Size : 577 bytes

Response Headers:
Date: Sun, 25 Oct 2026 06:41:58 GMT
Content-Type: text/html; charset=utf-8
Transfer-Encoding: chunked
Connection: keep-alive
Server: cloudflare
allow: GET, HEAD
Content-Encoding: gzip

Response Body:
<!doctype html><html lang=en><head><meta charset=utf-8>
<title>Example Domain</title>
...

--- Computer Networks Insight ---
A GET request was transmitted over HTTPS to host 'example.com'. The server responded with HTTP 200 (OK) in 396.05 ms.
Status Note: The request succeeded. Standard response for successful HTTP requests.
===========================================
```

### Network Error Example:
When testing an invalid domain (`python main.py https://invalid-domain-test-xyz.org`):
```
========== HTTP REQUEST ANALYZER ==========

Request Failed!
Error Type    : Connection Failure
Error Details : Failed to establish a connection to 'https://invalid-domain-test-xyz.org'. Possible causes: DNS lookup failed, hostname does not exist, host is offline, or connection was refused.
Elapsed Time  : 43.55 ms

===========================================
```

---

## 8. Computer Networks Concepts Demonstrated

1. **Application Layer Protocol (HTTP/HTTPS)**:
   - Client sends an ASCII-formatted request header specifying a Method (`GET`, `POST`, etc.), target URI, and Protocol Version (`HTTP/1.1`).
   - Server responds with a status line, headers, and optional body.

2. **Client-Server Architecture**:
   - Stateless protocol where each request is independent unless session/cookie state is maintained.

3. **Status Code Taxonomy**:
   - `1xx` Informational: Protocol negotiation (e.g. 101 Switching Protocols).
   - `2xx` Success: Action received and processed (e.g. 200 OK, 201 Created).
   - `3xx` Redirection: Resource location shifted (e.g. 301 Permanent, 302 Temporary).
   - `4xx` Client Errors: Client provided invalid request, missing token, or nonexistent path (e.g. 400, 401, 403, 404).
   - `5xx` Server Errors: Server encountered internal failure or gateway timeout (e.g. 500, 502, 504).

4. **Network Latency & Round-Trip Time (RTT)**:
   - Includes DNS resolution time, TCP 3-way handshake (`SYN` &rarr; `SYN-ACK` &rarr; `ACK`), TLS key exchange, server processing delay, and packet propagation delay over transmission media.

5. **HTTP Headers**:
   - Control content negotiation (`Accept`, `Content-Type`), caching (`Cache-Control`, `ETag`), compression (`Content-Encoding: gzip`), and security policies (`Strict-Transport-Security`, `CORS`).

---

## 9. Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3** | Core programming language |
| **Requests** | HTTP client library for socket transmission and response handling |
| **Flask** | Web framework serving GUI and API |
| **HTML5 & Vanilla CSS** | Clean dark-mode user interface with responsive layout |
| **JavaScript (ES6+)** | Dynamic asynchronous frontend without external JS frameworks |
| **Colorama** | Terminal color formatting for cross-platform CLI output |
| **Unittest** | Test automation suite |
