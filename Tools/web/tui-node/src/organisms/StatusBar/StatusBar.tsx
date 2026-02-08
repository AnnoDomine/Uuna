import { Box, Text } from "ink";
import type { FC } from "react";
import StatusLabel from "../../atoms/StatusLabel.js";
import { useStore } from "../../store/useStore.js";
import { STATUS_BAR_ITEMS } from "./statusBar.constants.js";

const Delimiter = ({ delimiter = "|" }) => <Text> {delimiter} </Text>;

const StatusBar: FC = () => {
	const { apiOnline, currentBuild, activeAgents } = useStore();

	const statusBar = STATUS_BAR_ITEMS(currentBuild, apiOnline, activeAgents);

	return (
		<Box borderStyle="round" borderColor="#414868" paddingX={1} width="100%">
			{statusBar.map((i, idx) =>
				i.id === "delimiter" ? (
					<Delimiter key={`${i.id}_${idx}`} delimiter={i.value} />
				) : (
					<StatusLabel key={i.id} {...i} />
				),
			)}
		</Box>
	);
};

export default StatusBar;
