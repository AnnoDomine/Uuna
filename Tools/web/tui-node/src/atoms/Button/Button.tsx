import { Text } from "ink";
import type { FC } from "react";

interface ButtonProps {
    label: string;
    onPress?: () => void;
    color?: string;
    isActive?: boolean;
}

const Button: FC<ButtonProps> = ({ label, onPress, color = "cyan", isActive = false }) => {
    return (
        <Text
            color={isActive ? "white" : color}
            backgroundColor={isActive ? color : undefined}
            bold
            onPress={onPress}
        >
            {` [ ${label} ] `}
        </Text>
    );
};

export default Button;
