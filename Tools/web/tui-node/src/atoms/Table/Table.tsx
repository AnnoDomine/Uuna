/**
 * This component is a copy and past working version of the Table component from the no more maintained repo "ink-table"
 * @link https://github.com/maticzav/ink-table/issues/268#issue-2068855920
 */
// Table.tsx

import { Box, Text } from "ink";
import React, { type FC } from "react";
import ScrollArea from "../../organisms/ScrollArea/ScrollArea.js";
import type { EFocusAreal } from "../../store/useFocusStore.js";

type Scalar = string | number | boolean | null | undefined;

type ScalarDict = {
	[key: string]: Scalar;
};

type Column = {
	key: string;
	width: number;
};

type TableProps = {
	id: string;
	areal?: EFocusAreal;
	data: ScalarDict[];
	showHeaders?: boolean;
	headerStyles?: {
		color?: string;
		backgroundColor?: string;
		bold?: boolean;
		italic?: boolean;
		underline?: boolean;
		inverse?: boolean;
		strikethrough?: boolean;
		dimColor?: boolean;
	};
};

// Helper function to generate headers from data
function generateHeaders(data: ScalarDict[]): ScalarDict {
	const headers: ScalarDict = {};

	data.forEach((row) => {
		Object.keys(row).forEach((key) => {
			headers[key] = key;
		});
	});

	return headers;
}

// biome-ignore lint/suspicious/noExplicitAny: See header
type RowProps = { row: ScalarDict; columns: Column[]; textStyles?: any };

// Helper function to render a row with separators
const Row: FC<RowProps> = ({ row, columns, textStyles }) => {
	return (
		<Box flexDirection="row">
			<Text>│</Text>
			{columns.map((column, index) => (
				<React.Fragment key={column.key}>
					{index !== 0 && <Text>│</Text>}
					{/* Add separator before each cell except the first one */}
					<Box width={column.width} justifyContent="center">
						<Text {...textStyles}>{row[column.key]?.toString() || ""}</Text>
					</Box>
				</React.Fragment>
			))}
			<Text>│</Text>
		</Box>
	);
};

const Table = ({
	data,
	showHeaders = true,
	headerStyles,
	id,
	areal,
}: TableProps) => {
	// Determine columns and their widths
	const columns: Column[] = getColumns(data);

	return (
		<Box flexDirection="column" height="100%" width="100%">
			<ScrollArea id={id} areal={areal}>
				{renderHeaderSeparators(columns)}

				{showHeaders && (
					<>
						<Row
							row={generateHeaders(data)}
							columns={columns}
							textStyles={{
								color: "blue",
								bold: true,
								...headerStyles,
							}}
						/>
						{renderRowSeparators(columns)}
					</>
				)}
				{data.map((row, index) => (
					<React.Fragment
						key={`row-${
							// biome-ignore lint/suspicious/noArrayIndexKey: see header
							index
						}`}
					>
						{index !== 0 && renderRowSeparators(columns)}
						<Row row={row} columns={columns} textStyles={headerStyles} />
					</React.Fragment>
				))}
				{renderFooterSeparators(columns)}
			</ScrollArea>
		</Box>
	);
};

// Helper function to determine columns and their widths
function getColumns(data: ScalarDict[]): Column[] {
	const columnWidths: { [key: string]: number } = {};

	data.forEach((row) => {
		Object.keys(row).forEach((key) => {
			const valueLength = row[key]?.toString().length || 0;
			columnWidths[key] = Math.max(
				columnWidths[key] || key.length,
				valueLength,
			);
		});
	});

	return Object.keys(columnWidths).map((key) => ({
		key: key,
		width: (columnWidths[key] ?? 0) + 2, // adding padding
	}));
}

function renderHeaderSeparators(columns: Column[]) {
	return renderRowSeparators(columns, "┌", "┬", "┐");
}

function renderFooterSeparators(columns: Column[]) {
	return renderRowSeparators(columns, "└", "┴", "┘");
}

function renderRowSeparators(
	columns: Column[],
	leftChar = "├",
	midChar = "┼",
	rightChar = "┤",
) {
	return (
		<Box flexDirection="row">
			<Text>{leftChar}</Text>
			{columns.map((column, index) => (
				<React.Fragment key={column.key}>
					<Text>{"─".repeat(column.width)}</Text>
					{index < columns.length - 1 ? (
						<Text>{midChar}</Text>
					) : (
						<Text>{rightChar}</Text>
					)}
				</React.Fragment>
			))}
		</Box>
	);
}

export default Table;
