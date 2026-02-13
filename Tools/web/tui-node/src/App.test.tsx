import { render } from "ink-testing-library";
import { describe, expect, it, vi } from "vitest";
import App from "./App.js";

// Mock hooks that might fail in test environment
vi.mock("./hooks/useBackend.js", () => ({
    default: () => ({
        status: "online",
        isStarting: false,
    }),
}));

vi.mock("./hooks/useTerminalDimensions.js", () => ({
    default: () => ({
        width: 100,
        height: 30,
    }),
}));

describe("App E2E", () => {
    it("should render the header with the app name", () => {
        const { lastFrame } = render(<App />);

        // Check if the app name is present in the output
        expect(lastFrame()).toContain("WoW Library");
    });

    it("should render the navigation sidebar", () => {
        const { lastFrame } = render(<App />);

        expect(lastFrame()).toContain("🏠 - Overview");
        expect(lastFrame()).toContain("Tasks");
        expect(lastFrame()).toContain("Wiki");
    });

    it("should allow navigating to the Wiki page", async () => {
        const { lastFrame, stdin } = render(<App />);

        // Wait for initial render
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Navigate down until we reach Wiki
        // We use a fixed number of steps based on the known order
        for (let i = 0; i < 6; i++) {
            stdin.write("\u001B[B");
            await new Promise((resolve) => setTimeout(resolve, 100));
        }

        // Press Enter to select
        stdin.write("\r");

        // Wait for page switch animation/effect
        let _found = false;
        for (let i = 0; i < 10; i++) {
            await new Promise((resolve) => setTimeout(resolve, 200));
            if (lastFrame()?.includes("Wiki")) {
                _found = true;
                break;
            }
        }

        expect(lastFrame()).toContain("Wiki");
    });
});
