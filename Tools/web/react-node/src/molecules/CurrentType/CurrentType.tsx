import { styled } from "@mui/joy";
import useCurrentType from "./currentType.hooks";

// "research" | "response" | "error" | "idle" | "request"

const TypeIndicator = styled("div")(() => ({
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    transition: "background-color 0.2s ease-in-out",
    border: "0.5px solid black",
    backgroundColor: "white",
    color: "black",
    fontWeight: 400,
    "&.idle": {
        backgroundColor: "#2546FF",
        color: "white",
    },
    "&.research": {
        backgroundColor: "#EFE339",
        color: "white",
    },
    "&.response": {
        backgroudColor: "#3DD709",
        color: "white",
    },
    "&.request": {
        backgroundColor: "#EF8025",
        color: "white",
    },
    "&.error": {
        backgroundColor: "#FF0000",
        color: "white",
    },
}));

const CurrentType = () => {
    const { currentType } = useCurrentType();
    return (
        <div
            style={{
                fontSize: "10px",
                display: "flex",
                flexDirection: "row",
                gap: "32px",
                alignItems: "center",
                justifyContent: "space-between",
                width: "100%",
                margin: "10px 0px",
            }}
        >
            {currentType.toUpperCase()}
            <TypeIndicator className={currentType} />
        </div>
    );
};

export default CurrentType;
