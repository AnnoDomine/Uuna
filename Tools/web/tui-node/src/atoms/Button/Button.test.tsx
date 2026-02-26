import { render } from "ink-testing-library";
import { describe, expect, it } from "vitest";
import Button from "./Button.js";

describe("Button", () => {
    it("renders with label", () => {
        const { lastFrame } = render(<Button label="Click Me" />);
        expect(lastFrame()).toContain("[ Click Me ]");
    });

    it("renders active state correctly", () => {
        // Since we can't easily check colors in raw text output of ink-testing-library (unless using experimental features),
        // we mainly check that it renders without error.
        // In a real TUI test we might check ANSI codes if needed.
        const { lastFrame } = render(<Button label="Active" isActive={true} />);
        expect(lastFrame()).toContain("[ Active ]");
    });
});
