import { Text } from 'ink';
import { marked } from 'marked';
import { markedTerminal, type TerminalRendererOptions } from 'marked-terminal';
import React from 'react';

export type Props = TerminalRendererOptions & {
  children: string;
};

export default function Markdown({ children, ...options }: Props) {
  marked.use(markedTerminal(options));
  const parsedMarkdown = marked.parse(children) as string;
  return React.createElement(Text, null, parsedMarkdown);
}
