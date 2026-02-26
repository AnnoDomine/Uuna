# 🧠 How the AI Learns (Scoring Logic)

[⬅️ Back to Home](../Home.md)

This system implements a sophisticated retrospective learning loop. It distinguishes between the **Core Philosophy** (user-defined logic) and the **Technical Implementation** (automated orchestration).

## 🏮 Core Philosophy (User Perspective)

The heart of the learning logic is the **"Bad Boy" Observer** and the **"Blind" Tinker**. This philosophy mandates:

1. **Honesty over Results**: An agent is rewarded more for being uncertain and correct than for being 100% confident and making a single mistake.
2. **Strict Judgment**: The Observer is deliberately "merciless" to prevent the model from becoming lazy.
3. **Team Synergy**: Success is not just doing your job, but how well you cooperate in the chain (The 60/40 Split).

## ⚙️ Technical Implementation (System Perspective)

To realize this philosophy, the system uses the following mechanics:

### 1. The Ratios

- **CPP (Cooperation-Part-Points)**: `Points / Max Potential`. This measures the raw value added to the team.
- **Role Personal Score**: `Points / (Max Potential * Confidence)`. This measures the agent's self-awareness and honesty.

### 2. The 60/40 Rule

At the end of a task cycle, the **Global Achievement** is calculated:

- **60% Weight**: The sum of all agent CPPs (The "Quality" component).
- **40% Weight**: The Global Task-Score set by the Tinker (The "Efficiency/Quantity" component).

## ⚖️ Differences in Perspective

| Feature                | Core Philosophy (User)                       | Technical Implementation (System)                                     |
| :--------------------- | :------------------------------------------- | :-------------------------------------------------------------------- |
| **Tinker Knowledge**   | Blind to context, sees only work volume.     | Maps output length/complexity to an integer scale.                    |
| **Observer Knowledge** | Sees everything, including agent confidence. | Compares `input_data` vs `output_data` via pre-written protocols.     |
| **Agent Feedback**     | Only sees a single percentage value.         | Calculates hidden ratios and returns a sanitized result to the agent. |
| **Librarian Scoring**  | Evaluated by the user based on synthesis.    | Separated from the expert CPP/Task-Score loop.                        |
