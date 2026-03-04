import { Input, styled, Typography } from "@mui/joy";
import clsx from "clsx";
import useTerminal from "./terminal.hooks";

const TerminalInput = styled(Input)(() => ({
    outlineColor: "transparent !important",
    "--Input-focusedThickness": "0rem",
    color: "black",
    caretColor: "black",
    backgroundColor: "lightgray",
    fontFamily: "Fira Code",
    caretShape: "underscore",
    borderWidth: "3px",
    "&.loading": {
        // Show a fancy effect as the background color.
        animation: "inputPuls 1.5s infinitie easy-in-out",
        BorderColor: "#ff8000",
        pointerEvents: "none",
    },
}));

const Terminal = () => {
    const {
        mode,
        value,
        setValue,
        lastValues,
        handleSubmit,
        lastValuesIndex,
        setLastValuesIndex,
        isLoading,
    } = useTerminal();
    return (
        <>
            {mode === "research" && lastValues.length > 0 && (
                <Typography
                    sx={{
                        color: "lightgray",
                        textOverflow: "ellipsis",
                        width: "60vw",
                        overflow: "hidden",
                        textWrap: "nowrap",
                    }}
                >
                    Last value: {lastValues[lastValuesIndex - 1]}
                </Typography>
            )}
            <TerminalInput
                className={clsx({ loading: isLoading })}
                variant="outlined"
                color={mode === "command" ? "warning" : "success"}
                startDecorator={">"}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter") {
                        handleSubmit();
                    }
                    switch (mode) {
                        case "research":
                            if (e.key === "ArrowUp") {
                                if (!lastValues.length || lastValuesIndex === 0) return;
                                if (lastValuesIndex === -1) {
                                    setLastValuesIndex(lastValues.length - 1);
                                    setValue(lastValues[lastValues.length - 1]);
                                    return;
                                }
                                const newIndex = Math.max(lastValuesIndex - 1, 0);
                                setLastValuesIndex(newIndex);
                                setValue(lastValues[newIndex]);
                            }
                            if (e.key === "ArrowDown") {
                                if (!lastValues.length || lastValuesIndex === lastValues.length)
                                    return;
                                if (lastValuesIndex === lastValues.length - 1) {
                                    setValue("");
                                    setLastValuesIndex(lastValues.length);
                                    return;
                                }
                                const newIndex = Math.min(
                                    lastValuesIndex + 1,
                                    lastValues.length - 1,
                                );
                                setLastValuesIndex(newIndex);
                                setValue(lastValues[newIndex]);
                            }
                            break;
                        default:
                            break;
                    }
                }}
            />
        </>
    );
};

export default Terminal;
