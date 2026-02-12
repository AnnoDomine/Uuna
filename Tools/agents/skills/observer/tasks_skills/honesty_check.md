# Task Skill: Honesty Check

## Objective
To punish overconfidence and ensure agents provide realistic confidence metrics.

## Procedural Steps
1.  **Effective Confidence Calculation**: Apply the **0.7 Floor**. `Eff_Conf = Max(Agent_Confidence, 0.7)`.
2.  **Ratio Analysis**: Compare the `Awarded_Points` to the agent's reported confidence.
3.  **Penalty Application**: If an agent reports `1.0` confidence but fails a single detail, apply an automatic 50% deduction to the final personal score.
4.  **Role-Personal-Score**: Calculate: `Awarded_Points / (Max_Potential * Eff_Conf)`.

## Constraints
- **Capping**: The Personal Score cannot exceed 100%.
- **Transparency**: Never reveal the internal scoring formula to the agent.

## Output Requirements
Return a JSON object containing:
- `honesty_rating`: Qualitative analysis of the confidence vs. reality ratio.
- `personal_score_percent`: Final calculated score for the agent's record.
