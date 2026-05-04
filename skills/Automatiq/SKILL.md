---
name: automatiq
description: Reverse-engineers a recorded browser session into a Python automation script.
---

# Automatiq

> [!NOTE] Agent Context: The source code for this skill is co-located in the `modules/` directory.

Automatiq is a CLI tool that watches you browse the web, records the session (network requests, user actions, and video), and then uses an AI agent to reverse-engineer that session into a standalone Python automation/extraction script. It applies the philosophy of "breaking things apart and building them back up" to bypass browser fingerprinting by extracting the raw requests, avoiding headless browsers whenever possible.

This `SKILL.md` serves as a comprehensive developer guide and context map for agents working on the codebase.

## Codebase Architecture & Key Modules

The codebase is located in `modules/src/automatiq/` and is divided into several sub-packages.

### 1. CLI Entry & Setup (`modules/src/automatiq/`)
- [`__main__.py`](modules/src/automatiq/__main__.py): The main entry point. It handles CLI argument parsing, background module preloading (to speed up startup), and sets up `config.py` overrides. Exposes commands: `record`, `agent`, and `run` (record + agent).
- [`cli/`](modules/src/automatiq/cli/): Contains UI and CLI orchestrator code using `rich`.
  - [`console.py`](modules/src/automatiq/cli/console.py): Logging setup, spinners, and customized rich layouts.
  - [`orchestrator.py`](modules/src/automatiq/cli/orchestrator.py): Binds CLI UI rendering to the internal `events.py` signals.
  - [`automatiq_banner.py`](modules/src/automatiq/cli/automatiq_banner.py): The terminal startup animation.

### 2. The Recorder Phase (`modules/src/automatiq/core/recorder/`)
Responsible for recording the user's browser session and compiling it into an AI-friendly workspace dump.
- [`browser_agent.py`](modules/src/automatiq/core/recorder/browser_agent.py): Uses `zendriver` (CDP) to launch Chrome and inject JavaScript (from `js/telemetry.js` and `js/visuals.js`) to capture user interactions (clicks, inputs) and raw network requests/responses.
- [`video_recorder.py`](modules/src/automatiq/core/recorder/video_recorder.py): Uses `mss` to capture screen frames and `imageio-ffmpeg` to encode them into video.
- [`data_compressor.py`](modules/src/automatiq/core/recorder/data_compressor.py): The compilation phase. It splits the full video into short clips around each user action, uses a Vision-Language Model (`RECORDER_AI_MODEL`) to annotate the clips, uses `Magika` to detect content types, and dumps the structured result to `output/workspace/session_dump/`.
- [`blocklist_db.py`](modules/src/automatiq/core/recorder/blocklist_db.py): Prevents tracking/ad requests from bloating the dump.

### 3. The Agent Phase (`modules/src/automatiq/core/`)
Responsible for acting as the "Investigator" LLM. It interacts with an IPython sandbox to read the dumped data and progressively build a script.
- [`main.py`](modules/src/automatiq/core/main.py): The core agent loop. It manages the interaction between the user, the LLM (`litellm`), and the sandbox. It enforces safety limits (loop detection, script bouncing if submitted outside building mode) and outputs session histories as compressed YAMLs.
- [`agent.py`](modules/src/automatiq/core/agent.py): Contains the **system prompt** and the definitions of the 3 fundamental modes:
  - **Reading Mode**: The default. Used to explore `session_dump`, grep files, and trace how tokens/cookies are generated.
  - **Testing Mode**: Used to test specific hypothesis against the live site in the sandbox (one at a time).
  - **Building Mode**: Used to assemble the verified pieces into the final script.
- [`schema.py`](modules/src/automatiq/core/schema.py): Defines the Pydantic models for Agent structured outputs (using `instructor`), such as `AgentStep`, `AssistantResponse`, and `ToolEnum`.
- [`prompt.py`](modules/src/automatiq/core/prompt.py): The `PromptFactory` and manager that formats the agent memory before sending it to the LLM.
- [`events.py`](modules/src/automatiq/core/events.py): A `blinker`-based event bus used to decouple the core logic from the CLI UI.

### 4. IPython Sandbox (`modules/src/automatiq/core/ipython_sandbox/`)
An isolated, persistent environment where the agent executes Python code and shell commands.
- [`sandbox.py`](modules/src/automatiq/core/ipython_sandbox/sandbox.py): The main interface. Handles starting the worker, `%reset`, `%restore`, and `%view_output` commands. Implements soft/hard timeouts for misbehaving code.
- [`worker.py`](modules/src/automatiq/core/ipython_sandbox/worker.py): Runs in a separate process via `multiprocessing`. Sets up an `IPython` interactive shell, captures standard output/error, and exposes shell commands (like `!rg`, `!jq`, `!cat`).

---

## Session Dump Structure

When the Recorder completes, the agent reads from `output/workspace/session_dump/`. This directory structure is critical context for building scripts:

```text
session_dump/
├── SUMMARY.json              # High-level metadata, statistical breakdown, and AI chronological summary of actions
├── session_metadata.json     # Basic recording setup info
├── timeline.json             # Interleaved sequence of user_actions (with AI vision annotations) and network_requests
├── clips/                    # MP4 video clips sliced around each user action
└── requests/                 # One folder per network transaction (e.g., 000_GET_example.com)
    └── transaction.json      # Complete headers, timings, HTTP status, and AI content flags
    └── req_payload.*         # The request body (if any), file extension guessed by Magika
    └── res_body.*            # The response body (if any)
```

**Agent Philosophy:** Always read `SUMMARY.json` and `timeline.json` first. Do not guess dynamic tokens—find them in the dump using shell commands like `rg` or `jq`.

---

## Technical Tooling Standards

When modifying Automatiq, you MUST adhere to the following tools and conventions:

- **Dependency Management:** The project uses `uv` in PDM-like mode (configured via `pyproject.toml` and `uv.lock`). 
  - Install dependencies and setup environment: `uv sync`
  - Add dependencies: `uv add <package>` (or `uv add --dev <package>`)
- **Testing:** Uses `pytest`. Run tests using `uv run pytest`.
- **Linting & Formatting:** Uses `ruff`.
  - Format code: `uv run ruff format`
  - Lint code: `uv run ruff check`
- **Execution:** Run the local instance of the cli during development using `uv run automatiq`.
- **Python Version:** 3.11+.

## Development Tips

1. **State Cancellation:** `CancelToken` and `StopToken` (`modules/src/automatiq/core/cancel_standard.py`) are passed deeply down the call stack. Always respect them in blocking/async functions to ensure `Ctrl+C` works properly.
2. **Event Emitting:** Never put `print()` statements inside `src/automatiq/core/*`. Instead, emit events via `events.py` (e.g., `events.log_info.send("core", text="Hello")`), which are caught by `cli/orchestrator.py` to render via Rich.
3. **Sandbox Updates:** If you add a system binary (like busybox or sd) or change how IPython works, it should be updated in `core/ipython_sandbox/worker.py`.
4. **Pydantic / Instructor:** Automatiq uses `litellm` and `instructor` to enforce JSON schema responses. Any changes to the LLM's available tools require updating `schema.py`.
