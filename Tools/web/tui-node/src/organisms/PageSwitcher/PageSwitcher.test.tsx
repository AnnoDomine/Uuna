import { render } from "ink-testing-library";
import { describe, expect, it } from "vitest";
import { ENavigationItems } from "../../molecules/Navigation/navigation.enums.js";
import { useStore } from "../../store/useStore.js";
import PageSwitcher from "./PageSwitcher.js";

describe("PageSwitcher", () => {
    it("should render Home by default", () => {
        const { lastFrame } = render(<PageSwitcher />);
        expect(lastFrame()).toContain("Please enter your question:");
    });

    it("should switch to Settings page", async () => {
        const { lastFrame } = render(<PageSwitcher />);

        useStore.getState().setCurrentPage(ENavigationItems.SETTINGS);

        await new Promise((resolve) => setTimeout(resolve, 100));

        expect(lastFrame()).toContain("AI & SYSTEM SETTINGS");
    });

    it("should switch to Wiki page", async () => {
        const { lastFrame } = render(<PageSwitcher />);

        useStore.getState().setCurrentPage(ENavigationItems.WIKI);

        await new Promise((resolve) => setTimeout(resolve, 100));

        expect(lastFrame()).toContain("WIKI:");
    });
});
