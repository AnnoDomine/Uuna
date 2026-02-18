import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import { EFocusAreal } from "../../store/useFocusStore.js";
import useScrollArea from "./scroll_area.hooks.js";

// Mocks
const mockSetScrollOffset = vi.fn();
const mockSetScrollRef = vi.fn();

vi.mock("../../store/useScrollStore.js", () => ({
    default: () => ({
        scrollOffset: 0,
        setScrollOffset: mockSetScrollOffset,
        setScrollRef: mockSetScrollRef,
    }),
}));

vi.mock("../../hooks/useScopedInput.js", () => ({
    useScopedInput: () => ({
        isFocused: true,
    }),
}));

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useScrollArea>) => void }> = ({
    onRender,
}) => {
    const data = useScrollArea("test-id", EFocusAreal.CONTENT);
    onRender(data);
    return <Text>Test</Text>;
};

describe("useScrollArea", () => {
    it("should initialize with default values", () => {
        let result: ReturnType<typeof useScrollArea> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result).toBeDefined();
        expect(result?.scrollOffset).toBe(0);
        expect(result?.isFocused).toBe(true);
        expect(result?.scrollRef).toBeDefined();
    });

    it("should set scroll ref on mount", () => {
        render(<TestComponent onRender={() => {}} />);
        expect(mockSetScrollRef).toHaveBeenCalled();
    });
});
