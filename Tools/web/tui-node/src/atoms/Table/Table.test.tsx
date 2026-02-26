import { render } from "ink-testing-library";
import { describe, expect, it, vi } from "vitest";
import Table from "./Table.js";

// Mock ScrollArea since Table depends on it and we want to isolate Table logic (mostly helpers)
vi.mock("../../organisms/ScrollArea/ScrollArea.js", () => ({
    default: ({ children }: { children: React.ReactNode }) => children,
}));

describe("Table", () => {
    const testData = [
        { id: 1, name: "Alice", role: "Admin" },
        { id: 2, name: "Bob", role: "User" },
    ];

    it("renders data correctly", () => {
        const { lastFrame } = render(<Table id="test-table" data={testData} />);
        const frame = lastFrame();

        // Check content
        expect(frame).toContain("Alice");
        expect(frame).toContain("Bob");
        expect(frame).toContain("Admin");
        expect(frame).toContain("User");
    });

    it("renders headers by default", () => {
        const { lastFrame } = render(<Table id="test-table" data={testData} />);
        const frame = lastFrame();

        expect(frame).toContain("id");
        expect(frame).toContain("name");
        expect(frame).toContain("role");
    });

    it("hides headers when requested", () => {
        const { lastFrame } = render(<Table id="test-table" data={testData} showHeaders={false} />);
        const frame = lastFrame();

        // Should not contain headers (unless they match data values, which they don't here)
        // But since we mock ScrollArea, layout might be simplified.
        // We check that we don't see the header row explicitly if we could, but string matching "id" might match data "id" if present.
        // Here keys are id, name, role. Values are 1, Alice, Admin...
        // So checking for "name" should be safe if no user is named "name".
        expect(frame).not.toContain("name");
    });
});
