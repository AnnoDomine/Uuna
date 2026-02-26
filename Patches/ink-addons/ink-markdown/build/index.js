import { Text } from 'ink';
import { marked } from 'marked';
import { markedTerminal } from 'marked-terminal';
import React from 'react';
export default function Markdown({ children, ...options }) {
    marked.use(markedTerminal(options));
    const parsedMarkdown = marked.parse(children);
    return React.createElement(Text, null, parsedMarkdown);
}
