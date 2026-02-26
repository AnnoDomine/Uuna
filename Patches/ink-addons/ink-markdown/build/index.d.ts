import { type TerminalRendererOptions } from 'marked-terminal';
import React from 'react';
export type Props = TerminalRendererOptions & {
    children: string;
};
export default function Markdown({ children, ...options }: Props): React.FunctionComponentElement<import("ink").TextProps>;
