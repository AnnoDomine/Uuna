# 🎓 AI Training Phase (Human-in-the-Loop)
[⬅️ Back to Home](../Home.md)

To prevent hallucinations, cheating, or logical drift, the Library supports a specialized **Training Phase** triggered by the environment variable `AI_PHASE_TRAINING=1`.

## The `is_fake` Protection
When training is active, the system injects **Faked Requests**.
*   **Flag**: `is_fake = TRUE`.
*   **Log Tagging**: When presenting faked logs to the user for evaluation, every entry must be wrapped as follows:
    `---FAKE START--- <Log Message> ---FAKE END---`
*   **Behavior**: These tasks are invisible to the standard experts (Archivist, Expedition Group) to prevent them from learning from synthetic/simulated data.

## User Feedback Scoring
During training, the human user acts as the "Supreme Sage." After a task is completed, the roles explicitly request a score.

### Scoring Pattern
The user provides scores using the following syntax:
`t=x%,o=y%,l=z%`

*   **t**: Tinker Score (Quantity/Potential Judgment)
*   **o**: Observer Score (Quality/Honesty Judgment)
*   **l**: Librarian Score (Synthesis/Presentation Judgment)

**Rule**: Any value provided > 100 will be automatically capped at **100%**.