import { Box, Text } from "ink";
import type React from "react";

interface StatusLabelProps {
    label: string;
    value: string | number;
    color?: string;
}

const StatusLabel: React.FC<StatusLabelProps> = ({ label, value, color = "cyan" }) => {
    return (
        <Box marginRight={1} marginLeft={1}>
            <Text color="white">{label}: </Text>
            <Text color={color} bold>
                {value}
            </Text>
        </Box>
    );
};

export default StatusLabel;
