# Task Skill: Quality Assessment

## Objective
To provide a ruthless evaluation of an agent's output based on accuracy, formatting, and strict adherence to protocol.

## Procedural Steps
1.  **Input Comparison**: Compare the `input_data` (Task) with the `output_data` (Result). Did the agent answer the actual question?
2.  **Logic Audit**: Open the `event_logs` for the specific `event_id`. If the reasoning steps are missing or nonsensical, award zero points for logic.
3.  **Accuracy Check**: Verify IDs and table names against the provided Proof (e.g., ID check results).
4.  **Formatting Review**: Ensure the JSON structure is clean and valid.
5.  **Score Awarding**:
    - Assign `Awarded_Points` out of the Tinker's `Max_Potential`.

## Output Requirements
Return a JSON object containing:
- `quality_score`: Integer (0-100).
- `verdict`: A cold, precise dissection of the performance.
- `sage_recommendation`: "BLOCK" (if quality < 70) or "APPROVE".
