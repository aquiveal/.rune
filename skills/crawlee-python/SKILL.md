---
name: crawlee-python
description: Complete encyclopedia for the Crawlee Python system. Contains full directory topography, file dictionaries, docs summaries, and workflows. Trigger this whenever working on any part of this codebase.
---

# Crawlee Python Complete Encyclopedia

## Table of Contents
1. System Overview
2. Documentation Dictionary
3. Complete Codebase Topography
4. Module & File Dictionary
5. Core Data Flows & Workflows
6. Global Conventions & Anti-Patterns

## 1. System Overview
*   **App Purpose:** Crawlee is a web scraping and browser automation library for Python. It provides a unified interface for HTTP and headless browser crawling, automatic parallel crawling, retries, proxy rotation, and pluggable storage.
*   **Tech Stack Details:** 
    *   Language: Python (with strict type hints)
    *   Core Libraries: `asyncio`, `httpx` (HTTP client), `beautifulsoup4` (HTML parsing), `playwright` (headless browser automation), `parsel` (optional parsing)
    *   Storage Clients: Memory, File System, Redis, SQL
    *   Testing: `pytest`, `codecov`
    *   Documentation: Docusaurus (React/TypeScript for the website)
    *   Package Management: `uv`, `pyproject.toml`
*   **Environment Variables Needed:** 
    *   `CRAWLEE_STORAGE_DIR`: Directory for local storage (default: `./storage`)
    *   `CRAWLEE_DEFAULT_DATASET_ID`: Default dataset ID
    *   `CRAWLEE_DEFAULT_KEY_VALUE_STORE_ID`: Default key-value store ID
    *   `CRAWLEE_DEFAULT_REQUEST_QUEUE_ID`: Default request queue ID
    *   `CRAWLEE_LOG_LEVEL`: Logging level (e.g., `INFO`, `DEBUG`)

## 2. Documentation Dictionary
*An exhaustive summary of all relevant documentation so the LLM knows what external rules apply.*

*   **[Crawlee Python Documentation]**
    *   *Link:* `https://crawlee.dev/python/`
    *   *Summary:* Official documentation covering setup, guides, and API reference.
    *   *Key Constraints:* Use `asyncio` for all operations. Prefer `BeautifulSoupCrawler` for static pages and `PlaywrightCrawler` for dynamic/JS-heavy pages.
*   **[Apify SDK Documentation]**
    *   *Link:* `https://docs.apify.com/sdk/python/`
    *   *Summary:* Guide for deploying Crawlee scrapers to the Apify platform.
*   **[Playwright Python Documentation]**
    *   *Link:* `https://playwright.dev/python/docs/intro`
    *   *Summary:* Underlying browser automation library used by `PlaywrightCrawler`.

## 3. Complete Codebase Topography
*The exhaustive ASCII tree of the project structure so the LLM can visually parse the architecture.*

```text
crawlee-python/
├── modules/
│   ├── docs/                     # Markdown documentation files
│   ├── src/
│   │   └── crawlee/              # Core library source code
│   │       ├── _autoscaling/     # Autoscaling pool and system status
│   │       ├── _utils/           # Utility functions (crypto, file, log, etc.)
│   │       ├── browsers/         # Browser controllers (Playwright, Stagehand)
│   │       ├── crawlers/         # Crawler implementations (BeautifulSoup, Playwright, etc.)
│   │       ├── events/           # Event management system
│   │       ├── fingerprint_suite/# Browser fingerprinting
│   │       ├── http_clients/     # HTTP client wrappers (httpx, curl_impersonate)
│   │       ├── otel/             # OpenTelemetry instrumentation
│   │       ├── project_template/ # CLI templates for new projects
│   │       ├── request_loaders/  # Request queues and lists
│   │       ├── sessions/         # Session management and rotation
│   │       ├── statistics/       # Error tracking and statistics
│   │       ├── storage_clients/  # Storage backends (Memory, FileSystem, Redis, SQL)
│   │       └── storages/         # High-level storage APIs (Dataset, KeyValueStore, RequestQueue)
│   ├── tests/                    # Unit and integration tests
│   └── website/                  # Docusaurus website source code
├── pyproject.toml                # Python project configuration
└── uv.lock                       # Dependency lockfile
```

## 4. Module & File Dictionary
*The exhaustive index of what lives where.*

### `modules/src/crawlee/crawlers/` (Crawler Implementations)
*   `_beautifulsoup/_beautifulsoup_crawler.py`: Implements `BeautifulSoupCrawler` for fast, HTTP-based scraping using `httpx` and `beautifulsoup4`.
*   `_parsel/_parsel_crawler.py`: Implements `ParselCrawler` for scraping using XPath and CSS selectors via the `parsel` library.
*   `_http/_http_crawler.py`: Implements `HttpCrawler` for raw HTTP requests without automatic HTML parsing.
*   `_adaptive_playwright/_adaptive_playwright_crawler.py`: Implements `AdaptivePlaywrightCrawler` which tries HTTP first and falls back to Playwright if rendering is needed.
*   `_basic/_basic_crawler.py`: Base class for all crawlers, handling the main crawling loop, concurrency, and request routing.
*   `_stagehand/_stagehand_crawler.py`: Crawler using Stagehand for AI-driven browser automation.

### `modules/src/crawlee/storage_clients/` (Storage Backends)
*   `_memory/`: In-memory storage client (default for testing).
*   `_file_system/`: Local file system storage client (default for local runs, saves to `./storage`).
*   `_redis/`: Redis-backed storage client for distributed crawling.
*   `_sql/`: SQL-backed storage client (e.g., SQLite, PostgreSQL).

### `modules/src/crawlee/storages/` (High-Level Storage APIs)
*   `Dataset`: For storing tabular data (like CSV/JSON rows).
*   `KeyValueStore`: For storing files, images, or arbitrary JSON objects.
*   `RequestQueue`: For managing the queue of URLs to crawl, ensuring uniqueness and handling retries.

### `modules/src/crawlee/router.py` (Request Routing)
*   `Router`: Decorator-based router for directing requests to specific handler functions based on URL patterns or labels. Supports `router.use()` for middleware, `error_handler` for recoverable errors, and `failed_request_handler` for permanent failures. Also supports pre-navigation hooks.

### `modules/src/crawlee/sessions/` (Session Management)
*   `SessionPool`: Manages rotation of proxy IP addresses, cookies, and custom settings. Filters out blocked/non-functional proxies and ensures even IP rotation.
*   `Session`: Represents a single session with its own cookies and proxy.

### `modules/src/crawlee/proxy_configuration.py` (Proxy Management)
*   `ProxyConfiguration`: Manages proxy URLs, including tiered proxies (falling back to more expensive proxies only when needed) and session-based proxy rotation.

## 5. Core Data Flows & Workflows

### Flow 1: Basic Crawling Loop
1. **Initialization:** User creates a `Crawler` instance (e.g., `BeautifulSoupCrawler`) and defines a `Router` with handlers.
2. **Run:** User calls `crawler.run(['https://example.com'])`.
3. **Queueing:** The initial URLs are added to the `RequestQueue`.
4. **Fetching:** The `AutoscaledPool` pulls requests from the queue and assigns them to workers.
5. **Processing:** The crawler fetches the page (via HTTP or Browser) and creates a `CrawlingContext`.
6. **Handling:** The `Router` matches the request to a handler function and executes it.
7. **Extraction & Storage:** The handler extracts data and calls `context.push_data()` to save it to the `Dataset`.
8. **Link Enqueueing:** The handler calls `context.enqueue_links()` to find new URLs and add them to the `RequestQueue`.
9. **Completion:** The loop continues until the `RequestQueue` is empty or `max_requests_per_crawl` is reached.

### Flow 2: Storage Client Resolution
1. When a storage (Dataset, KVS, RQ) is accessed, Crawlee checks the `Configuration`.
2. If a specific storage client is configured, it uses that.
3. Otherwise, it defaults to `MemoryStorageClient` (if running in memory) or `FileSystemStorageClient` (if running locally).

## 6. Global Conventions & Anti-Patterns

### Coding Rules
*   **Asynchronous Programming:** ALWAYS use `async`/`await` for I/O operations (fetching, storing, sleeping).
*   **Type Hinting:** Strict type hinting is mandatory. Use `typing` module extensively.
*   **Context Usage:** Always use the `CrawlingContext` provided to the handler for logging, storing data, and enqueueing links. Do not use global state.
*   **Error Handling:** Let the crawler handle transient errors. It will automatically retry failed requests. Use `error_handler` for custom recovery logic and `failed_request_handler` for permanent failures.
*   **Session Management:** Use `SessionPool` to manage cookies and proxy rotation to avoid IP blocking. Bind requests to specific sessions using `session_id` when authentication is required.
*   **Storage Cleanup:** Unnamed storages are automatically purged at the start of each run (`purge_on_start=True`). Named storages persist across runs.

### Anti-Patterns (NEVER DO THIS)
*   ❌ **Blocking I/O:** Never use synchronous libraries like `requests` or `urllib` inside a crawler handler. Always use the provided async HTTP client or browser.
*   ❌ **Manual Queue Management:** Never try to manually manage the list of URLs to visit. Always use `context.enqueue_links()` or `context.add_requests()`.
*   ❌ **Hardcoded Storage Paths:** Never hardcode paths to save files. Always use `context.push_data()` or `context.get_key_value_store().set_value()`.
