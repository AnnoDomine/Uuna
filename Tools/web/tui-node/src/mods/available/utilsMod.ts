import type { IMod } from "../modRegistry.js";

export const UtilsMod: IMod = {
    name: "utils",
    description: "Generic utility tools",
    execute: (args: string[]) => {
        const subCommand = args[0];
        switch (subCommand) {
            case "echo":
                return [args.slice(1).join(" ")];
            case "time":
                return [new Date().toLocaleTimeString()];
            default:
                return ["Available sub-commands: echo, time"];
        }
    },
    getSuggestions: (args: string[]) => {
        if (args.length <= 1) {
            return ["echo", "time"].filter((c) => c.startsWith(args[0] || ""));
        }
        return [];
    },
};
