import { createContext, useContext } from "react";

export const SettingsContext = createContext<undefined>(undefined);

export const useSettings = () => {
    const settings = useContext(SettingsContext);
    if (settings === undefined) {
        throw new Error("useSettings must be used within a SettingsProvider");
    }
    return settings;
};
