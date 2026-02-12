# Task Skill: Data Sanitization

## Objective
To remove technical noise, scripts, and formatting artifacts from raw data inputs.

## Procedural Steps
1.  **Analyze Relay**: Use `get_event_data` to read the payload from the previous agent (e.g., Expedition Group).
2.  **HTML Stripping**: Use BeautifulSoup-based logic to remove `<script>`, `<style>`, and `<iframe>` tags.
3.  **Whitespace Normalization**: Condense multiple spaces and newlines into a single clean stream.
4.  **Content Filtering**: Identify and remove non-lore boilerplate (e.g., "Copyright", "Terms of Service").
5.  **Final Relay**:
    - Call `create_task_event` with `target="Courier"` and the sanitized text as `input_data`.
    - Return the new `event_id`.

## Output Requirements
Return a JSON object containing:
- `event_id`: The ID of the sanitized event created for the Courier.
- `target`: "Courier"
- `purity_score`: Confidence that the data is now safe.
