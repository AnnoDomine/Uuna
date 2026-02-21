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
        height: 40,
    }),
}));

describe("App E2E", () => {
    it("should render the header with the app name", async () => {
        const { lastFrame } = render(<App />);

        // Wait for initial render
        await new Promise((resolve) => setTimeout(resolve, 500));

        const output = lastFrame();
        expect(output).toContain("WoW Library");
    });

    it("should render the command line prompt", async () => {
        const { lastFrame } = render(<App />);

        await new Promise((resolve) => setTimeout(resolve, 500));

        expect(lastFrame()).toContain("> ");
    });

    it("should allow navigating via command line", async () => {
        const { lastFrame, stdin } = render(<App />);

        // Wait for initial render
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Type command to go to Wiki (Faster typing for CI)
        const command = ":goto:wiki\r";
        for (const char of command) {
            stdin.write(char);
            await new Promise((resolve) => setTimeout(resolve, 10));
        }

        // Wait for page switch
        let found = false;
        // Check for up to 10 seconds (50 * 200ms)
        for (let i = 0; i < 50; i++) {
            await new Promise((resolve) => setTimeout(resolve, 200));
            const frame = lastFrame();
            // We check for "WIKI" which appears in the Wiki organism header
            if (frame?.includes("WIKI")) {
                found = true;
                break;
            }
        }

        expect(found).toBe(true);
    }, 15000); // Set explicit timeout to 15s for CI stability
});
