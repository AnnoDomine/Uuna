import { Box } from "ink";
import type { FC } from "react";
import LogTable from "../../organisms/LogTable/LogTable.js";

const Logs: FC = () => {
    return (
        <Box flexDirection="column" flexGrow={1} padding={1}>
            <LogTable />
        </Box>
    );
};

export default Logs;
