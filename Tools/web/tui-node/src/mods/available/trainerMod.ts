import axios from "axios";
import { API_BASE_URL } from "../../utils/constants/globals.js";
import type { IMod } from "../modRegistry.js";

export const TrainerMod: IMod = {
    name: "trainer",
    description: "Runs pattern compliance training for agents",
    execute: (args: string[]) => {
        const role = args[0];
        if (!role)
            return [
                "Usage: :mod:trainer:<role>",
                "Roles: archivist, librarian, courier, sages, observer, tinker",
            ];

        // We trigger the training via a new API endpoint we'll create
        axios
            .post(`${API_BASE_URL}/ai/train`, { role })
            .then((res) => {
                console.log("Training started", res.data);
            })
            .catch((err) => {
                console.error("Training failed", err);
            });

        return [
            `Started pattern training for ${role}...`,
            "Check terminal/logs for progress.",
            "KI will complete 5 rounds.",
        ];
    },
    getSuggestions: (args: string[]) => {
        if (args.length <= 1) {
            const roles = [
                "archivist",
                "librarian",
                "courier",
                "sages",
                "observer",
                "tinker",
                "expedition_group",
                "sentinel",
            ];
            return roles.filter((r) => r.startsWith(args[0] || ""));
        }
        return [];
    },
};
