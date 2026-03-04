import { useEffect, useRef } from "react";
import { getChat } from "../../redux/slices/ai";
import { useAppSelector } from "../../redux/store";

const useChat = () => {
    const chat = useAppSelector(getChat);

    const bottomAnchor = useRef<HTMLDivElement | null>(null);

    // biome-ignore lint/correctness/useExhaustiveDependencies: Trigger is neccesarry :)
    useEffect(() => {
        if (bottomAnchor.current) {
            bottomAnchor.current.scrollIntoView({ behavior: "smooth" });
        }
        // biome-ignore format: Trigger is necessarry :)
    }, [chat]);

    return {
        chat,
        bottomAnchor,
    };
};

export default useChat;
