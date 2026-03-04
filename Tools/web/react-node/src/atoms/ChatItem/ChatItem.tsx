import { styled } from "@mui/joy";
import clsx from "clsx";
import type { AIChatItem } from "../../redux/types/ai.types";

type Props = AIChatItem;

const ChatItemContainer = styled("div")(() => ({
    display: "flex",
    flexDirection: "column",
    padding: "0px 2px",
    maxWidth: "100%",
    fontFamily: "Fira Code",
    justifyContent: "flex-start",
    alignItems: "flex-start",
    "&.use": {
        color: "var(--color-user)",
    },
    "&.lib": {
        color: "var(--color-librarian)",
    },
    "&.sys": {
        color: "var(--color-system)",
    },
    "&.cou": {
        color: "var(--color-courier)",
    },
    "&.arc": {
        color: "var(--color-archivist)",
    },
    "&.car": {
        color: "var(--color-cartographer)",
    },
    "&.exp": {
        color: "var(--color-expedition-group)",
    },
    "&.obs": {
        color: "var(--color-observer)",
    },
    "&.sag": {
        color: "var(--color-sages)",
    },
    "&.sen": {
        color: "var(--color-sentinel)",
    },
    "&.tin": {
        color: "var(--color-tinker)",
    },
    "&:not(:last-child)": {
        borderBottom: "1px solid white",
    },
    "&.error": {
        border: "3.5px solid #FF1616",
    },
}));

const ChatItemSender = styled("div")(() => ({
    display: "flex",
    flexDirection: "row",
    gap: "16px",
}));

const ChatItemMessage = styled("div")(() => ({
    display: "flex",
    flexDirection: "row",
    gap: "16px",
    textAlign: "left",
    textWrap: "pretty",
}));

const ChatItem = ({ timestamp, agent, message, type }: Props) => {
    const parsedAgent = agent ? agent[0].toUpperCase() + agent.slice(1) : "Unknown";
    return (
        <ChatItemContainer
            className={clsx(agent.slice(0, 3).toLowerCase(), { error: type === "error" })}
        >
            <ChatItemSender>
                <div>[{new Date(timestamp).toLocaleString()}]</div>
                <div>{parsedAgent}:</div>
            </ChatItemSender>
            <ChatItemMessage>{message}</ChatItemMessage>
        </ChatItemContainer>
    );
};

export default ChatItem;
