import type { ISetting } from "../../pages/Settings/settings.types.js";

export interface SettingsListItemProps {
    setting: ISetting;
    onSave: (key: string, value: string) => Promise<void>;
}
