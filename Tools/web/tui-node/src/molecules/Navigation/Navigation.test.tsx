import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import { ENavigationItems } from "./navigation.enums.js";
import useNavigation from "./navigation.hooks.js";

// Mock store
const mockSetCurrentPage = vi.fn();
vi.mock("../../store/useStore.js", () => ({
    useStore: () => ({
        currentPage: ENavigationItems.HOME,
        setCurrentPage: mockSetCurrentPage,
    }),
}));

// Mock helper to avoid side effects (like process.exit if quit is called)
vi.mock("./navigation.helpers.js", () => ({
    handleSelectItemHelper: vi.fn(),
}));

// Import the mocked helper to assert on it
import { handleSelectItemHelper } from "./navigation.helpers.js";

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useNavigation>) => void }> = ({
    onRender,
}) => {
    const data = useNavigation();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useNavigation", () => {
    it("should return navigation items", () => {
        let result: ReturnType<typeof useNavigation> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.highlitedItems.length).toBeGreaterThan(0);
        // Check if Home is present
        expect(result?.highlitedItems.find((i) => i.value === ENavigationItems.HOME)).toBeDefined();
    });

    it("should handle selection", () => {
        let result: ReturnType<typeof useNavigation> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        result?.handleSelectItem(ENavigationItems.SETTINGS);
        expect(handleSelectItemHelper).toHaveBeenCalledWith(
            ENavigationItems.HOME, // current page from mock
            mockSetCurrentPage,
            ENavigationItems.SETTINGS,
        );
    });
});
