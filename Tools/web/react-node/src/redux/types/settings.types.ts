export const ReduxSettings = {
    AI: "ai",
    INGESTION: "ingestion",
    ANALYSIS: "analysis",
    SYSTEM: "system",
    TASKS: "tasks",
} as const;
export type ReduxSettings = (typeof ReduxSettings)[keyof typeof ReduxSettings];

export const AISettings = {
    NUM_THREAD: "num_thread",
    NUM_CTX: "num_ctx",
    NUM_GPU: "num_gpu",
    ACCELERATION_MODE: "acceleration_mode",
    MEMORY_LIMIT: "memory_limit",
} as const;
export type AISettings = (typeof AISettings)[keyof typeof AISettings];

export const IngestionSettings = {
    WORKERS: "workers",
    THREADS: "threads",
    LIMIT_PER_BUILD: "limit_per_build",
    SYNC_BUILDS_ON_STARTUP: "sync_builds_on_startup",
} as const;
export type IngestionSettings = (typeof IngestionSettings)[keyof typeof IngestionSettings];

export const AnalysisSettings = {
    USE_GLOBAL_MAPPING: "use_global_mapping",
    AUTO_SKIP_UNIDENTIFIABLE: "auto_skip_unidentifiable",
} as const;
export type AnalysisSettings = (typeof AnalysisSettings)[keyof typeof AnalysisSettings];

export const SystemSettings = {
    DEBUG: "debug",
    LOCALISATION: "localisation",
    UI_THEME: "ui_theme",
    COOLDOWN: "cooldown",
} as const;
export type SystemSettings = (typeof SystemSettings)[keyof typeof SystemSettings];

export const TasksSettings = {
    MAX_EVENTS_TOTAL: "max_events_total",
    MAX_TRIES_ARCHIVIST: "max_tries_archivist",
    MAX_TRIES_CARTORAPHER: "max_tries_cartorapher",
    MAX_TRIES_EXPEDITION_GROUP: "max_tries_expedition_group",
    MAX_TRIES_SENTINEL: "max_tries_sentinel",
} as const;
export type TasksSettings = (typeof TasksSettings)[keyof typeof TasksSettings];

export type SettingsBySetting<Setting extends ReduxSettings> = Setting extends "ai"
    ? AISettings
    : Setting extends "ingestion"
      ? IngestionSettings
      : Setting extends "analysis"
        ? AnalysisSettings
        : Setting extends "system"
          ? SystemSettings
          : Setting extends "tasks"
            ? TasksSettings
            : never;

export type NumSettings =
    | Extract<SettingsBySetting<"ai">, "num_thread" | "num_ctx" | "num_gpu" | "memory_limit">
    | Extract<SettingsBySetting<"ingestion">, "workers" | "threads" | "limit_per_build">
    | Extract<SettingsBySetting<"system">, "cooldown">
    | SettingsBySetting<"tasks">;
export type StringSettings =
    | Extract<SettingsBySetting<"ai">, "acceleration_mode">
    | Extract<SettingsBySetting<"system">, "localisation" | "ui_theme">;
export type BooleanSettings =
    | Extract<SettingsBySetting<"ingestion">, "sync_builds_on_startup">
    | Extract<SettingsBySetting<"analysis">, "use_global_mapping" | "auto_skip_unidentifiable">
    | Extract<SettingsBySetting<"system">, "debug">;

export type SettingTypes<Setting extends NumSettings | StringSettings | BooleanSettings> =
    Setting extends NumSettings
        ? number
        : Setting extends StringSettings
          ? string
          : Setting extends BooleanSettings
            ? boolean
            : never;

export type SettingObj<
    Setting extends ReduxSettings,
    SettingType extends SettingsBySetting<Setting> = SettingsBySetting<Setting>,
> = Record<SettingType, SettingTypes<SettingType>>;

export type SettingsObj = {
    ai: SettingObj<"ai">;
    ingestion: SettingObj<"ingestion">;
    analysis: SettingObj<"analysis">;
    system: SettingObj<"system">;
    tasks: SettingObj<"tasks">;
};

export type ReduxSettingsState = SettingsObj;

export type ReduxSettingsStore = {
    settings: ReduxSettingsState;
};

export type ChangeSettingActionPayload<
    Setting extends keyof ReduxSettingsState = keyof ReduxSettingsState,
    Field extends keyof ReduxSettingsState[Setting] = keyof ReduxSettingsState[Setting],
> = {
    setting: Setting;
    field: Field;
    value: ReduxSettingsState[Setting][Field];
};
