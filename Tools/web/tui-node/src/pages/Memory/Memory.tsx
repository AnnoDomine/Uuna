import { Box, Text } from "ink";
import TextInput from "ink-text-input";
import type { FC } from "react";
import { useScopedInput } from "../../hooks/useScopedInput.js";
import ScrollArea from "../../organisms/ScrollArea/ScrollArea.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import useMemory from "./memory.hooks.js";

const Memory: FC = () => {
    const { query, setQuery, results, isLoading, handleSearch } = useMemory();

    // Search Input Focus + Logic
    const { isFocused: isSearchFocused } = useScopedInput({
        id: "memory-search-input",
        areal: EFocusAreal.CONTENT,
        autoFocus: true,
        keyMap: (_input, key) => {
            if (key.return) {
                handleSearch();
            }
        },
    });

    return (
        <Box flexDirection="column" flexGrow={1} padding={1}>
            <Box marginBottom={1}>
                <Text color="#7aa2f7" bold>
                    VECTOR MEMORY SEARCH
                </Text>
            </Box>

            {/* Search Box */}
            <Box
                borderStyle="round"
                borderColor={isSearchFocused ? "#7aa2f7" : "#24283b"}
                paddingX={1}
                marginBottom={1}
            >
                <Text color={isSearchFocused ? "cyan" : "white"}>Search Query: </Text>
                <TextInput
                    value={query}
                    onChange={setQuery}
                    focus={isSearchFocused}
                    placeholder="Enter lore, mechanics or technical patterns..."
                />
            </Box>

            <Box marginBottom={1}>
                <Text dimColor color="gray">
                    Press [Enter] to query the semantic memory archive.
                </Text>
            </Box>

            {isLoading && <Text color="yellow">Scanning vector patterns...</Text>}

            <Box flexGrow={1} flexDirection="column">
                <ScrollArea id="memory-results-scroll">
                    {results.length > 0
                        ? results.map((result, index) => (
                              <Box
                                  key={result.id}
                                  flexDirection="column"
                                  borderStyle="single"
                                  borderColor="#414868"
                                  paddingX={1}
                                  marginBottom={1}
                              >
                                  <Box justifyContent="space-between">
                                      <Text color="#bb9af7" bold>
                                          Match #{index + 1}
                                      </Text>
                                      <Text color="green">
                                          {(result.similarity * 100).toFixed(1)}% Match
                                      </Text>
                                  </Box>
                                  <Box marginTop={1}>
                                      <Text color="white">{result.content}</Text>
                                  </Box>
                                  <Box marginTop={1}>
                                      <Text color="gray" dimColor>
                                          Role: {result.role} | Source:{" "}
                                          {result.metadata?.source || "Archive"}
                                      </Text>
                                  </Box>
                              </Box>
                          ))
                        : !isLoading && (
                              <Box padding={1}>
                                  <Text color="gray">No patterns matched your query yet.</Text>
                              </Box>
                          )}
                </ScrollArea>
            </Box>
        </Box>
    );
};

export default Memory;
