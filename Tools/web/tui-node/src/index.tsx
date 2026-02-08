import { Box, render } from "ink";
import type React from "react";
import Header from "./atoms/Header/Header.js";
import useBackend from "./hooks/useBackend.js";
import Navigation from "./molecules/Navigation/Navigation.js";
import PageSwitcher from "./organisms/PageSwitcher/PageSwitcher.js";
import ScrollArea from "./organisms/ScrollArea/ScrollArea.js";
import StatusBar from "./organisms/StatusBar/StatusBar.js";
import Logs from "./pages/Logs/Logs.js";
import useDebugStore from "./store/useDebbugStore.js";
import { APP_NAME } from "./utils/constants/globals.js";

// Prevent MaxListenersExceededWarning
process.stdin.setMaxListeners(100);

const App: React.FC = () => {
    // Initialize backend management
    useBackend();
    const { enabled: isDebugEnabled } = useDebugStore();

    return (
        <Box flexDirection="column" width="100%" minHeight={20}>
            <Header title={APP_NAME} subtitle="Multi-Agent Orchestration & Vector Memory" />

            <Box flexDirection="row" flexGrow={1} height={30}>
                <Navigation />
                <Box
                    flexDirection="column"
                    paddingX={2}
                    flexGrow={1}
                    borderStyle="single"
                    borderColor="#414868"
                >
                    <PageSwitcher />
                </Box>
                {isDebugEnabled && (
                    <Box
                        flexDirection="column"
                        paddingX={2}
                        flexGrow={1}
                        borderStyle="single"
                        borderColor="#73FF00"
                    >
                        <ScrollArea id="logs-scroll-area">
                            <Logs />
                        </ScrollArea>
                    </Box>
                )}
            </Box>

            <StatusBar />
        </Box>
    );
};

render(<App />);
