import { Box } from "ink";
import type React from "react";
import Header from "./atoms/Header/Header.js";
import useBackend from "./hooks/useBackend.js";
import useExpress from "./hooks/useExpress.js";
import useTerminalDimensions from "./hooks/useTerminalDimensions.js";
import CommandLine from "./organisms/CommandLine/CommandLine.js";
import PageSwitcher from "./organisms/PageSwitcher/PageSwitcher.js";
import StatusBar from "./organisms/StatusBar/StatusBar.js";
import Logs from "./pages/Logs/Logs.js";
import useDebugStore from "./store/useDebugStore.js";
import { APP_NAME } from "./utils/constants/globals.js";

const App: React.FC = () => {
    // Initialize backend management
    useBackend();
    // Initialize signal receiver for agent notifications
    useExpress();

    const { width, height } = useTerminalDimensions();
    const { enabled: isDebugEnabled } = useDebugStore();

    return (
        <Box flexDirection="column" width={width} height={height}>
            <Box height={4} width="100%">
                <Header title={APP_NAME} subtitle="Multi-Agent Orchestration & Vector Memory" />
            </Box>

            <Box flexDirection="row" flexGrow={1} width="100%">
                {/* Page Content: Now full width since Navigation is removed */}
                <Box
                    flexDirection="column"
                    paddingX={2}
                    flexGrow={1}
                    height="100%"
                    borderStyle="single"
                    borderColor="#414868"
                >
                    <PageSwitcher />
                </Box>

                {/* Debug Logs: Optional overlay or sidebar */}
                {isDebugEnabled && (
                    <Box
                        flexDirection="column"
                        padding={1}
                        width={90}
                        borderStyle="single"
                        borderColor="#73FF00"
                        height="100%"
                    >
                        <Logs />
                    </Box>
                )}
            </Box>

            {/* Bottom Section: Status and Command Line */}
            <Box flexDirection="column" width="100%">
                <CommandLine />
                <Box height={3}>
                    <StatusBar />
                </Box>
            </Box>
        </Box>
    );
};

export default App;
