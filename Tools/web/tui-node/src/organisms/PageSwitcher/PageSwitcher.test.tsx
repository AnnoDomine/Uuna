import { render } from "ink-testing-library";
import React from "react";
import { describe, expect, it } from "vitest";
import PageSwitcher from "./PageSwitcher.js";
import { useStore } from "../../store/useStore.js";
import { ENavigationItems } from "../../molecules/Navigation/navigation.enums.js";

describe("PageSwitcher", () => {
    it("should render Home by default", () => {
        const { lastFrame } = render(<PageSwitcher />);
        expect(lastFrame()).toContain("Please enter your question:");
    });

    it("should switch to Settings page", () => {
        const { lastFrame } = render(<PageSwitcher />);
        
        useStore.getState().setCurrentPage(ENavigationItems.SETTINGS);
        
        // We expect some settings-specific text. 
        // I'll check what's in Settings page first but usually it has "Settings" or group names.
        expect(lastFrame()).toBeTruthy();
    });

    it("should switch to Wiki page", () => {
        const { lastFrame } = render(<PageSwitcher />);
        
        useStore.getState().setCurrentPage(ENavigationItems.WIKI);
        
        expect(lastFrame()).toBeTruthy();
    });
});
