import { Text } from "ink";
import { render } from "ink-testing-library";
import { describe, expect, it, vi } from "vitest";
import Logs from "./Logs.js";

vi.mock("../../organisms/LogTable/LogTable.js", () => ({
    default: () => <Text>LogTable Mock</Text>,
}));

describe("Logs Page", () => {
    it("renders LogTable", () => {
        const { lastFrame } = render(<Logs />);
        expect(lastFrame()).toContain("LogTable Mock");
    });
});
