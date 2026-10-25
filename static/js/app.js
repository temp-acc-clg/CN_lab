/**
 * HTTP Request Analyzer - Frontend Application Logic
 * Manages request composition, API calls, dynamic UI rendering, and history.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const form = document.getElementById("request-form");
    const methodSelect = document.getElementById("request-method");
    const urlInput = document.getElementById("request-url");
    const sendBtn = document.getElementById("send-btn");
    const btnText = sendBtn.querySelector(".btn-text");
    const spinner = sendBtn.querySelector(".spinner");

    const headersContainer = document.getElementById("headers-rows-container");
    const addHeaderRowBtn = document.getElementById("add-header-row-btn");
    const headerCountBadge = document.getElementById("header-count-badge");
    const requestBodyInput = document.getElementById("request-body-input");
    const formatJsonBtn = document.getElementById("format-json-body-btn");
    const timeoutInput = document.getElementById("request-timeout");

    // UI States
    const welcomeCard = document.getElementById("welcome-card");
    const loadingState = document.getElementById("loading-state");
    const errorCard = document.getElementById("error-card");
    const errorTitle = document.getElementById("error-title");
    const errorMessage = document.getElementById("error-message");
    const errorDetailsBox = document.getElementById("error-details-box");
    const errorDetailsPre = document.getElementById("error-details-pre");
    const resultsCard = document.getElementById("results-card");

    // Response display elements
    const resStatusBadge = document.getElementById("res-status-badge");
    const resStatusCategory = document.getElementById("res-status-category");
    const resTimeVal = document.getElementById("res-time-val");
    const resSizeVal = document.getElementById("res-size-val");
    const resCharCount = document.getElementById("res-char-count");
    const resContentType = document.getElementById("res-content-type");
    const resEncoding = document.getElementById("res-encoding");
    const redirectNotice = document.getElementById("redirect-notice");
    const redirectText = document.getElementById("redirect-text");

    const responseBodyPre = document.getElementById("response-body-pre");
    const bodyFormatBadge = document.getElementById("body-format-badge");
    const copyBodyBtn = document.getElementById("copy-body-btn");
    const resHeaderCount = document.getElementById("res-header-count");
    const resHeadersTbody = document.getElementById("res-headers-tbody");
    const reqHeadersTbody = document.getElementById("req-headers-tbody");
    const headerSearchInput = document.getElementById("header-search-input");

    const cnSummaryNote = document.getElementById("cn-summary-note");
    const cnStatusExplanation = document.getElementById("cn-status-explanation");

    // History & Navigation
    const historySidebar = document.getElementById("history-sidebar");
    const toggleHistoryBtn = document.getElementById("toggle-history-btn");
    const historyList = document.getElementById("history-list");
    const historyCountBadge = document.getElementById("history-count");
    const clearHistoryBtn = document.getElementById("clear-history-btn");

    // State Variables
    let currentResponseHeaders = [];
    let requestHistory = JSON.parse(localStorage.getItem("cn_http_history") || "[]");

    // -------------------------------------------------------------
    // Initial Setup
    // -------------------------------------------------------------
    updateHistoryUI();
    updateMethodColor();

    // Add one empty header row to begin with
    addHeaderRow("Accept", "*/*");

    // -------------------------------------------------------------
    // Method Selector Color Update
    // -------------------------------------------------------------
    function updateMethodColor() {
        methodSelect.className = `method-select method-${methodSelect.value}`;
    }
    methodSelect.addEventListener("change", updateMethodColor);

    // -------------------------------------------------------------
    // Header Row Management
    // -------------------------------------------------------------
    function addHeaderRow(key = "", val = "") {
        const row = document.createElement("div");
        row.className = "header-row";
        row.innerHTML = `
            <input type="text" class="header-input header-key" placeholder="Key (e.g. Authorization)" value="${escapeHtml(key)}">
            <input type="text" class="header-input header-val" placeholder="Value (e.g. Bearer token)" value="${escapeHtml(val)}">
            <button type="button" class="btn-icon delete-header-btn" title="Remove header">&times;</button>
        `;

        row.querySelector(".delete-header-btn").addEventListener("click", () => {
            row.remove();
            updateHeaderCount();
        });

        row.querySelectorAll("input").forEach(input => {
            input.addEventListener("input", updateHeaderCount);
        });

        headersContainer.appendChild(row);
        updateHeaderCount();
    }

    function updateHeaderCount() {
        const rows = headersContainer.querySelectorAll(".header-row");
        let activeCount = 0;
        rows.forEach(r => {
            const k = r.querySelector(".header-key").value.trim();
            if (k) activeCount++;
        });
        headerCountBadge.textContent = activeCount;
    }

    addHeaderRowBtn.addEventListener("click", () => addHeaderRow());

    function getCustomHeaders() {
        const headers = {};
        const rows = headersContainer.querySelectorAll(".header-row");
        rows.forEach(r => {
            const k = r.querySelector(".header-key").value.trim();
            const v = r.querySelector(".header-val").value.trim();
            if (k) {
                headers[k] = v;
            }
        });
        return headers;
    }

    // -------------------------------------------------------------
    // Tabs Navigation (Generic)
    // -------------------------------------------------------------
    document.querySelectorAll(".tabs-container").forEach(container => {
        const tabBtns = container.querySelectorAll(".tabs-header .tab-btn");
        tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetTabId = btn.getAttribute("data-tab");

                tabBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");

                container.querySelectorAll(".tab-content").forEach(content => {
                    if (content.id === targetTabId) {
                        content.classList.add("active");
                    } else {
                        content.classList.remove("active");
                    }
                });
            });
        });
    });

    // -------------------------------------------------------------
    // Quick Presets
    // -------------------------------------------------------------
    document.querySelectorAll(".preset-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const presetUrl = chip.getAttribute("data-url");
            const presetMethod = chip.getAttribute("data-method") || "GET";
            const presetBody = chip.getAttribute("data-body") || "";

            urlInput.value = presetUrl;
            methodSelect.value = presetMethod;
            updateMethodColor();

            if (presetBody) {
                requestBodyInput.value = presetBody;
                // Switch to body tab
                const bodyTabBtn = document.querySelector('[data-tab="tab-body"]');
                if (bodyTabBtn) bodyTabBtn.click();
            }

            // Automatically trigger request for smooth interactive demo
            sendRequest();
        });
    });

    // -------------------------------------------------------------
    // Beautify JSON in Request Body
    // -------------------------------------------------------------
    formatJsonBtn.addEventListener("click", () => {
        const text = requestBodyInput.value.trim();
        if (!text) return;
        try {
            const parsed = JSON.parse(text);
            requestBodyInput.value = JSON.stringify(parsed, null, 2);
        } catch (e) {
            alert("Invalid JSON: " + e.message);
        }
    });

    // -------------------------------------------------------------
    // Send Request Execution
    // -------------------------------------------------------------
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        sendRequest();
    });

    async function sendRequest() {
        const rawUrl = urlInput.value.trim();
        if (!rawUrl) {
            urlInput.focus();
            return;
        }

        const method = methodSelect.value;
        const customHeaders = getCustomHeaders();
        const bodyContent = requestBodyInput.value;
        const timeout = parseFloat(timeoutInput.value) || 10.0;

        // Try parsing body as JSON if possible
        let jsonData = null;
        if (bodyContent && ["POST", "PUT", "PATCH"].includes(method)) {
            try {
                jsonData = JSON.parse(bodyContent);
            } catch (e) {
                jsonData = null;
            }
        }

        // UI Loading State
        welcomeCard.style.display = "none";
        resultsCard.style.display = "none";
        errorCard.style.display = "none";
        loadingState.style.display = "block";

        sendBtn.disabled = true;
        btnText.style.display = "none";
        spinner.style.display = "inline-block";

        const startTime = performance.now();

        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    url: rawUrl,
                    method: method,
                    headers: customHeaders,
                    data: !jsonData && bodyContent ? bodyContent : null,
                    json_data: jsonData,
                    timeout: timeout
                })
            });

            const data = await response.json();
            loadingState.style.display = "none";

            if (!data.success) {
                renderError(data);
                saveToHistory(method, rawUrl, "Failed", data.error_type || "Error", Math.round(performance.now() - startTime));
            } else {
                renderSuccess(data);
                saveToHistory(
                    data.request.method,
                    data.request.url,
                    data.response.status_code,
                    data.response.status_reason,
                    data.timing.total_time_ms
                );
            }
        } catch (err) {
            loadingState.style.display = "none";
            renderError({
                error_type: "Network / Client Error",
                error_message: "Failed to communicate with local analyzer server.",
                details: err.message
            });
        } finally {
            sendBtn.disabled = false;
            btnText.style.display = "inline";
            spinner.style.display = "none";
        }
    }

    // -------------------------------------------------------------
    // Render Results
    // -------------------------------------------------------------
    function renderSuccess(data) {
        const resp = data.response;
        const req = data.request;
        const timing = data.timing;
        const insights = data.network_insights;

        // Status Badge & Category
        const sc = resp.status_code;
        resStatusBadge.textContent = `${sc} ${resp.status_reason}`;
        resStatusBadge.className = "status-badge";
        if (sc >= 200 && sc < 300) resStatusBadge.classList.add("status-2xx");
        else if (sc >= 300 && sc < 400) resStatusBadge.classList.add("status-3xx");
        else if (sc >= 400 && sc < 500) resStatusBadge.classList.add("status-4xx");
        else resStatusBadge.classList.add("status-5xx");

        resStatusCategory.textContent = resp.status_category;
        resTimeVal.textContent = timing.total_time_ms;
        resSizeVal.textContent = resp.content_length_human;
        resCharCount.textContent = `${resp.char_count} characters`;
        resContentType.textContent = resp.content_type;
        resEncoding.textContent = `Encoding: ${resp.encoding || "standard"}`;

        // Redirect Alert
        if (resp.is_redirect && resp.redirect_chain.length > 0) {
            redirectNotice.style.display = "flex";
            const hops = resp.redirect_chain.map(h => `${h.status_code} (${h.url})`).join(" -> ");
            redirectText.innerHTML = `<strong>Redirects Followed (${resp.redirect_chain.length}):</strong> ${hops} &rarr; Final URL: <code>${resp.final_url}</code>`;
        } else {
            redirectNotice.style.display = "none";
        }

        // Response Body
        const bodyContent = resp.body || "[Empty Response Body]";
        responseBodyPre.querySelector("code").textContent = bodyContent;
        bodyFormatBadge.textContent = resp.is_json ? "JSON (Formatted)" : (resp.content_type.split(";")[0] || "Plain Text");

        // Response Headers Table
        currentResponseHeaders = resp.headers_analyzed || [];
        resHeaderCount.textContent = currentResponseHeaders.length;
        renderHeadersTable(currentResponseHeaders);

        // Request Headers Sent Table
        reqHeadersTbody.innerHTML = "";
        const sentHeaders = resp.request_headers_sent || {};
        for (const [k, v] of Object.entries(sentHeaders)) {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><code>${escapeHtml(k)}</code></td>
                <td><code style="word-break: break-all;">${escapeHtml(v)}</code></td>
            `;
            reqHeadersTbody.appendChild(tr);
        }

        // CN Insights
        cnSummaryNote.textContent = insights.summary_note || "Request completed successfully.";
        cnStatusExplanation.innerHTML = `<strong>HTTP ${sc} (${resp.status_reason}):</strong> ${resp.status_description}`;

        resultsCard.style.display = "block";
        resultsCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function renderError(data) {
        errorTitle.textContent = data.error_type || "Request Failed";
        errorMessage.textContent = data.error_message || "An error occurred while executing the HTTP request.";

        if (data.details) {
            errorDetailsPre.textContent = data.details;
            errorDetailsBox.style.display = "block";
        } else {
            errorDetailsBox.style.display = "none";
        }

        errorCard.style.display = "block";
        errorCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    // -------------------------------------------------------------
    // Headers Filter / Search
    // -------------------------------------------------------------
    function renderHeadersTable(headersList) {
        resHeadersTbody.innerHTML = "";
        if (!headersList || headersList.length === 0) {
            resHeadersTbody.innerHTML = '<tr><td colspan="3" class="text-muted" style="text-align: center;">No headers returned.</td></tr>';
            return;
        }

        headersList.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><code>${escapeHtml(item.name)}</code></td>
                <td><code style="word-break: break-all;">${escapeHtml(item.value)}</code></td>
                <td class="header-desc">${escapeHtml(item.description)}</td>
            `;
            resHeadersTbody.appendChild(tr);
        });
    }

    headerSearchInput.addEventListener("input", (e) => {
        const term = e.target.value.toLowerCase().trim();
        if (!term) {
            renderHeadersTable(currentResponseHeaders);
            return;
        }
        const filtered = currentResponseHeaders.filter(h => 
            h.name.toLowerCase().includes(term) ||
            h.value.toLowerCase().includes(term) ||
            h.description.toLowerCase().includes(term)
        );
        renderHeadersTable(filtered);
    });

    // -------------------------------------------------------------
    // Copy Body Button
    // -------------------------------------------------------------
    copyBodyBtn.addEventListener("click", () => {
        const text = responseBodyPre.querySelector("code").textContent;
        navigator.clipboard.writeText(text).then(() => {
            const originalHtml = copyBodyBtn.innerHTML;
            copyBodyBtn.innerHTML = `
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg> Copied!
            `;
            setTimeout(() => {
                copyBodyBtn.innerHTML = originalHtml;
            }, 1800);
        });
    });

    // -------------------------------------------------------------
    // History Management
    // -------------------------------------------------------------
    function saveToHistory(method, url, status, reason, timeMs) {
        const record = {
            id: Date.now(),
            method: method,
            url: url,
            status: status,
            reason: reason,
            time: timeMs,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        // Keep max 20 items
        requestHistory.unshift(record);
        if (requestHistory.length > 20) requestHistory.pop();
        localStorage.setItem("cn_http_history", JSON.stringify(requestHistory));
        updateHistoryUI();
    }

    function updateHistoryUI() {
        historyCountBadge.textContent = requestHistory.length;
        if (requestHistory.length === 0) {
            historyList.innerHTML = '<div class="empty-hint">No recent requests recorded.</div>';
            return;
        }

        historyList.innerHTML = "";
        requestHistory.forEach(item => {
            const div = document.createElement("div");
            div.className = "history-item";
            div.innerHTML = `
                <div class="history-item-top">
                    <span class="badge method-${item.method}" style="font-weight: 700;">${item.method}</span>
                    <span style="font-size: 0.75rem; font-weight: 600; color: ${item.status === 'Failed' ? '#f87171' : '#34d399'};">
                        ${item.status} ${item.reason}
                    </span>
                </div>
                <div class="history-url" title="${escapeHtml(item.url)}">${escapeHtml(item.url)}</div>
                <div class="history-meta">
                    <span>${item.time} ms</span>
                    <span>${item.timestamp}</span>
                </div>
            `;
            div.addEventListener("click", () => {
                urlInput.value = item.url;
                methodSelect.value = item.method;
                updateMethodColor();
                sendRequest();
            });
            historyList.appendChild(div);
        });
    }

    clearHistoryBtn.addEventListener("click", () => {
        if (confirm("Clear all request history?")) {
            requestHistory = [];
            localStorage.removeItem("cn_http_history");
            updateHistoryUI();
        }
    });

    toggleHistoryBtn.addEventListener("click", () => {
        historySidebar.classList.toggle("collapsed");
    });

    // Modal Close
    document.getElementById("close-modal-btn").addEventListener("click", () => {
        window.location.hash = "";
    });

    // Helper: Escape HTML
    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
