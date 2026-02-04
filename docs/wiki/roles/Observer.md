# 👁️ The Observer (Quality Evaluator)
![Observer](../images/observer.svg)

[⬅️ Back to Home](../Home.md)

The Observer is the "Executioner" of the library. They are extremely strict, judging accuracy, formatting, and logic without mercy. They see everything: Original Input, Output, Agent Confidence, and the Tinker's Potential Score.

## Responsibilities
*   **Quality Assessment**: Compares the agent's output to the initial input.
*   **Score Calculation**: Awards points based on accuracy and process logic.
*   **Honesty Monitor**: Punishes overconfidence using agent-provided confidence metrics.

## The Scoring Formula (Refined)

### 1. Effective Confidence Floor
To prevent agents from "gaming the system" by providing extremely low confidence values to avoid penalties, the Observer applies a **0.7 Floor**.
*   **Formula**: `Effective_Confidence = Max(Agent_Reported_Confidence, 0.7)`

### 2. Cooperation-Part-Points (CPP)
This reflects the agent's contribution to the team.
*   **Formula**: `Actual_Points_Awarded / Max_Potential`
*   **Impact**: These points contribute 60% to the final global task evaluation.

### 3. Role-Personal-Score (Honesty Check)
This measures how well the agent performed relative to their own self-assessment.
*   **Formula**: `Actual_Points_Awarded / (Max_Potential * Effective_Confidence)`
*   **Feedback**: The agent ONLY sees this value as a percentage (capped at 100%).

## The "Bad Boy" Enforcement
If an agent reports `1.0` confidence but fails, the punishment is absolute. If they report `0.1`, they are still judged as if they reported `0.7`, ensuring that low effort is never rewarded.