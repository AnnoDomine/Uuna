import { Box, Text } from "ink";
import type { FC } from "react";
import Table from "../../atoms/Table/Table.js";
import ScrollableSelection from "../../molecules/ScrollableSelection/ScrollableSelection.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import { KEYBINDINGS_DATA } from "./help.constants.js";
import useHelp from "./help.hooks.js";
import { EHelpTopic } from "./help.types.js";

const Help: FC = () => {
    const { activeTopic, topics, handleSelectTopic } = useHelp();

    return (
        <Box flexDirection="row" flexGrow={1} height="100%" width="100%">
            {/* Left Side: Topic Selection */}
            <Box flexDirection="column" width={30} paddingRight={1} height="100%">
                <Text color="#bb9af7" bold underline>
                    Help Topics
                </Text>
                <Box marginTop={1} flexGrow={1}>
                    <ScrollableSelection
                        items={topics}
                        onSelect={handleSelectTopic}
                        options={{
                            width: "100%",
                            height: "100%",
                            areal: EFocusAreal.CONTENT,
                        }}
                    />
                </Box>
            </Box>

            {/* Right Side: Topic Content */}
            <Box flexDirection="column" flexGrow={1} height="100%" width="100%">
                {activeTopic === EHelpTopic.KEYBINDINGS && (
                    <Box flexDirection="column">
                        <Text color="#7aa2f7" bold>
                            KEYBINDINGS REFERENCE
                        </Text>
                        <Box marginTop={1} flexGrow={1} width="100%" height="100%">
                            <Table
                                data={KEYBINDINGS_DATA.map((k) => ({
                                    Key: k.key,
                                    Action: k.action,
                                    Scope: k.scope,
                                }))}
                                headerStyles={{ color: "cyan" }}
                                id="help-keybindings-table"
                            />
                        </Box>
                    </Box>
                )}

                {activeTopic !== EHelpTopic.KEYBINDINGS && (
                    <Box>
                        <Text color="gray italic">Content for {activeTopic} coming soon...</Text>
                    </Box>
                )}
            </Box>
        </Box>
    );
};

export default Help;
