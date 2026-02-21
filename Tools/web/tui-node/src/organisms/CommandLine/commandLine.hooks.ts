import axios from "axios";
import { useCallback, useEffect, useMemo, useState } from "react";
import useBackend from "../../hooks/useBackend.js";
import { initMods } from "../../mods/index.js";
import { modRegistry } from "../../mods/modRegistry.js";
import { ENavigationItems } from "../../molecules/Navigation/navigation.enums.js";
import useSettings from "../../pages/Settings/settings.hooks.js";
import useAIStore from "../../store/useAIStore.js";
import { useStore } from "../../store/useStore.js";
import { API_BASE_URL } from "../../utils/constants/globals.js";

// Initialize Mods once
initMods();

const PAGES = Object.values(ENavigationItems);
const COMMANDS = ["goto", "settings", "mod", "restart-backend", "reload-settings", "quit"];

export const useCommandLine = () => {
    const [input, setInput] = useState("");
    const [info, setInfo] = useState<string[]>(["", "", "", "", ""]);
    const [suggestionIndex, setSuggestionIndex] = useState(-1);
    const [configStructure, setConfigStructure] = useState<Record<string, string[]>>({});

    const { setCurrentPage } = useStore();
    const { handleUpdateSetting, fetchSettings } = useSettings();
    const { addChat } = useAIStore();
    const { restartBackend } = useBackend();

    // Fetch dynamic structure from Backend Class (Pydantic)
    useEffect(() => {
        const loadStructure = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/settings/structure`);
                setConfigStructure(response.data);
            } catch (err) {
                console.error("Failed to load settings structure", err);
            }
        };
        loadStructure();
    }, []);

    const updateInfo = useCallback((lines: string[]) => {
        const newInfo = [...lines];
        while (newInfo.length < 5) newInfo.push("");
        setInfo(newInfo.slice(0, 5));
    }, []);

    const currentSuggestions = useMemo(() => {
        if (!input.startsWith(":")) return [];
        const parts = input.slice(1).split(":");

        if (parts.length === 1) {
            return COMMANDS.filter((c: string) => c.startsWith(parts[0] || ""));
        }

        const cmd = parts[0];
        const sub = parts[1] || "";

        if (cmd === "goto") {
            return PAGES.filter((p: string) => p.startsWith(sub));
        }

        if (cmd === "mod") {
            if (parts.length === 2) {
                return modRegistry.getAllModNames().filter((m: string) => m.startsWith(sub));
            }
            const mod = modRegistry.getMod(parts[1] || "");
            if (mod) return mod.getSuggestions(parts.slice(2));
        }

        if (cmd === "settings") {
            if (parts.length === 2) {
                return Object.keys(configStructure).filter((k: string) => k.startsWith(sub));
            }
            if (parts.length === 3) {
                const group = parts[1];
                if (group && configStructure[group]) {
                    return configStructure[group].filter((s: string) => s.startsWith(sub));
                }
            }
        }

        return [];
    }, [input, configStructure]);

    const handleCycleSuggestion = useCallback(
        (direction: "next" | "prev") => {
            if (currentSuggestions.length === 0) return;
            const nextIndex =
                direction === "next"
                    ? (suggestionIndex + 1) % currentSuggestions.length
                    : (suggestionIndex - 1 + currentSuggestions.length) % currentSuggestions.length;
            setSuggestionIndex(nextIndex);
            const parts = input.split(":");
            parts[parts.length - 1] = currentSuggestions[nextIndex] as string;
            setInput(parts.join(":"));
        },
        [currentSuggestions, suggestionIndex, input],
    );

    const handleAiRequest = useCallback(
        (input: string) => {
            addChat(input);
            setInput("");
            setSuggestionIndex(-1);
        },
        [addChat],
    );

    const handleExecute = useCallback(
        (rawInput: string) => {
            if (!rawInput.startsWith(":")) {
                handleAiRequest(rawInput);
                return;
            }
            const parts = rawInput.slice(1).split(":");
            const command = parts[0];
            const subParts = parts.slice(1);

            switch (command) {
                case "mod": {
                    const modName = subParts[0];
                    if (modName) {
                        const mod = modRegistry.getMod(modName);
                        if (mod) {
                            const result = mod.execute(subParts.slice(1));
                            updateInfo(result);
                        } else {
                            updateInfo([`Mod '${modName}' not found.`]);
                        }
                    }
                    break;
                }
                case "goto": {
                    if (subParts[0]) {
                        setCurrentPage(subParts[0] as ENavigationItems);
                        updateInfo([`Navigated to ${subParts[0]}`]);
                    }
                    break;
                }
                case "settings": {
                    if (subParts.length >= 2) {
                        const value = subParts.pop();
                        const settingPath = subParts.join(".");
                        if (value !== undefined) {
                            handleUpdateSetting(settingPath, value);
                            updateInfo([`Setting ${settingPath} updated to ${value}`]);
                        }
                    }
                    break;
                }
                case "restart-backend":
                    restartBackend();
                    updateInfo(["Restarting Backend Service..."]);
                    break;
                case "reload-settings":
                    fetchSettings();
                    updateInfo(["Settings reloaded from Data/settings.json"]);
                    break;
                case "quit":
                    process.exit(0);
                    break;
                default:
                    updateInfo([`Unknown command: ${command}`]);
            }
            setInput("");
            setSuggestionIndex(-1);
        },
        [
            setCurrentPage,
            handleUpdateSetting,
            restartBackend,
            fetchSettings,
            updateInfo,
            handleAiRequest,
        ],
    );

    useEffect(() => {
        if (input.startsWith(":")) {
            const lines =
                currentSuggestions.length > 0
                    ? ["SUGGESTIONS (Ctrl+Tab):", currentSuggestions.join(", "), "", "", input]
                    : ["COMMAND MODE", "Enter :mod:<name>:<cmd> or :goto:<page>", "", "", input];
            updateInfo(lines);
        } else {
            updateInfo(["Type ':' to start a command", "", "", "", ""]);
        }
    }, [input, currentSuggestions, updateInfo]);

    return { input, setInput, info, handleExecute, handleCycleSuggestion };
};
