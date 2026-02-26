import { Text } from "ink";
import { render } from "ink-testing-library";
import { describe, expect, it, vi } from "vitest";
import Help from "./Help.js";
import { EHelpTopic } from "./help.types.js";

// Mock hooks and components
vi.mock("./help.hooks.js", () => ({
    default: () => ({
        activeTopic: EHelpTopic.KEYBINDINGS,
        topics: [{ label: "Keybindings", value: EHelpTopic.KEYBINDINGS, id: "1" }],
        handleSelectTopic: vi.fn(),
    }),
}));

vi.mock("../../atoms/Table/Table.js", () => ({
    default: () => <Text>Table Mock</Text>,
}));

vi.mock("../../molecules/ScrollableSelection/ScrollableSelection.js", () => ({
    default: () => <Text>Selection Mock</Text>,
}));

describe("Help Page", () => {
    it("renders keybindings table when active", () => {
        const { lastFrame } = render(<Help />);
        expect(lastFrame()).toContain("KEYBINDINGS REFERENCE");
        expect(lastFrame()).toContain("Table Mock");
    });
});
