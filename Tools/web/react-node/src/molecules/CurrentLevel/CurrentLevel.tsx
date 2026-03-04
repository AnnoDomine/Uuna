import useCurrentLevel from "./currentLevel.hooks";

const CurrentLevel = () => {
    const { currentLevel } = useCurrentLevel();
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
            <div>Level:</div>
            {(currentLevel || "NONE").toUpperCase()}
        </div>
    );
};

export default CurrentLevel;
