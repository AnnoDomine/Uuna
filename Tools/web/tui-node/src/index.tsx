import { Box, render } from "ink";
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

// Prevent MaxListenersExceededWarning
process.stdin.setMaxListeners(100);

const App: React.FC = () => {
	// Initialize backend management
	useBackend();

	const { width, height } = useTerminalDimensions();
	const { enabled: isDebugEnabled } = useDebugStore();

	return (
		<Box flexDirection="column" width={width} height={height}>
			<Header
				title={APP_NAME}
				subtitle="Multi-Agent Orchestration & Vector Memory"
			/>

			<Box flexDirection="row" flexGrow={1}>
				{/* Sidebar: Statische Breite */}
				<Navigation />

				{/* Page Content: Dynamisch (nimmt den Rest) */}
				<Box
					flexDirection="column"
					paddingX={2}
					flexGrow={1}
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

			<StatusBar />
		</Box>
	);
};

render(<App />);
