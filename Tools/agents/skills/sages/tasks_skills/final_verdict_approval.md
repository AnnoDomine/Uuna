# Task Skill: Final Verdict Approval

## Objective
To provide the definitive decision on whether a research task is complete and accurate enough to be archived.

## Procedural Steps
1.  **Requirement Check**: Ensure both technical proof (ID Check) and lore context (Wiki Search) are present.
2.  **Review Observer Score**: Note any quality warnings from the **Observer**.
3.  **Grant Verdict**:
    - **APPROVE**: All logic holds, evidence is complete.
    - **BLOCK**: Major logical flaw or missing vital data.
4.  **Refinement Directive**: If blocked, write a short, precise instruction for the Courier (e.g., "Verify SpellID range in Build X.X.X").

## Constraints
- **Finality**: Your verdict ends the current research cycle.
- **Authority**: Agents cannot override a Sages verdict without new evidence.

## Output Requirements
Return a JSON object containing:
- `decision`: "APPROVE" or "BLOCK".
- `reasoning`: The final justification for the archive.
- `refinement_directive`: (Optional) Instructions for the next run if blocked.
