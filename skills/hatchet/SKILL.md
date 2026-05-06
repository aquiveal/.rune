# hatchet

Operational guide for AI agents to interact with and manage the Hatchet task engine.

## 1. Define Clear Boundaries

### Scope
- **API Usage**: Interacting with the Hatchet REST/gRPC API for lifecycle management of workflows and tasks.
- **CLI Workflows**: Using `hatchet-cli` for environment setup, local development, and observability.
- **Worker Management**: Implementing, registering, and monitoring workers across Go, TypeScript, and Python.
- **Workflow Orchestration**: Defining DAGs, durable tasks, and scheduled runs.
- **Infrastructure**: Managing core dependencies (PostgreSQL for durability, RabbitMQ for messaging).

### Agent Context
Before applying this logic, the agent must have:
- Access to the project root containing `modules/`.
- Valid API credentials (Token) or a pre-configured CLI profile.
- Knowledge of the target tenant ID.

---

## 2. Structural Overview

### Mental Map
Hatchet uses a **Dispatcher-Worker** model with **Postgres** as the source of truth for durability.

- **Tenant**: Primary isolation unit. All resources (Workflows, Workers, Events) are tenant-scoped.
- **Workflow**: Definition of logic. Composed of one or more **Jobs**.
- **Job**: A set of **Steps** that run sequentially or in parallel (DAG).
- **Step (Task)**: The atomic unit of work assigned to a worker.
- **Worker**: A client process that registers capabilities (Actions) with the Dispatcher.
- **Dispatcher**: Engine component that manages worker heartbeats and assigns `AssignedAction` items via gRPC streams.
- **Event**: An ingested signal (`event_key` + `payload`) that can trigger workflow runs.

### Component Entry Points
- **API (`modules/cmd/hatchet-api`)**: Entry point for SDKs and CLI management.
- **Engine (`modules/cmd/hatchet-engine`)**: Core orchestration logic, including the Ticker for scheduled/cron jobs.
- **CLI (`modules/cmd/hatchet-cli`)**: Terminal interface for all operational tasks.
- **Contracts (`modules/api-contracts`)**: Protobuf (`.proto`) and OpenAPI (`.yaml`) definitions for all communications.

---

## 3. Workflows

### Setup: Initialize Local Environment
1. Start infrastructure: `task start-db` (Starts Postgres and RabbitMQ via Docker).
2. Run migrations: `task migrate`.
3. Start the API/Engine: `task start-api` and `task start-engine`.
4. Configure CLI: `hatchet profile add --name dev --token <DEV_TOKEN>`.

### Development: Implementing a Task (TypeScript)
1. Initialize client: `const hatchet = Hatchet.init()`.
2. Define Task:
   ```typescript
   export const myTask = hatchet.task({
     name: 'my-task',
     fn: async (input: MyInput) => { ... }
   });
   ```
3. Start Worker:
   ```typescript
   const worker = await hatchet.worker('my-worker');
   worker.register([myTask]);
   await worker.start();
   ```

### Operations: Trigger and Monitor
1. Trigger via CLI: `hatchet run trigger <workflow_name> --input '{"foo":"bar"}'`.
2. List Runs: `hatchet run list --since 1h`.
3. Inspect Logs: `hatchet run logs <run_id>`.
4. Replay Failure: `hatchet run replay <run_id> --step <step_readable_id>`.

---

## 4. If/Then Decision Rules

| Requirement | Process / Selection |
| :--- | :--- |
| **Simple async task** | Use `StandaloneTask` via SDK. |
| **Sequential steps** | Define a Workflow with multiple tasks. |
| **Parallel execution (DAG)** | Specify `parents: ["parent-step-id"]` in task options. |
| **Recurring task** | Use `cron_triggers` in the Workflow definition. |
| **Third-party API limit** | Define `RateLimit` in the task options with a unique key. |
| **High resource task** | Use `worker_labels` (Affinity) to route to specific worker groups. |
| **Fault tolerance** | Configure `Retries` and `BackoffFactor` in task metadata. |

---

## 5. Guardrails and Pitfalls

### Critical Constraints
- **Never** block the worker's main thread/event loop. This causes heartbeat failures and task eviction.
- **Never** pass binary blobs in task inputs. Use a storage service and pass the URI.
- **Avoid** using `v1` and `v2` APIs interchangeably without checking engine compatibility (refer to `GetVersion` RPC).

### Known Failure Modes
- **Dispatcher Eviction**: Occurs when a worker misses heartbeats (default 5s). Ensure workers have sufficient CPU.
- **Database Bloat**: Workflow history is persisted. Regularly run retention cleanup tasks if self-hosting.
- **RabbitMQ Saturation**: High-frequency event ingestion can overwhelm the queue. Monitor `SERVER_MSGQUEUE_RABBITMQ_URL` metrics.

---

## 6. Syntax & Configuration Reference

### Common Expression Language (CEL)
Used in `modules/internal/cel` for:
- **Event Filtering**: `event.data.amount > 100`
- **Rate Limit Keys**: `input.user_id`
- **Concurrency Keys**: `input.tenant_id`

### Key Configuration (Environment Variables)
- `DATABASE_URL`: Required for all components.
- `SERVER_GRPC_BROADCAST_ADDRESS`: Address for workers to connect to (default `:7070`).
- `SERVER_AUTH_COOKIE_DOMAIN`: Required for Web UI authentication.

### Core Protobuf Types (`dispatcher.proto`)
- `AssignedAction`: Contains `action_payload`, `action_type` (START/CANCEL), and `workflow_run_id`.
- `StepActionEvent`: Reported by workers; includes `event_type` (STARTED/COMPLETED/FAILED).
