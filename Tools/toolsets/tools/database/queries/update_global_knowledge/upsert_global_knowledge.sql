INSERT INTO research.global_knowledge (column_pattern, source_table, target_table, confidence, ai_notes, last_verified_build, confirmations)
VALUES (?, ?, ?, ?, ?, ?, 1)
ON CONFLICT(column_pattern, source_table, target_table) DO UPDATE SET
    confirmations = confirmations + 1,
    last_verified_build = excluded.last_verified_build,
    ai_notes = COALESCE(excluded.ai_notes, ai_notes),
    confidence = (confidence + excluded.confidence) / 2
