import fs from "node:fs";
import path from "node:path";
import { useCallback, useEffect, useMemo } from "react";
import { v4 as uuidV4 } from "uuid";
import { type LinkMappingItem, useWikiStore, type WikiState } from "../../contexts/WikiContext.js";

export const useWikiLogic = (): WikiState => {
    const {
        currentPage,
        setCurrentPage,
        currentLink,
        setCurrentLink,
        linkMapping,
        setLinkMapping,
        error,
        setError,
        loading,
        setLoading,
    } = useWikiStore();

    const parseForLinks = useCallback((data: string): Array<LinkMappingItem> => {
        // Regex to find [**Label**](Link)
        const linkRegex = /\[\*\*([\s\S]+?)\*\*\]\(([\s\S]+?)\)/g;
        const foundLinks: Array<LinkMappingItem> = [
            {
                label: "Home",
                value: "Home.md",
                linkType: "internal",
                id: "home",
            },
        ];

        for (const match of data.matchAll(linkRegex)) {
            foundLinks.push({
                label: match[1],
                value: match[2],
                linkType: match[2].startsWith("http") ? "external" : "internal",
                id: uuidV4(),
            });
        }

        return foundLinks;
    }, []);

    const fetchWikiPage = useCallback(
        async (id: string) => {
            const linkItem = linkMapping.find((item) => item.id === id);
            if (!linkItem) {
                return;
            }
            setLoading(true);
            try {
                setError(null);
                // Adjust path resolution to be robust regardless of where the script is run from
                // Assuming process.cwd() is project root or TUI root.
                // We'll stick to the original logic but make it slightly more robust if needed.
                // Original: path.resolve(process.cwd(), "../../..") from TUI dir?
                // Let's assume process.cwd() is where the node process started.
                const projectRoot = path.resolve(process.cwd(), "../../..");
                const wikiDir = path.join(projectRoot, "docs/wiki/");
                const filePath = path.join(wikiDir, linkItem.value);

                const data = fs.readFileSync(filePath, "utf-8");
                setCurrentPage(data);
                setLinkMapping(parseForLinks(data));
                setCurrentLink(linkItem.label);
            } catch (err) {
                console.error(err);
                setError(`Failed to load wiki page: ${linkItem.value}`);
            } finally {
                setLoading(false);
            }
        },
        [
            linkMapping,
            parseForLinks,
            setLinkMapping,
            setCurrentLink,
            setCurrentPage,
            setLoading,
            setError,
        ],
    );

    // biome-ignore lint/correctness/useExhaustiveDependencies: Initialize
    useEffect(() => {
        if (!currentPage) fetchWikiPage("home");
    }, []);

    return useMemo(
        (): WikiState => ({
            currentPage,
            linkMapping,
            currentLink,
            error,
            fetchWikiPage,
            loading,
        }),
        [currentPage, linkMapping, currentLink, error, fetchWikiPage, loading],
    );
};
