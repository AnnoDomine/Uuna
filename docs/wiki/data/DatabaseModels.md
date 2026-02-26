# 💾 Database Models

[⬅️ Back to Home](../Home.md)

Tracking and quality metrics are handled in the `research` schema of `WoW_Research_Knowledge.db`. All tables follow a standard with `created_at` and `updated_at`.

## Standard Columns (Internal Tables)

| Column       | Type      | Description                   |
| :----------- | :-------- | :---------------------------- |
| `created_at` | TIMESTAMP | Auto-set on creation.         |
| `updated_at` | TIMESTAMP | Auto-updated on every change. |

## `research.tasks` (The Dossier)

Tracks the global state and history of a research request.

| Column             | Type    | Description                                                     |
| :----------------- | :------ | :-------------------------------------------------------------- |
| `task_id`          | UUID    | Primary Key.                                                    |
| `query`            | TEXT    | Original user input.                                            |
| `output`           | TEXT    | Final synthesized answer.                                       |
| `status`           | VARCHAR | `running`, `completed`, `blocked`, `awaiting_review`.           |
| `current_location` | VARCHAR | Agent name (e.g., 'Courier').                                   |
| `assigned_builds`  | JSON    | List of WoW versions (e.g., `["7.3.5.25600", "10.0.2.45779"]`). |

## `research.task_events` (The Action Layer)

Specific agent missions triggered by the Courier.

| Column             | Type    | Description                          |
| :----------------- | :------ | :----------------------------------- |
| `event_id`         | UUID    | Primary Key.                         |
| `task_id`          | UUID    | Foreign Key to tasks.                |
| `initiator_role`   | VARCHAR | Role that requested the action.      |
| `target_role`      | VARCHAR | Agent expected to perform the work.  |
| `input_data`       | JSON    | Parameters for the mission.          |
| `output_data`      | JSON    | Result data from the agent.          |
| `agent_confidence` | DOUBLE  | Self-reported certainty (0.0 - 1.0). |

## `research.event_logs` (The Agent's Diary)

Granular step-by-step logs from an agent during a mission.

| Column      | Type    | Description                   |
| :---------- | :------ | :---------------------------- |
| `log_id`    | INTEGER | Primary Key (Auto).           |
| `event_id`  | UUID    | Foreign Key to task_events.   |
| `task_id`   | UUID    | Foreign Key to tasks.         |
| `role`      | VARCHAR | Agent writing the log.        |
| `log_entry` | TEXT    | Detaillierter Arbeitsschritt. |

## `research.score_board` (The Final Judgment)

The results of the retrospective evaluation.

| Column          | Type    | Description                                                    |
| :-------------- | :------ | :------------------------------------------------------------- |
| `score_id`      | INTEGER | Primary Key (Auto).                                            |
| `task_id`       | UUID    | Foreign Key to tasks.                                          |
| `event_id`      | UUID    | Optional: Ref to specific event (NULL for collective scoring). |
| `final_percent` | DOUBLE  | The only feedback visible to the AI (0 - 100).                 |
