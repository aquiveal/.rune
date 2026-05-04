---
name: cloakbrowser
description: "Stealth Chromium automation library with source-level C++ fingerprint patches for bypassing bot detection in Playwright and Puppeteer."
---
# System Context Map

#### 1. Tech Stack & I/O Boundaries
- **Tech Stack:** Python (Playwright, httpx) | TypeScript (Playwright-core, Puppeteer-core) | Custom Chromium (C++ Patches).
- **Ingress/Egress (I/O):** 
  - **Ingress:** Python/JS API calls (`launch()`, `launchContext()`) -> Environment Variables (`CLOAKBROWSER_BINARY_PATH`, `CLOAKBROWSER_CACHE_DIR`).
  - **Egress:** Custom Chromium process execution -> HTTP/SOCKS5 Proxies -> CDP (Chrome DevTools Protocol) WebSockets (Port 9222+).
  - **Updates:** Background version checks against `cloakbrowser.dev` or GitHub API.

#### 2. Domain & Data Model (The Nouns)
- `Browser` (Location: `cloakbrowser/browser.py` | `js/src/playwright.ts`) 
  - **Concept:** Stealth-patched Chromium instance.
- `BrowserContext` (Location: `cloakbrowser/browser.py` | `js/src/playwright.ts`)
  - **Concept:** Isolated session; can be ephemeral (incognito) or persistent.
- `Fingerprint` (Location: `cloakbrowser/config.py` | `js/src/config.ts`)
  - **Concept:** Deterministic identity (GPU, Screen, WebGL) derived from a master `--fingerprint` seed.
- `HumanConfig` (Location: `cloakbrowser/human/config.py` | `js/src/human/config.ts`)
  - **Concept:** Parameters for human-like behavior (typing delay, mouse curves).

#### 3. Component & Directory Matrix (The Map)
- `/modules/cloakbrowser/` -> Python wrapper core (Sync/Async).
- `/modules/js/src/` -> Node.js wrapper core (TypeScript).
- `/modules/cloakbrowser/human/` & `/modules/js/src/human/` -> Behavioral patching logic (CDP interception).
- `modules/bin/cloakserve` -> CDP multiplexer; routes connections to per-seed browser processes.
- `modules/bin/cloaktest` -> Diagnostic tool for verifying stealth against live detection sites.
- `modules/examples/` -> Reference implementations for AI agents (browser-use, Crawl4AI).

#### 4. Execution Lifecycles (The Verbs)
- **Path: Launching a Stealth Session**
  1. User calls `launch()` in Python or JS wrapper.
  2. `ensure_binary()` verifies/downloads custom Chromium binary to `~/.cloakbrowser`.
  3. `build_args()` generates CLI flags: `--fingerprint={seed}` + platform-specific overrides.
  4. Wrapper starts Chromium with `ignoreDefaultArgs=['--enable-automation', '--enable-unsafe-swiftshader']`.
  5. (If `humanize=True`) `patch_browser()` wraps CDP methods to inject Bézier curves and typing delays.
- **Path: CDP Multiplexing (`cloakserve`)**
  1. `cloakserve` starts an Aiohttp server on port 9222.
  2. Client connects with `?fingerprint=12345` query param.
  3. `ChromePool` spawns/retrieves a Chromium process pinned to that seed.
  4. `cloakserve` proxies WebSocket traffic between the client and the specific Chromium process.

#### 5. Distilled Documentation & Workflows (How to Build)
- **Workflow: Adding a new Stealth Arg:**
  1. Add flag mapping to `build_args` in `cloakbrowser/browser.py` and `js/src/args.ts`.
  2. Define default values in `cloakbrowser/config.py` and `js/src/config.ts`.
- **Workflow: Implementing Human Interaction Patching:**
  1. Create logic in `human/` subfolder (e.g., `mouse.py` / `mouse.ts`).
  2. Intercept the target Playwright/Puppeteer method in `human/__init__.py` / `human/index.ts`.
  3. Ensure the patch falls back to `_original` for raw speed if needed.

#### 6. Coding Conventions & Guardrails
- **Behavioral Stealth:** Use `page.type()` instead of `page.fill()` to trigger keyboard events.
- **CDP Leak Prevention:** NEVER use `page.waitForTimeout()` (detected by reCAPTCHA); use native `time.sleep()` or `setTimeout`.
- **Location Matching:** Always use `geoip=True` when using proxies to synchronize Timezone/Locale with the proxy IP.
- **Persistence:** Use `launch_persistent_context()` to bypass incognito detection and maintain sessions.

#### 7. Project-Specific Vocabulary
- **Source-Level Patch:** C++ modifications in the Chromium binary itself, preventing detection without JS injection.
- **Fingerprint Seed:** A numeric seed (`--fingerprint`) that creates a unique, consistent browser identity.
- **Humanize:** The process of overlaying human-like mechanical noise on top of automated CDP commands.
- **Patchright:** An alternative backend that suppresses additional CDP signals at the protocol layer.
