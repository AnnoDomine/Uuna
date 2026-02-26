import { Box, Text } from "ink";
import Markdown from "ink-markdown";
import type { FC } from "react";
import ScrollableSelection from "../../molecules/ScrollableSelection/ScrollableSelection.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import ScrollArea from "../ScrollArea/ScrollArea.js";
import { useWikiLogic } from "./wiki.hooks.js";

const Wiki: FC = () => {
    const { error, currentPage, currentLink, fetchWikiPage, linkMapping, loading } = useWikiLogic();

    if (loading) {
        return (
            <Box padding={1}>
                <Text color="yellow" bold>
                    Loading...
                </Text>
            </Box>
        );
    }

    if (error) {
        return (
            <Box padding={1}>
                <Text color="red" bold>
                    {error}
                </Text>
            </Box>
        );
    }

    return (
        <Box flexDirection="row" flexGrow={1} height="100%" width="100%">
            <Box flexDirection="column" flexGrow={1}>
                <Box marginBottom={1}>
                    <Text color="#7aa2f7" bold underline>
                        WIKI: {currentLink.toLocaleUpperCase()}
                    </Text>
                </Box>
                {/* Wrap Markdown in a focusable ScrollArea */}
                <Box flexDirection="column" flexGrow={1} height="100%" width="100%">
                    <ScrollArea id="wiki-content-scroll">
                        <Box paddingX={1} flexDirection="column">
                            <Markdown>{currentPage}</Markdown>
                        </Box>
                    </ScrollArea>
                </Box>
            </Box>
            <ScrollableSelection
                items={linkMapping.map((item) => ({
                    ...item,
                    label: item.linkType === "external" ? `${item.label} 🌎` : item.label,
                    meta: item,
                }))}
                onSelect={(v) => fetchWikiPage(v)}
                options={{
                    mark_first_item_after_select: true,
                    width: 30,
                    height: "100%",
                    areal: EFocusAreal.CONTENT,
                }}
            />
        </Box>
    );
};

export default Wiki;
