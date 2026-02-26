import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { describe, expect, it, vi } from "vitest";
import useSelectBuild from "./selectBuild.hooks.js";

// Mocks
const mockFetchBuilds = vi.fn();
const mockAddLog = vi.fn();

const mockBuilds = [
    {
        version: "10.0.0.12345",
        is_downloaded: true,
        indexed: true,
    },
    {
        version: "10.0.0.12346",
        is_downloaded: false,
        indexed: false,
    },
];

vi.mock("../../store/useBuildsStore.js", () => ({
    default: () => ({
        builds: mockBuilds,
        isLoading: false,
        isFetching: false,
        isUninitialised: false,
        isErrored: false,
        error: null,
        fetchBuilds: mockFetchBuilds,
    }),
}));

vi.mock("../../store/useDebugStore.js", () => ({
    default: () => ({
        addLog: mockAddLog,
    }),
}));

const TestComponent: FC<{ onRender: (data: ReturnType<typeof useSelectBuild>) => void }> = ({
    onRender,
}) => {
    const data = useSelectBuild();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useSelectBuild", () => {
    it("should return parsed builds", () => {
        let result: ReturnType<typeof useSelectBuild> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.parsedBuilds).toHaveLength(2);
        expect(result?.parsedBuilds[0]).toEqual({
            id: "10.0.0.12346",
            value: "10.0.0.12346",
            label: "10.0.0.12346",
            meta: mockBuilds[1],
        });
    });

    it("should return isLoadingBuilds as false when not loading", () => {
        let result: ReturnType<typeof useSelectBuild> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );
        expect(result?.isLoadingBuilds).toBe(false);
    });

    it("should return isErrored and error", () => {
        let result: ReturnType<typeof useSelectBuild> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );
        expect(result?.isErrored).toBe(false);
        expect(result?.error).toBeNull();
    });
});
