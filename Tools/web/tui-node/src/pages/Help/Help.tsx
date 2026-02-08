import { Box } from "ink";
import type { FC } from "react";
import Wiki from "../../organisms/Wiki/Wiki.js";

const Help: FC = () => {
    return (
        <Box flexDirection="column" paddingX={2} flexGrow={1}>
            <Wiki />
        </Box>
    );
};

export default Help;
