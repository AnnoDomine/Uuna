import { render } from "ink-testing-library";
import React from "react";
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
		await new Promise(resolve => setTimeout(resolve, 100));

		// Navigate down 5 times to reach "Wiki" (Overview -> Tasks -> Memory -> Scoring -> Settings -> Wiki)
		// ArrowDown is usually \u001B[B
		for (let i = 0; i < 5; i++) {
			stdin.write("\u001B[B");
			await new Promise(resolve => setTimeout(resolve, 50));
		}
		
		// Press Enter to select
		stdin.write("\r");
		await new Promise(resolve => setTimeout(resolve, 100));

		// Check if we are on the Wiki page (should show wiki content or title)
		expect(lastFrame()).toContain("📖 - Wiki");
	});
});
