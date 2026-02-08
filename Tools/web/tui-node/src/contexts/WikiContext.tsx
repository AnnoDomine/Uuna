import fs from "node:fs";
import path from "node:path";
import { useCallback, useEffect, useMemo } from "react";
import { v4 as uuidV4 } from "uuid";
import { create } from "zustand";

export interface LinkMappingItem {
    id: string;
    label: string;
    value: string;
    linkType: "internal" | "external"; // Externals are URL links
}

export interface WikiState {
    currentPage: string;
    currentLink: string;
    linkMapping: Array<LinkMappingItem>;
    error: string | null;
    fetchWikiPage: (id: string) => void;
    loading: boolean;
}

export interface WikiStore {
    currentPage: string;
    currentLink: string;
    linkMapping: Array<LinkMappingItem>;
    error: string | null;
    loading: boolean;
    setCurrentPage: (page: string) => void;
    setCurrentLink: (link: string) => void;
    setLinkMapping: (mapping: Array<LinkMappingItem>) => void;
    setError: (error: string | null) => void;
    setLoading: (loading: boolean) => void;
}

export const useWikiStore = create<WikiStore>((set) => ({
    currentPage: "",
    currentLink: "Home",
    linkMapping: [
        {
            label: "Home",
            value: "Home.md",
            linkType: "internal",
            id: "home",
        },
    ],
    error: null,
    loading: true,
    setCurrentPage: (page) => set({ currentPage: page }),
    setCurrentLink: (link) => set({ currentLink: link }),
    setLinkMapping: (mapping) => set({ linkMapping: mapping }),
    setError: (error) => set({ error }),
    setLoading: (loading) => set({ loading }),
}));

export const useWiki = (): WikiState => {
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

    // biome-ignore lint/correctness/useExhaustiveDependencies: Initialze
    useEffect(() => {
        if (!currentPage) fetchWikiPage("home");
    }, []);

    const value = useMemo(
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

    return value;
};
