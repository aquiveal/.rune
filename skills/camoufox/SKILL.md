# Camoufox

> [!NOTE] Agent Context: The source code for this skill is co-located in the modules/ directory.


#### 1. System Essence & Stack
- **Purpose:** Camoufox is a modified Firefox fork optimized for AI agents, web scraping, and stealth automation. It patches the browser's C++ core to evade bot detection by masking automation hooks (like Playwright/Juggler) and dynamically rotating realistic device fingerprints.
- **Tech Stack:**
  - **Core/Browser:** C++, Firefox source codebase
  - **Automation Tooling:** Python 3, Playwright
  - **Fingerprint Generation:** `browserforge`
  - **Build System:** Python scripts, `make`, Docker
- **Build/Run Commands:**
  - Build Environment Setup: `make bootstrap`, `make dir`
  - Build Browser: `python3 multibuild.py --target linux windows macos --arch x86_64 arm64`
  - Developer Tools (Patch Management): `make edits`
  - Run Tests: `make tests`

#### 2. Architectural Map (Where to find things)
- `modules/pythonlib/camoufox/` -> Python Playwright wrappers, fingerprint generation, and API interfaces.
- `modules/patches/` -> Core C++ diff patches applied to the Firefox source to spoof fingerprints, evade detection, and sandbox Playwright.
- `modules/scripts/` -> Build system scripts, packaging tools, and the developer UI (`developer.py`).
- `modules/settings/` -> Custom browser configurations (`camoufox.cfg`, `properties.json`) and minimal UI styling.
- `modules/tests/` -> Playwright test suite for validating stealth and features.
- **Entry Points:**
  - **Python API (Sync):** `modules/pythonlib/camoufox/sync_api.py`
  - **Python API (Async):** `modules/pythonlib/camoufox/async_api.py`
  - **Build System CLI:** `modules/multibuild.py`

#### 3. Execution Flow & Lifecycle (How it works)
Standard lifecycle for a Camoufox Playwright automation session:
- **Step 1:** Starts in `modules/pythonlib/camoufox/sync_api.py` (or `async_api.py`) via the `Camoufox()` context manager.
- **Step 2:** `launch_options()` prepares Firefox CLI arguments, custom user profiles, and extensions (e.g., uBlock Origin).
- **Step 3:** For a new context, `generate_context_fingerprint()` in `modules/pythonlib/camoufox/fingerprints.py` generates a realistic device profile (using `browserforge` or predefined presets), including unique seeds for Canvas/Audio spacing.
- **Step 4:** Playwright launches the patched `camoufox` executable. The Python wrapper injects the spoofed properties via `addInitScript` so they self-destruct before page execution. The patched C++ core utilizes these seeds to emulate a human browser seamlessly.

#### 4. Project-Specific Vocabulary (What is what)
- **BrowserForge:** A library used to generate statistically realistic browser fingerprints (OS, User-Agent, screen dimensions). Integrated in `modules/pythonlib/camoufox/fingerprints.py`.
- **Juggler:** The custom automation protocol inside Firefox that Playwright uses. Camoufox heavily patches Juggler to sandbox Playwright code from page scripts, hiding automation traces.
- **Developer UI:** A local GUI started via `make edits` (`modules/scripts/developer.py`) used to create and manage `.patch` files against the Firefox source safely.
- **Virtual Display:** Handled by `modules/pythonlib/camoufox/virtdisplay.py` to run headful Firefox mode in environments without a physical display (like headless servers) to bypass headless detection.

#### 5. Documentation & Source Code Navigation Rules
- **Docs Location:** High-level project README at `modules/README.md`. Extended documentation at `camoufox.com`.
- **Search Heuristics:** To find how a specific browser property is spoofed, search in `modules/patches/` for `.patch` files (e.g., `webgl-spoofing.patch`). Do not search for JS-based spoofing, as it is primarily done in C++.
- **State Management:** Fingerprint states are tied to Playwright `BrowserContexts` via `modules/pythonlib/camoufox/fingerprints.py` and are injected on context initialization. Firefox core state modifications are applied via C++ patches.
- **Error Handling:** Python exceptions (like `InvalidProxy`) are defined in `modules/pythonlib/camoufox/exceptions.py`. Build errors halt execution and are printed to stderr in `modules/multibuild.py`.

#### 6. Anti-Patterns & Strict Boundaries
- **Never modify Firefox source directly:** Always use `make edits` to create/update `.patch` files in `modules/patches/`. Do not edit the raw source tree (e.g., `camoufox-*/` directories) directly without extracting changes into a patch.
- **Do not rely on JS injection for stealth:** Fingerprints and spoofing must occur at the C++ patch level or self-destruct via `addInitScript()`. Never leave persistent JS variables or prototype modifications in the page scope where bot protection scripts can detect them.
- **Do not use standard CDP detection evasion:** Camoufox uses a patched Juggler, not Chrome DevTools Protocol (CDP). Standard Playwright Chromium evasion techniques (e.g., `puppeteer-extra-plugin-stealth`) are redundant and potentially harmful here.
- **Never bypass the virtual display for headless operation:** If headless mode leaks, always fall back to the Virtual Display buffer (`headless='virtual'`) instead of standard headless arguments.
