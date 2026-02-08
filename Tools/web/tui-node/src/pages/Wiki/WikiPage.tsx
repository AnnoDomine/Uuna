import { Box } from "ink";
import type { FC } from "react";
import Wiki from "../../organisms/Wiki/Wiki.js";

const WikiPage: FC = () => {
	return (
		<Box flexDirection="column" flexGrow={1}>
			<Wiki />
		</Box>
	);
};

export default WikiPage;
