import { useStdout } from "ink";
import { useEffect, useState } from "react";

/**
 * Enterprise Hook to track terminal dimensions dynamically.
 */
const useTerminalDimensions = () => {
    const { stdout } = useStdout();
    const [dimensions, setDimensions] = useState({
        width: stdout.columns,
        height: stdout.rows,
    });

    useEffect(() => {
        const handler = () => {
            setDimensions({
                width: stdout.columns,
                height: stdout.rows,
            });
        };

        stdout.on("resize", handler);
        return () => {
            stdout.off("resize", handler);
        };
    }, [stdout]);

    return dimensions;
};

export default useTerminalDimensions;
