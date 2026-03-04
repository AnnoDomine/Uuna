import ChatItem from "../../atoms/ChatItem/ChatItem";
import useChat from "./chat.hooks";

const Chat = () => {
    const { chat, bottomAnchor } = useChat();
    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                width: "100%",
                height: "100%",
                maxHeight: "60vh",
                border: "1px solid white",
                backgroundColor: "lightgrey",
                color: "white",
                overflow: "auto",
                lineBreak: "anywhere",
                borderRadius: "6px",
            }}
        >
            {(chat || []).map((c) => (
                <ChatItem key={c.timestamp} {...c} />
            ))}
            <div ref={bottomAnchor} style={{ height: "0px", width: "0px" }} />
        </div>
    );
};

export default Chat;
