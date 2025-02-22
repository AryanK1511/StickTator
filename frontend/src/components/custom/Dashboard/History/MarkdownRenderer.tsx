"use client";

import { FC } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";

type MarkdownRendererProps = {
    markdown: string;
};

export const MarkdownRenderer: FC<MarkdownRendererProps> = ({ markdown }) => {
    return (
        <div className="markdown-content prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto">
            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>{markdown}</ReactMarkdown>
        </div>
    );
};
