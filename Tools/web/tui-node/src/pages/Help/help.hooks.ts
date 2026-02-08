import { useCallback, useState } from "react";
import { EHelpTopic } from "./help.types.js";

const useHelp = () => {
    const [activeTopic, setActiveTopic] = useState<EHelpTopic>(EHelpTopic.KEYBINDINGS);

    const handleSelectTopic = useCallback((topicId: string) => {
        setActiveTopic(topicId as EHelpTopic);
    }, []);

    const topics = [
        {
            label: "⌨️ Keybindings",
            value: EHelpTopic.KEYBINDINGS,
            id: EHelpTopic.KEYBINDINGS,
            meta: {},
        },
        {
            label: "👥 Agent Roles",
            value: EHelpTopic.AGENT_ROLES,
            id: EHelpTopic.AGENT_ROLES,
            meta: {},
        },
        {
            label: "🏗️ Architecture",
            value: EHelpTopic.ARCHITECTURE,
            id: EHelpTopic.ARCHITECTURE,
            meta: {},
        },
    ];

    return {
        activeTopic,
        topics,
        handleSelectTopic,
    };
};

export default useHelp;
