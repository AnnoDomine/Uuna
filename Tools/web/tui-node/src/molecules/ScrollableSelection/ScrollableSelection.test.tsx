import { render } from "ink-testing-library";
import { describe, expect, it, vi } from "vitest";
import ScrollableSelection from "./ScrollableSelection.js";

// Mock useScopedInput to force focus
vi.mock("../../hooks/useScopedInput.js", () => ({
    useScopedInput: () => ({
        isFocused: true,
    }),
}));

// Mock ink-scroll-list since it might behave unexpectedly in test env or just to simplify
// Actually ink-scroll-list is a component, so we can let it render or shallow mock it.
// Let's try rendering it first.

describe("ScrollableSelection", () => {
    const items = [
        { id: "1", label: "Item 1", value: "1", meta: {} },
        { id: "2", label: "Item 2", value: "2", meta: {} },
    ];

    it("renders items", () => {
        const { lastFrame } = render(
            <ScrollableSelection items={items} onSelect={() => {}} id="test-list" />,
        );
        const frame = lastFrame();
        expect(frame).toContain("Item 1");
        expect(frame).toContain("Item 2");
    });

    it("marks selected item", () => {
        // Since we force focus and default index is 0, the first item should be marked
        const { lastFrame } = render(
            <ScrollableSelection items={items} onSelect={() => {}} id="test-list" />,
        );
        const frame = lastFrame();
        // Default prefix is "> "
        expect(frame).toContain("> Item 1");
    });
});
