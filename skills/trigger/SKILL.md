---
name: trigger
description: Operational guidance for AI agents to build, configure, and manage background tasks and AI workflows using Trigger.dev (v4).
---
# Trigger.dev Operational Skill

This skill provides operational guidance for AI agents to build, configure, and manage background tasks and AI workflows using Trigger.dev (v4).

## 1. Define Clear Boundaries

### Scope
- **Framework**: Trigger.dev v4 (using `@trigger.dev/sdk`).
- **Capabilities**: Background tasks, scheduled jobs, AI agent orchestration, real-time status/streaming, human-in-the-loop.
- **Environment**: Node.js 18+, TypeScript, `pnpm` (preferred).
- **Permissions**: Requires `TRIGGER_SECRET_KEY` for API access and deployment.

### When to Use
- Implementing long-running processes (exceeding serverless timeouts).
- Building complex AI workflows (parallelizing LLM calls, chaining with gates).
- Scheduling recurring tasks (crons).
- Requiring reliable retries and observability for critical operations.
- Implementing "human-in-the-loop" approval gates.

---

## 2. Structural Overview

### Mental Map
Trigger.dev operates on a **decoupled execution model**. You define tasks in your codebase, and the Trigger.dev platform manages the queueing, execution, and persistence (checkpointing).

- **`trigger.config.ts`**: The entry point for project-level settings (project ID, task directories, build extensions).
- **`trigger/`**: The conventional directory where tasks are defined and exported.
- **`task()` / `schemaTask()`**: The primary primitives for defining unit-of-work.
- **Trigger Server**: The orchestrator that receives triggers and assigns them to workers.
- **`npx trigger`**: The CLI for development (`dev`) and deployment (`deploy`).

### Key Components
- **SDK**: `@trigger.dev/sdk` for task definition and triggering.
- **CLI**: `trigger` (npm package `trigger.dev`) for managing the lifecycle.
- **Realtime**: `@trigger.dev/react-hooks` for frontend synchronization.

---

## 3. Documented Workflows

### Workflow: Project Initialization
1. **Install SDK**: `pnpm add @trigger.dev/sdk`
2. **Initialize**: `npx trigger init` (creates `trigger.config.ts` and `trigger/` dir).
3. **Configure**: Set `project` ID in `trigger.config.ts` and `TRIGGER_SECRET_KEY` in `.env`.

### Workflow: Creating a Basic Task
1. Create a file in `trigger/` (e.g., `trigger/my-task.ts`).
2. Define the task using `task()`:
   ```typescript
   import { task } from "@trigger.dev/sdk";

   export const myTask = task({
     id: "my-task",
     run: async (payload: { message: string }) => {
       console.log(payload.message);
       return { success: true };
     },
   });
   ```
3. **Export** the task from the file.

### Workflow: Triggering Tasks
- **From Backend**:
  ```typescript
  import { tasks } from "@trigger.dev/sdk";
  import type { myTask } from "./trigger/myTask";

  await tasks.trigger<typeof myTask>("my-task", { message: "Hello" });
  ```
- **From Inside another Task (Sequential)**:
  ```typescript
  const result = await myTask.triggerAndWait({ message: "Hello" });
  if (result.ok) { /* handle result.output */ }
  ```

### Workflow: Deployment
1. Ensure `trigger.config.ts` is correctly configured.
2. Run `npx trigger deploy`.
3. Verify the deployment in the Trigger.dev dashboard.

---

## 4. "If/Then" Decision Rules

| If the task requires... | Then use... |
| :--- | :--- |
| Runtime payload validation | `schemaTask({ schema: z.object(...), ... })` |
| To run multiple *different* tasks in parallel | `batch.triggerByTaskAndWait([...])` |
| To run multiple *instances* of the same task | `myTask.batchTriggerAndWait([...])` |
| Human approval or external callback | `wait.forToken({ token: "..." })` |
| To pause for a specific duration | `wait.for({ minutes: 5 })` |
| To pause until a specific time | `wait.until({ date: new Date(...) })` |
| To stream LLM responses to a frontend | `streams.define(...)` + `stream.pipe(completion)` |
| To install system packages (FFmpeg, etc.) | `build.extensions` in `trigger.config.ts` |
| To process one user at a time | `queue({ name: "user-queue", concurrencyLimit: 1 })` |

---

## 5. Guardrails and Common Pitfalls

### Critical Constraints
- **NO `Promise.all`**: Never wrap `wait.*`, `triggerAndWait()`, or `batchTriggerAndWait()` in `Promise.all` or `Promise.allSettled`. These MUST be awaited individually or via `batch` methods.
- **V2 DEPRECATION**: Never use `client.defineJob`. It will break the application.
- **Idempotency**: Use `idempotencyKey` for critical operations like payments.
- **Result vs Output**: `triggerAndWait` returns a `Result` object. Access output via `result.output` only if `result.ok` is true, or use `.unwrap()`.

### Limits
- **Batch Size**: Max 1,000 items per batch.
- **Payload Size**: Max 3MB per item. Payloads > 512KB are offloaded but count towards limits.
- **Tags**: Max 10 tags per run. Tag length 1-64 chars.
- **Wait Duration**: No hard limit, but tasks are checkpointed for waits > 5s.

---

## 6. Syntax & Configuration References

### `trigger.config.ts` Reference
```typescript
import { defineConfig } from "@trigger.dev/sdk";

export default defineConfig({
  project: "proj_xxxxxx",
  dirs: ["./trigger"],
  runtime: "node", // "node" or "bun"
  build: {
    extensions: [], // e.g., prismaExtension(), playwright()
    external: [],   // list of native modules
  },
  retries: {
    default: {
      maxAttempts: 3,
      minTimeoutInMs: 1000,
    },
  },
});
```

### CLI Command Reference
| Command | Description |
| :--- | :--- |
| `npx trigger init` | Initialize project configuration |
| `npx trigger dev` | Start local development server |
| `npx trigger deploy` | Deploy tasks to Trigger.dev cloud |
| `npx trigger login` | Authenticate CLI with your account |

### Task Definition Options
- `retry`: Configuration for automatic retries.
- `queue`: Concurrency and rate limiting settings.
- `machine`: vCPU and RAM requirements (`micro` to `large-2x`).
- `maxDuration`: Maximum execution time in seconds.
