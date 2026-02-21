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
        await new Promise((resolve) => setTimeout(resolve, 1000));

        const output = lastFrame();
        // Check if the app name is present in the output
        expect(output).toContain("WoW Library");
    });

    it("should render the command line prompt", async () => {
        const { lastFrame } = render(<App />);

        await new Promise((resolve) => setTimeout(resolve, 1000));

        // CommandLine uses "> " as prompt
        expect(lastFrame()).toContain("> ");
    });

    it("should allow navigating via command line", async () => {
        const { lastFrame, stdin } = render(<App />);

        // Wait for initial render
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Type command to go to Wiki
        const command = ":goto:wiki\r";
        for (const char of command) {
            stdin.write(char);
            // Simulate human typing speed
            await new Promise((resolve) => setTimeout(resolve, 50));
        }

        // Wait for page switch and potential loading state
        let found = false;
        for (let i = 0; i < 20; i++) {
            await new Promise((resolve) => setTimeout(resolve, 200));
            const frame = lastFrame();
            if (frame?.toLowerCase().includes("wiki")) {
                found = true;
                break;
            }
        }

        expect(found).toBe(true);
    });
});
