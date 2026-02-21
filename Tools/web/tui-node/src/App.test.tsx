import { render } from "ink-testing-library";
import { describe, expect, it, vi } from "vitest";
import App from "./App.js";

// Mock hooks
vi.mock("./hooks/useBackend.js", () => ({
    default: () => ({
        status: "online",
        isStarting: false,
        restartBackend: vi.fn(),
    }),
}));

vi.mock("./hooks/useTerminalDimensions.js", () => ({
    default: () => ({
        width: 100,
        height: 50,
    }),
}));

vi.mock("axios", () => ({
    default: {
        get: vi.fn(() => Promise.resolve({ data: {} })),
        post: vi.fn(() => Promise.resolve({ data: {} })),
    },
}));

describe("App E2E", () => {
    it("should render the header with the app name", async () => {
        const { lastFrame } = render(<App />);
        await new Promise((resolve) => setTimeout(resolve, 1500));
        expect(lastFrame()).toContain("WoW Library");
    });

    it("should render the command line prompt", async () => {
        const { lastFrame } = render(<App />);
        await new Promise((resolve) => setTimeout(resolve, 1500));
        expect(lastFrame()).toContain("> ");
    });

    it("should allow navigating via command line", async () => {
        const { lastFrame, stdin } = render(<App />);

        // Wait longer for initial render and focus stability
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // 1. Type command with even more delay between chars
        const commandText = ":goto:wiki";
        for (const char of commandText) {
            stdin.write(char);
            await new Promise((resolve) => setTimeout(resolve, 100));
        }

        // Verify typing is visible (using a partial match if first char dropped, but we want full)
        const output = lastFrame();
        expect(output).toContain(commandText);

        // 2. Execute
        stdin.write("\r");

        // 3. Wait for feedback or page change
        let found = false;
        for (let i = 0; i < 30; i++) {
            await new Promise((resolve) => setTimeout(resolve, 300));
            const frame = lastFrame();
            // Check for navigation feedback or the Wiki title
            if (frame?.includes("Navigated to wiki") || frame?.includes("WIKI")) {
                found = true;
                break;
            }
        }

        expect(found).toBe(true);
    }, 30000); // 30s timeout for total safety
});
