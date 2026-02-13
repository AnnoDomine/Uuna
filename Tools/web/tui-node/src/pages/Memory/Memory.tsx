import { Box, Text } from "ink";
import TextInput from "ink-text-input";
import type { FC } from "react";
import { useScopedInput } from "../../hooks/useScopedInput.js";
import ScrollableSelection from "../../molecules/ScrollableSelection/ScrollableSelection.js";
import ScrollArea from "../../organisms/ScrollArea/ScrollArea.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import { MEMORY_ROLES } from "./memory.constants.js";
import useMemory from "./memory.hooks.js";

const Memory: FC = () => {
    const { query, setQuery, role, setRole, results, isLoading, handleSearch } = useMemory();

    // Search Input Scope
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
        <Box
            flexDirection="row"
            flexGrow={1}
            width="100%"
            height="100%"
            minHeight={0}
            justifyContent="space-between"
        >
            {/* Left Column: Search & Filters */}
            <Box flexDirection="column" width="30%" height="100%" flexGrow={1}>
                <Box flexDirection="column" width="100%" height={7} flexGrow={1}>
                    <Box height={2} width="100%">
                        <Text color="#bb9af7" bold underline>
                            Search Configuration
                        </Text>
                    </Box>

                    {/* Query Input */}
                    <Box
                        borderStyle="round"
                        borderColor={isSearchFocused ? "#7aa2f7" : "#24283b"}
                        paddingX={1}
                        flexDirection="column"
                        height={4}
                        width="100%"
                    >
                        <Text color={isSearchFocused ? "cyan" : "white"} bold>
                            Query:
                        </Text>
                        <TextInput
                            value={query}
                            onChange={setQuery}
                            focus={isSearchFocused}
                            placeholder="Enter keywords..."
                        />
                    </Box>
                </Box>

                <Box flexDirection="column" width="100%" height="100%" flexGrow={1}>
                    <Box height={1} width="100%">
                        <Text color="white" bold>
                            Target Role:
                        </Text>
                    </Box>

                    <Box flexGrow={1} height="100%" width="100%">
                        {/* Role Selection */}
                        <ScrollableSelection
                            items={MEMORY_ROLES}
                            onSelect={(v) => {
                                const selectedRole = MEMORY_ROLES.find((r) => r.id === v);
                                if (selectedRole) setRole(selectedRole.value);
                            }}
                            id="memory-role-select"
                            options={{
                                areal: EFocusAreal.CONTENT,
                            }}
                        />
                    </Box>
                </Box>
            </Box>

            {/* Right Column: Results */}
            <Box flexDirection="column" width="70%" height="100%" flexGrow={1}>
                <Box height={2} width="100%">
                    <Text color="#bb9af7" bold underline>
                        [{role}] Semantic Matches{" "}
                        {isLoading ? "(Searching...)" : `(${results.length})`}
                    </Text>
                </Box>
                <Box flexDirection="column" width="100%" height="100%" flexGrow={1}>
                    <ScrollArea id="memory-results-scroll">
                        {results.length > 0
                            ? results.map((result, index) => (
                                  <Box
                                      key={result.id || `match-${index}`}
                                      flexDirection="column"
                                      borderStyle="single"
                                      borderColor="#414868"
                                      paddingX={1}
                                  >
                                      <Box justifyContent="space-between">
                                          <Text color="cyan" bold>
                                              Result #{index + 1}
                                          </Text>
                                          <Text color="green">
                                              {(result.score * 100).toFixed(1)}% Match
                                          </Text>
                                      </Box>
                                      <Box marginTop={1}>
                                          <Text color="white">{result.content}</Text>
                                      </Box>
                                      <Box marginTop={1}>
                                          <Text color="gray" dimColor>
                                              Source: {result.metadata?.source || "Global Archive"}
                                          </Text>
                                      </Box>
                                  </Box>
                              ))
                            : !isLoading && (
                                  <Box padding={1} borderStyle="classic" borderColor="#24283b">
                                      <Text color="gray">
                                          Initiate a query to see semantically related patterns from
                                          the vector database.
                                      </Text>
                                  </Box>
                              )}
                    </ScrollArea>
                </Box>
            </Box>
        </Box>
    );
};

export default Memory;
