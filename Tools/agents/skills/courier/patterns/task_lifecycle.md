# Pattern: Task Lifecycle

## Lifecycle States
- **`spawned`**: Task created by Librarian, no work done yet.
- **`active`**: Currently being processed by an agent.
- **`pending_verification`**: Data gathered, waiting for the Sages.
- **`stalled`**: Missing dependencies (e.g., build not indexed).
- **`rejected`**: Logic failed validation by Sages or Observer.
- **`finalized`**: Knowledge committed to Vector Memory and Global Truths.

## The Torch (Event ID) Flow
The Courier holds the `task_id` and generates a new `event_id` for every hand-off.
1.  **Courier** receives `Event_A` (Result).
2.  **Courier** analyzes result and decides on **Agent_B**.
3.  **Courier** creates `Event_B`, attaching the output of `Event_A` as input for `Agent_B`.
4.  This creates a chain: `Event_A` -> `Event_B` -> `Event_C`...

## Convergence
A task only converges when the **Sages** provide an `APPROVE` verdict and the **Observer** grants a quality score > 80%.
