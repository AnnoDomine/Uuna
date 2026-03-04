export const SETTINGS_STORE_SETTTINGSFALLBACK = {
    ai: {
        num_thread: 10,
        num_ctx: 4096,
        num_gpu: 99,
        acceleration_mode: "gpu",
        memory_limit: 3,
    },
    ingestion: {
        workers: 8,
        threads: 4,
        limit_per_build: 1000,
        sync_builds_on_startup: true,
    },
    analysis: {
        use_global_mapping: false,
        auto_skip_unidentifiable: false,
    },
    system: {
        debug: true,
        localisation: "german",
        ui_theme: "dark",
        cooldown: 4.0,
    },
};
