import { Box, type BoxProps } from "ink";
import { ControlledScrollView } from "ink-scroll-view";
import type { FC, PropsWithChildren } from "react";
import { createContext, useContext } from "react";
import type { EFocusAreal } from "../../store/useFocusStore.js";
import useScrollArea from "./scroll_area.hooks.js";

interface ScrollAreaContextType {
	scrollToItem: (index: number) => void;
}

const ScrollAreaContext = createContext<ScrollAreaContextType | null>(null);

export const useScrollAreaContext = () => {
	const context = useContext(ScrollAreaContext);
	if (!context) {
		throw new Error("useScrollAreaContext must be used within a ScrollArea");
	}
	return context;
};

interface ScrollAreaProps {
	id: string;
	hideBoarder?: boolean;
	areal?: EFocusAreal;
}

const ScrollArea: FC<PropsWithChildren<ScrollAreaProps>> = ({
	children,
	id,
	hideBoarder = false,
	areal,
}) => {
	const { scrollRef, scrollOffset, scrollToItem, isFocused } = useScrollArea(
		id,
		areal,
	);

	const defaultBoxProps = {
		flexGrow: 1,
		width: "100%",
		height: "100%",
		minHeight: 1,
	};

	const boxProps: BoxProps = {
		...defaultBoxProps,
		borderStyle: hideBoarder ? undefined : "round",
		borderColor: !hideBoarder && isFocused ? "#7aa2f7" : "#24283b",
	};

	return (
		<ScrollAreaContext.Provider value={{ scrollToItem }}>
			<Box {...boxProps}>
				<ControlledScrollView ref={scrollRef} scrollOffset={scrollOffset}>
					{children}
				</ControlledScrollView>
			</Box>
		</ScrollAreaContext.Provider>
	);
};

export default ScrollArea;
