import { Box, Text } from "ink";
import Spinner from "ink-spinner";
import ScrollableSelection, {
    type Item,
} from "../../molecules/ScrollableSelection/ScrollableSelection.js";
import type { BuildItem } from "../../store/useBuildsStore.js";
import { EFocusAreal } from "../../store/useFocusStore.js";
import useSelectBuild from "./selectBuild.hooks.js";

type Props = {
    id: string;
    selectedBuild: string | null;
    onChange: (build: string) => void;
};

const SelectBuild = ({ selectedBuild, onChange, id }: Props) => {
    const { parsedBuilds, error, isLoadingBuilds, isErrored } = useSelectBuild();
    return (
        <Box
            width="25%"
            flexDirection="column"
            borderStyle="single"
            borderColor={"green"}
            marginRight={1}
        >
            {isErrored && (
                <Box padding={1} flexGrow={1} flexDirection="column" minHeight={0}>
                    <Text color="red">{(error || "Unknown error").slice(0, 13)}</Text>
                </Box>
            )}
            <Box marginBottom={1} paddingX={1}>
                {isLoadingBuilds && <Spinner type="timeTravel" />}
                <Text bold color="green">
                    {selectedBuild
                        ? `SELECTED: ${selectedBuild}`
                        : `BUILDS (${parsedBuilds.length})`}
                </Text>
            </Box>
            <ScrollableSelection
                items={parsedBuilds}
                onSelect={onChange}
                id={id}
                options={{
                    height: "100%",
                    mark_first_item_after_select: false,
                    areal: EFocusAreal.CONTENT,
                }}
                parsers={{
                    overrideTextColor: (_idx, fallback, item) => {
                        const meta = (item as unknown as Item<BuildItem>).meta;
                        if (!meta.is_downloaded) return "red";
                        if (!meta.indexed) return "yellow";
                        if (item.id === selectedBuild) return "blue";
                        return fallback;
                    },
                }}
            />
        </Box>
    );
};

export default SelectBuild;
