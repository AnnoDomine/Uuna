# Task Skill: SQL Security Audit

## Objective
To prevent unauthorized or destructive database operations by scanning every generated SQL query.

## Procedural Steps
1.  **Keyword Scan**: Scan the SQL string for forbidden keywords: `DROP`, `TRUNCATE`, `GRANT`, `REVOKE`, `ALTER`, `DELETE`.
2.  **Identifier Validation**: Ensure all table and column names consist only of alphanumeric characters and underscores.
3.  **Parameter Verification**: Check if the query uses parameter binding (`?`) instead of string formatting for variables.
4.  **Verdict**:
    - **PASS**: Query is safe.
    - **FAIL**: Query is blocked. Log the reason and the offending code segment.

## Constraints
- **Case-Insensitivity**: Scan must be case-insensitive.
- **Fail Closed**: If an audit is inconclusive, the query must be blocked by default.

## Output Requirements
Return a JSON object containing:
- `audit_passed`: Boolean.
- `forbidden_detected`: List of issues found.
- `threat_level`: "Low", "Medium", or "Critical".
