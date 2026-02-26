declare module 'marked-terminal' {
  import type { MarkedExtension } from 'marked';

  export interface TerminalRendererOptions {
    code?: ((code: string) => string) | string;
    blockquote?: ((quote: string) => string) | string;
    html?: ((html: string) => string) | string;
    heading?: ((text: string) => string) | string;
    firstHeading?: ((text: string) => string) | string;
    hr?: ((hr: string) => string) | string;
    listitem?: ((text: string) => string) | string;
    list?: ((body: string, ordered: boolean) => string) | string;
    table?: ((table: string) => string) | string;
    paragraph?: ((text: string) => string) | string;
    strong?: ((text: string) => string) | string;
    em?: ((text: string) => string) | string;
    codespan?: ((code: string) => string) | string;
    del?: ((text: string) => string) | string;
    link?: ((href: string, title: string, text: string) => string) | string;
    href?: ((href: string) => string) | string;
    text?: ((text: string) => string) | string;
    unescape?: boolean;
    emoji?: boolean;
    width?: number;
    showSectionPrefix?: boolean;
    reflowText?: boolean;
    tab?: number;
    tableOptions?: Record<string, unknown>;
  }

  export function markedTerminal(
    options?: TerminalRendererOptions,
    highlightOptions?: Record<string, unknown>
  ): MarkedExtension;
}
