# Task Skill: Data Sanitization

## Objective
To remove technical noise, scripts, and formatting artifacts from raw data inputs.

## Procedural Steps
1.  **HTML Stripping**: Use BeautifulSoup-based logic to remove `<script>`, `<style>`, and `<iframe>` tags.
2.  **Whitespace Normalization**: Condense multiple spaces and newlines into a single clean stream.
3.  **Special Character Handling**: Escape or remove characters that could break JSON parsing or shell commands.
4.  **Content Filtering**: Identify and remove non-lore boilerplate (e.g., "Copyright", "Terms of Service", "Navigation").

## Output Requirements
Return a JSON object containing:
- `sanitized_content`: The cleaned text or data structure.
- `removed_elements_count`: Integer count of stripped items.
- `purity_score`: Confidence that the data is now safe.
