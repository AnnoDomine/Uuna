export const SETTING_LABELS = {
    ai: "AI",
    ingestion: "Ingestion",
    analysis: "Analysis",
    system: "System",
    tasks: "Tasks",
};

export const AI_SETTINGS = {
    num_thread: "Number of threads",
    num_ctx: "Number of context",
    num_gpu: "Number of GPUs",
    acceleration_mode: "Acceleration mode",
    memory_limit: "Memory limit",
};

export const INGESTION_SETTINGS = {
    workers: "Workers",
    threads: "Threads",
    limit_per_build: "Limit per build",
    sync_builds_on_startup: "Sync builds on startup",
};

export const ANALYSIS_SETTINGS = {
    use_global_mapping: "Use global mapping",
    auto_skip_unidentifiable: "Auto skip unidentifiable",
};

export const SYSTEM_SETTINGS = {
    debug: "Debug",
    localisation: "Localisation",
    ui_theme: "UI theme",
    cooldown: "Cooldown",
};

export const TASKS_SETTINGS = {
    max_events_total: "Max events total",
    max_tries_archivist: "Max tries archivist",
    max_tries_cartorapher: "Max tries cartorapher",
    max_tries_expedition_group: "Max tries expedition group",
    max_tries_sentinel: "Max tries sentinel",
};

export const ALL_SETTING_LABELS = {
    ...AI_SETTINGS,
    ...INGESTION_SETTINGS,
    ...ANALYSIS_SETTINGS,
    ...SYSTEM_SETTINGS,
    ...TASKS_SETTINGS,
};

export const SETTING_TITLES: Record<keyof typeof ALL_SETTING_LABELS, string> = {
    num_thread: "Number of threads to use for inference",
    num_ctx: "Number of context tokens to use for inference",
    num_gpu: "Number of GPUs to use for inference",
    acceleration_mode: "Acceleration mode to use for inference",
    memory_limit: "Memory limit to use for inference",
    workers: "Number of workers to use for ingestion",
    threads: "Number of threads to use for ingestion",
    limit_per_build: "Limit per build to use for ingestion",
    sync_builds_on_startup: "Sync builds on startup to use for ingestion",
    use_global_mapping: "Use global mapping to use for analysis",
    auto_skip_unidentifiable: "Auto skip unidentifiable to use for analysis",
    debug: "Enable/Disable debug mode for system",
    localisation: "Localisation to use for system",
    ui_theme: "UI theme to use for system",
    cooldown: "Cooldown to use for system",
    max_events_total: "Max events total to use for tasks",
    max_tries_archivist: "Max tries archivist to use for tasks",
    max_tries_cartorapher: "Max tries cartorapher to use for tasks",
    max_tries_expedition_group: "Max tries expedition group to use for tasks",
    max_tries_sentinel: "Max tries sentinel to use for tasks",
};
