import { render } from "ink-testing-library";
import { describe, expect, it } from "vitest";
import Header from "./Header.js";

describe("Header", () => {
    it("renders title correctly", () => {
        const { lastFrame } = render(<Header title="Main Title" />);
        expect(lastFrame()).toContain("Main Title");
    });

    it("renders subtitle when provided", () => {
        const { lastFrame } = render(<Header title="Main Title" subtitle="Sub Title" />);
        expect(lastFrame()).toContain("Main Title");
        expect(lastFrame()).toContain("Sub Title");
    });
});
