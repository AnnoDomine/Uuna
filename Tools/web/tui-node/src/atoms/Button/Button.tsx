import { Text } from "ink";
import type { FC } from "react";

interface ButtonProps {
    label: string;
    onPress?: () => void;
    color?: string;
    isActive?: boolean;
}

const Button: FC<ButtonProps> = ({ label, color = "cyan", isActive = false }) => {
    return (
        <Text
            color={isActive ? "white" : color}
            backgroundColor={isActive ? color : undefined}
            bold
        >
            {` [ ${label} ] `}
        </Text>
    );
};

export default Button;
