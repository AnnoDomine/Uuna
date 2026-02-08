import { Box, Text } from "ink";
import type { FC } from "react";
import type { HeaderProps } from "./header.types.js";

const Header: FC<HeaderProps> = ({ title, subtitle }) => {
    return (
        <Box
            flexDirection="column"
            borderStyle="single"
            borderColor="#7aa2f7"
            paddingX={1}
            width="100%"
        >
            <Text color="#7aa2f7" bold>
                {title}
            </Text>
            {subtitle && <Text color="#565f89">{subtitle}</Text>}
        </Box>
    );
};

export default Header;
