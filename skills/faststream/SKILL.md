---
name: faststream
description: Context and guidelines for working with the FastStream framework skill
---
# faststream

> [!NOTE] 
> Agent Context: The source code for this skill is co-located in the `modules/` directory.

## 1. Project Overview
FastStream is a modern, high-performance Python framework for building asynchronous message-centric microservices. It provides a unified API across multiple message brokers (Kafka, RabbitMQ, NATS, Redis, MQTT) with built-in serialization (Pydantic, Msgspec), automatic AsyncAPI documentation generation, and robust dependency injection powered by `FastDepends`. 

## 2. Directory Structure and Core Architecture
The framework source code and supporting files are located under `modules/`:

- **`modules/faststream/`**: The core framework package.
  - `app.py`: Defines the `FastStream` application class. It coordinates lifecycle events, hooks (`on_startup`, `on_shutdown`), and manages the broker instances.
  - `_internal/`: Core underlying mechanics. This is where cross-broker generic logic lives.
    - `application.py`: Contains `StartAbleApplication` and `Application` bases.
    - `broker/broker.py`: Defines the abstract `BrokerUsecase` which handles connections, publishers, subscribers, and dependency injection setup.
    - `di/`: Integrations with `FastDepends`.
    - `parser.py` / `proto.py`: Abstract definitions for message parsing and codecs.
  - **Brokers (`redis/`, `kafka/`, `rabbit/`, `nats/`, `mqtt/`)**: Broker-specific implementations.
    - `broker/broker.py`: Inherits from `BrokerUsecase` and a specific `Registrator` (e.g., `RedisBroker`).
    - `publisher/`: Producer/publish implementations specific to the broker's client.
    - `subscriber/`: Consumer/subscription implementations specific to the broker's client.
    - `parser/`: Broker-specific message decoding and parsing logic.
  - `middlewares/`: Base interfaces for middlewares (e.g., logging, exception handling, acknowledgment policies). The middleware pipeline handles requests before they reach the handler.
  - `opentelemetry/` & `prometheus/`: Integrations for observability.
- **`modules/docs/`**: MkDocs documentation and source files. The primary user documentation is built from here.
  - `mkdocs.yml`: Configuration for the documentation site.
  - `docs_src/`: Contains markdown files and actual runnable code examples that are injected into the docs.
- **`modules/tests/`**: Comprehensive Pytest suite covering all brokers, ASGI integration, and utilities.
- **`modules/benchmarks/`**: Performance benchmarks using CodSpeed.

## 3. Key Concepts & Execution Flow

- **Message Lifecycle Flow**:
  1. **Broker Client** receives a raw message bytes/string.
  2. **Parser/Codec** decodes the raw message into a standardized broker-specific Message object (e.g., `RedisMessage`).
  3. **Middleware Pipeline** processes the message (logging, telemetry, exceptions).
  4. **FastDepends DI** resolves dependencies and type-casts the payload using Pydantic V1/V2 or Msgspec based on handler annotations.
  5. **Handler Function** executes the core business logic.
  6. **Publisher** routes the returned response to the appropriate topic/channel if `@broker.publisher` is used.

- **Unified but Extensible API**: FastStream provides high-level decorators `@broker.subscriber()` and `@broker.publisher()`. However, the API supports native features of each broker via specific kwargs.
- **Dependency Injection**: Use `Depends`, `Context`, and `Header` for DI in message handlers. The `ContextRepo` manages both global and local contexts.
- **Automatic AsyncAPI**: The `schema` is attached to the Application and updated dynamically. Documentation generation is built-in.

## 4. Development & Tooling Standards

- **Environment & Dependency Management**: 
  - The repository utilizes a `justfile` and `uv` for local orchestration and testing.
  - Standard user instructions dictate: **Always use PDM with uv mode** for Python code you write. However, for executing existing repository scripts within `modules/`, leverage the `just` commands.
- **Testing**: 
  - **In-Memory Testing**: Use `TestBroker` context managers (e.g., `TestKafkaBroker`, `TestRedisBroker`) to patch real brokers for fast, infrastructure-free testing. Tests utilizing this should be marked with `pytest.mark.asyncio`.
  - **Running Tests**: The `justfile` contains commands like `just test` (runs fast, unconnected tests) and `just test-all`. Tests are categorized by marks (e.g., `-m "not slow and not connected"`).
- **Code Quality & Pre-commit**: 
  - The project uses `ruff` (formatting and linting), `mypy` (strict typing), `codespell`, and `bandit`.
  - Use `just lint` and `just static-analysis` to verify code quality.
  - Ensure all code is fully type-annotated (`strict = true`). Use `if TYPE_CHECKING:` blocks generously.
- **Async Concurrency**: FastStream uses `anyio` for cross-platform asynchronous task groups, sleeps, and timeouts. Prefer `anyio` primitives over raw `asyncio` to maintain compatibility across `asyncio` and `trio`.
- **Documentation Building**: The documentation uses MkDocs with plugins like `mkdocs-material` and `mkdocstrings`. Use `just docs-serve` to live-preview the docs locally, `just docs-build` to build them, and `just docs-build-api` to generate API references.

## 5. Coding Agent Instructions

When implementing new features, fixing bugs, or refactoring code in this repository:
1. **Locate the Right Layer**: Determine if the feature is a core framework capability (goes in `_internal/`) or a broker-specific feature (goes in `{broker}/`).
2. **Mirror Features**: When adding a feature to the unified API, ensure it is cleanly supported across all broker implementations, or properly abstracted.
3. **Follow the Justfile**: Use `just linter` and `just test` before finalizing code. Do not circumvent the pre-commit hooks configured in `.pre-commit-config.yaml`.
4. **Write Robust Tests**: Always add or update tests in `modules/tests/`. Ensure both the real broker integration tests and the `TestBroker` mock tests pass. Use the appropriate Pytest markers.
5. **Update Documentation & Examples**: For user-facing API changes, update the relevant markdown files in `modules/docs/`. If creating code examples, put them in `modules/docs/docs_src/`. These snippets are often included directly into the markdown files to guarantee the docs are always tested and runnable. Use `just docs-serve` to ensure your documentation renders correctly.
6. **Handle Exceptions Gracefully**: Utilize FastStream's exception handling and middleware pipeline to ensure broker connections recover or shutdown cleanly.
