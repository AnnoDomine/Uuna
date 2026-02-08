import { Box, Newline, Text } from "ink";
import { ScrollList, type ScrollListRef } from "ink-scroll-list";
import { useCallback, useMemo, useRef, useState } from "react";
import { useScopedInput } from "../../hooks/useScopedInput.js";
import { EFocusAreal } from "../../store/useFocusStore.js";

type Overrides = Partial<{
    unselected_item_color: string;
    selected_item_color: string;
    selected_item_prefix: string;
    selected_item_suffix: string;
    unselected_item_prefix: string;
    unselected_item_suffix: string;
    un_focused_color: string;
    focused_color: string;
}>;

type Options = Partial<{
    mark_first_item_after_select: boolean;
    width: number;
    height: number;
    areal: EFocusAreal;
}>;

// biome-ignore lint/suspicious/noExplicitAny: Allow everything
type DefaultMeta = any;

type Item<IM extends DefaultMeta = DefaultMeta> = Record<"label" | "value" | "id", string> & {
    meta: IM;
};

type Parsers<IM extends DefaultMeta = DefaultMeta> = Partial<{
    parseSelectedPrefix: (prefix: string) => string;
    parseSelectedSuffix: (suffix: string) => string;
    parseUnselectedPrefix: (prefix: string) => string;
    parseUnselectedSuffix: (suffix: string) => string;
    parseSlectedItem: (item: Item<IM>) => Item<IM>;
    parseUnselectedItem: (item: Item<IM>) => Item<IM>;
}>;

type Props<IM extends DefaultMeta = DefaultMeta> = {
    items: Array<Item<IM>>;
    onSelect: (id: string) => void;
    overrides?: Overrides;
    options?: Options;
    parsers?: Parsers;
    id?: string;
};

const ScrollableSelection = <IM extends DefaultMeta = DefaultMeta>({
    items,
    onSelect,
    overrides = {},
    options = {},
    id = "undefined_id",
    parsers = {},
}: Props<IM>) => {
    const usedOptions: Required<Options> = {
        mark_first_item_after_select: false,
        width: 30,
        height: 30,
        areal: EFocusAreal.CONTENT,
        ...options,
    };

    const listRef = useRef<ScrollListRef>(null);
    const [selectedIndex, setSelectedIndex] = useState(0);

    // Use our enterprise scoped input hook
    const { isFocused } = useScopedInput({
        id,
        areal: usedOptions.areal,
        keyMap: (_input, key) => {
            if (key.upArrow) {
                setSelectedIndex((prev) => Math.max(prev - 1, 0));
            }
            if (key.downArrow) {
                setSelectedIndex((prev) => Math.min(prev + 1, items.length - 1));
            }
            if (key.pageUp) {
                setSelectedIndex((prev) => Math.max(prev - 10, 0));
            }
            if (key.pageDown) {
                setSelectedIndex((prev) => Math.min(prev + 10, items.length - 1));
            }
            if (key.home) {
                setSelectedIndex(0);
            }
            if (key.end) {
                setSelectedIndex(items.length - 1);
            }
            if (key.return) {
                if (items[selectedIndex]) {
                    onSelect(items[selectedIndex].id);
                    if (usedOptions.mark_first_item_after_select) setSelectedIndex(0);
                }
            }
        },
    });

    const parseItem = useCallback(
        (item: Item<IM>, selected = false) => {
            let parser: undefined | ((item: Item<IM>) => Item<IM>);
            if (selected) {
                parser = parsers.parseSlectedItem;
            } else {
                parser = parsers.parseUnselectedItem;
            }
            if (parser) {
                return parser(item);
            }
            return item;
        },
        [parsers],
    );

    const parsePrefixSuffix = useCallback(
        (type: "prefix" | "suffix", value: string, selected = false) => {
            let parser: undefined | ((value: string) => string);
            switch (type) {
                case "prefix":
                    parser = selected ? parsers.parseSelectedPrefix : parsers.parseUnselectedPrefix;
                    break;
                case "suffix":
                    parser = selected ? parsers.parseSelectedSuffix : parsers.parseUnselectedSuffix;
                    break;
                default:
                    return value;
            }
            if (parser) {
                return parser(value);
            }
            return value;
        },
        [parsers],
    );

    const constants: NonNullable<Required<Overrides>> = useMemo(
        () => ({
            unselected_item_color: "white",
            selected_item_color: "green",
            selected_item_prefix: "> ",
            selected_item_suffix: "",
            unselected_item_prefix: "",
            unselected_item_suffix: "",
            un_focused_color: "white",
            focused_color: "green",
            ...overrides, // Override constants
        }),
        [overrides],
    );

    const getItemValue = useCallback(
        (item: Item<IM>, selected = false): string => {
            if (selected) {
                return `${parsePrefixSuffix("prefix", constants.selected_item_prefix, true)}${parseItem(item).label}${parsePrefixSuffix("suffix", constants.selected_item_suffix, true)}`;
            }
            return `${parsePrefixSuffix("prefix", constants.unselected_item_prefix)}${parseItem(item).label}${parsePrefixSuffix("suffix", constants.unselected_item_suffix)}`;
        },
        [parseItem, parsePrefixSuffix, constants],
    );

    return (
        <Box
            flexGrow={1}
            flexDirection="column"
            padding={1}
            borderStyle="round"
            borderColor={isFocused ? constants.focused_color : constants.un_focused_color}
            width={usedOptions.width}
            height={usedOptions.height}
        >
            {
                // If items are above view-point, show arrow above the list
                selectedIndex > 0 ? <Text>----- ↑ -----</Text> : <Text>-------------</Text>
            }
            <Newline />
            <ScrollList ref={listRef} selectedIndex={selectedIndex}>
                {items.map((item, index) => (
                    <Box key={item.id}>
                        <Text
                            color={
                                index === selectedIndex
                                    ? constants.selected_item_color
                                    : constants.unselected_item_color
                            }
                        >
                            {index === selectedIndex
                                ? getItemValue(item, true)
                                : getItemValue(item)}
                        </Text>
                    </Box>
                ))}
            </ScrollList>
            <Newline />
            {
                // If items are below view-point, show arrow below the list
                selectedIndex < items.length - 1 ? (
                    <Text>----- ↓ -----</Text>
                ) : (
                    <Text>-------------</Text>
                )
            }
        </Box>
    );
};

export default ScrollableSelection;
