import fs from "node:fs";
import { Text } from "ink";
import { render } from "ink-testing-library";
import type { FC } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useWikiStore } from "../../contexts/WikiContext.js";
import { useWikiLogic } from "./wiki.hooks.js";

// Mock fs and path
vi.mock("node:fs");
vi.mock("node:path", async () => {
    const actual = await vi.importActual("node:path");
    return {
        ...actual,
        resolve: vi.fn().mockReturnValue("/mock/root"),
        join: vi.fn((...args) => args.join("/")),
    };
});

// Dummy component to test the hook
const TestComponent: FC<{ onRender: (data: ReturnType<typeof useWikiLogic>) => void }> = ({
    onRender,
}) => {
    const data = useWikiLogic();
    onRender(data);
    return <Text>Test</Text>;
};

describe("useWikiLogic", () => {
    beforeEach(() => {
        // Reset store
        useWikiStore.setState({
            currentPage: "",
            currentLink: "Home",
            linkMapping: [
                {
                    label: "Home",
                    value: "Home.md",
                    linkType: "internal",
                    id: "home",
                },
            ],
            error: null,
            loading: true,
        });

        // Reset mocks
        vi.clearAllMocks();
    });

    it("should fetch home page on mount", () => {
        // Mock fs.readFileSync
        const mockContent = `# Home

Welcome to [**Wiki**](Wiki.md)`;
        vi.mocked(fs.readFileSync).mockReturnValue(mockContent);

        let result: ReturnType<typeof useWikiLogic> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        // Should try to read Home.md
        expect(fs.readFileSync).toHaveBeenCalledWith(
            expect.stringContaining("docs/wiki/Home.md"),
            "utf-8",
        );

        // Content should be updated
        expect(result?.currentPage).toBe(mockContent);
        expect(result?.currentLink).toBe("Home");
        expect(result?.loading).toBe(false);
    });

    it("should parse links from content", () => {
        const mockContent = `# Test

Link to [**Page**](Page.md) and [**External**](https://google.com)`;
        vi.mocked(fs.readFileSync).mockReturnValue(mockContent);

        let result: ReturnType<typeof useWikiLogic> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        // Check link mapping
        // 1 (Home) + 2 found links
        expect(result?.linkMapping).toHaveLength(3);

        const pageLink = result?.linkMapping.find((l) => l.label === "Page");
        expect(pageLink).toBeDefined();
        expect(pageLink?.value).toBe("Page.md");
        expect(pageLink?.linkType).toBe("internal");

        const extLink = result?.linkMapping.find((l) => l.label === "External");
        expect(extLink).toBeDefined();
        expect(extLink?.value).toBe("https://google.com");
        expect(extLink?.linkType).toBe("external");
    });

    it("should handle errors when fetching pages", () => {
        vi.mocked(fs.readFileSync).mockImplementation(() => {
            throw new Error("File not found");
        });

        let result: ReturnType<typeof useWikiLogic> | undefined;
        render(
            <TestComponent
                onRender={(data) => {
                    result = data;
                }}
            />,
        );

        expect(result?.error).toContain("Failed to load wiki page: Home.md");
        expect(result?.loading).toBe(false);
    });
});
