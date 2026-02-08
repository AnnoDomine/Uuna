import { Box, Text } from "ink";
import type { FC } from "react";
import type { HeaderProps } from "./header.types.js";

const Header: FC<HeaderProps> = ({ title, subtitle }) => {
    return (
        <Box
            flexDirection="row"
            justifyContent="space-between"
            borderStyle="single"
            borderColor="#7aa2f7"
            paddingX={1}
            width="100%"
            height={3}
        >
            <Text color="#7aa2f7" bold>
                {title}
            </Text>
            {subtitle && (
                <Text color="#7aa2f7" bold>
                    {subtitle}
                </Text>
            )}
        </Box>
    );
};

export default Header;
