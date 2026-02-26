import { render } from "ink-testing-library";
import { describe, expect, it } from "vitest";
import StatusLabel from "./StatusLabel.js";

describe("StatusLabel", () => {
    it("renders label and value", () => {
        const { lastFrame } = render(<StatusLabel label="Status" value="Online" />);
        expect(lastFrame()).toContain("Status:");
        expect(lastFrame()).toContain("Online");
    });

    it("renders numeric value", () => {
        const { lastFrame } = render(<StatusLabel label="Count" value={42} />);
        expect(lastFrame()).toContain("Count:");
        expect(lastFrame()).toContain("42");
    });
});
