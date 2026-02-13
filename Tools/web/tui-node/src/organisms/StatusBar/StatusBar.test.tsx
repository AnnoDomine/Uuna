import { render } from "ink-testing-library";
import { beforeEach, describe, expect, it } from "vitest";
import { useStore } from "../../store/useStore.js";
import StatusBar from "./StatusBar.js";

describe("StatusBar", () => {
    beforeEach(() => {
        // Reset store to default values
        useStore.setState({
            apiOnline: false,
            activeAgents: 0,
            currentBuild: "Midnight 12.0.0",
        });
    });

    it("should display the current build", () => {
        const { lastFrame } = render(<StatusBar />);
        expect(lastFrame()).toContain("Build: Midnight 12.0.0");
    });

    it("should update when API status changes", async () => {
        const { lastFrame } = render(<StatusBar />);
        expect(lastFrame()).toContain("API Health: Offline");

        // Manually update store
        useStore.getState().setApiOnline(true);

        // Wait for re-render
        await new Promise((resolve) => setTimeout(resolve, 500));

        expect(lastFrame()).toContain("API Health: Online");
    });

    it("should display active agent count", async () => {
        const { lastFrame } = render(<StatusBar />);

        useStore.getState().setAgents(5);

        // Wait for re-render
        await new Promise((resolve) => setTimeout(resolve, 500));

        expect(lastFrame()).toContain("Agents: 5");
    });
});
