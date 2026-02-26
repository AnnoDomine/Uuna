import { render } from "ink-testing-library";
import { describe, expect, it, vi } from "vitest";
import WikiPage from "./WikiPage.js";

// Mock Wiki organism
vi.mock("../../organisms/Wiki/Wiki.js", () => ({
    default: () => null,
}));

describe("WikiPage", () => {
    it("renders without crashing", () => {
        const { lastFrame } = render(<WikiPage />);
        expect(lastFrame()).toBeDefined();
    });
});
