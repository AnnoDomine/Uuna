import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import useSettingsListItem from "./settings_list_item.hooks.js";

// Mock ScrollArea context
const mockScrollToItem = vi.fn();
vi.mock("../../organisms/ScrollArea/ScrollArea.js", () => ({
    useScrollAreaContext: () => ({
        scrollToItem: mockScrollToItem,
    }),
}));

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useSettingsListItem>) => void }> = ({
    onRender,
}) => {
    const data = useSettingsListItem(5);
    onRender(data);
    return <Text>Test</Text>;
};

describe("useSettingsListItem", () => {
    it("should provide handleFokusScroll", () => {
        let result: ReturnType<typeof useSettingsListItem> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.handleFokusScroll).toBeDefined();
    });

    it("should call scrollToItem with index when handleFokusScroll is called", () => {
        let result: ReturnType<typeof useSettingsListItem> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        result?.handleFokusScroll();
        expect(mockScrollToItem).toHaveBeenCalledWith(5);
    });
});
