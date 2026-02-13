import { Box } from "ink";
import type React from "react";
import Header from "./atoms/Header/Header.js";
import useBackend from "./hooks/useBackend.js";
import useTerminalDimensions from "./hooks/useTerminalDimensions.js";
import Navigation from "./molecules/Navigation/Navigation.js";
import PageSwitcher from "./organisms/PageSwitcher/PageSwitcher.js";
import StatusBar from "./organisms/StatusBar/StatusBar.js";
import Logs from "./pages/Logs/Logs.js";
import useDebugStore from "./store/useDebugStore.js";
import { APP_NAME } from "./utils/constants/globals.js";

const App: React.FC = () => {
    // Initialize backend management
    useBackend();

    const { width, height } = useTerminalDimensions();
    const { enabled: isDebugEnabled } = useDebugStore();

    return (
        <Box flexDirection="column" width={width} height={height}>
            <Box height={4} width="100%">
                <Header title={APP_NAME} subtitle="Multi-Agent Orchestration & Vector Memory" />
            </Box>

            <Box flexDirection="row" flexGrow={1} width="100%" height="100%">
                {/* Sidebar: Statische Breite */}
                <Box width={30} height="100%">
                    <Navigation />
                </Box>

                {/* Page Content: Dynamisch (nimmt den Rest) */}
                <Box
                    flexDirection="column"
                    paddingX={2}
                    flexGrow={1}
                    height="100%"
                    width="100%"
                    borderStyle="single"
                    borderColor="#414868"
                >
                    <PageSwitcher />
                </Box>

                {/* Debug Logs: Prozentuale Breite (z.B. 30%) */}
                {isDebugEnabled && (
                    <Box
                        flexDirection="column"
                        padding={1}
                        width={90}
                        borderStyle="single"
                        borderColor="#73FF00"
                        height="100%"
                        minWidth={90}
                    >
                        <Logs />
                    </Box>
                )}
            </Box>

            <Box height={3} width="100%">
                <StatusBar />
            </Box>
        </Box>
    );
};

export default App;
