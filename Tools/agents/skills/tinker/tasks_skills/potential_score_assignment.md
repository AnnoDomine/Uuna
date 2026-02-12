# Task Skill: Potential Score Assignment

## Objective
To assign a `Max_Potential` integer value to a task, defining the performance ceiling.

## Procedural Steps
1.  **Base Potential**:
    - Tier 1: 50 points.
    - Tier 2: 100 points.
    - Tier 3: 200 points.
2.  **Modifiers**:
    - Add +25 points if **Expedition Group** is required.
    - Add +10 points for every additional build version involved.
3.  **Finalize Baseline**: This number is recorded in the `research.tasks` table and passed to the **Observer**.

## Constraints
- **Immutable**: Once work starts, the potential score cannot be changed.

## Output Requirements
Return a JSON object containing:
- `max_potential`: Integer value.
- `component_breakdown`: Logic for the final number.
