/* eslint-disable */
// @ts-nocheck

"use client";

import { type FC, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";

export const MarkdownRenderer: FC<{ url: string }> = ({ url }) => {
    const [content, setContent] = useState<string>("");

    useEffect(() => {
        async function fetchMarkdown() {
            try {
                const response = await fetch(url);
                const text = await response.text();
                setContent(text);
            } catch (error) {
                console.error("Error fetching markdown content:", error);
                setContent("Error loading markdown content.");
            }
        }

        fetchMarkdown();
    }, [url]);

    return (
        <div className="prose prose-invert max-w-none">
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw, rehypeHighlight]}
                components={{
                    h1: ({ node, ...props }) => (
                        <h1 className="text-3xl font-bold my-6 text-gray-100" {...props} />
                    ),
                    h2: ({ node, ...props }) => (
                        <h2 className="text-2xl font-semibold my-5 text-gray-200" {...props} />
                    ),
                    h3: ({ node, ...props }) => (
                        <h3 className="text-xl font-semibold my-4 text-gray-300" {...props} />
                    ),
                    p: ({ node, ...props }) => <p className="my-3 text-gray-300" {...props} />,
                    ul: ({ node, ...props }) => (
                        <ul className="list-disc list-inside my-3 text-gray-300" {...props} />
                    ),
                    ol: ({ node, ...props }) => (
                        <ol className="list-decimal list-inside my-3 text-gray-300" {...props} />
                    ),
                    li: ({ node, ...props }) => <li className="my-1 text-gray-300" {...props} />,
                    a: ({ node, ...props }) => (
                        <a
                            className="text-blue-400 hover:text-blue-300 hover:underline"
                            {...props}
                        />
                    ),
                    blockquote: ({ node, ...props }) => (
                        <blockquote
                            className="border-l-4 border-gray-600 pl-4 italic my-3 text-gray-400"
                            {...props}
                        />
                    ),
                    code: ({ node, inline, ...props }) =>
                        inline ? (
                            <code className="bg-gray-800 text-gray-200 rounded px-1" {...props} />
                        ) : (
                            <code
                                className="block bg-gray-900 text-gray-200 rounded p-3 my-3 overflow-x-auto"
                                {...props}
                            />
                        ),
                    pre: ({ node, ...props }) => (
                        <pre className="bg-gray-900 rounded p-3 my-3 overflow-x-auto" {...props} />
                    ),
                    img: ({ node, ...props }) => (
                        <img className="rounded-lg shadow-md my-4" {...props} />
                    ),
                    table: ({ node, ...props }) => (
                        <div className="overflow-x-auto my-4">
                            <table className="min-w-full divide-y divide-gray-700" {...props} />
                        </div>
                    ),
                    th: ({ node, ...props }) => (
                        <th
                            className="px-6 py-3 bg-gray-800 text-left text-xs font-medium text-gray-300 uppercase tracking-wider"
                            {...props}
                        />
                    ),
                    td: ({ node, ...props }) => (
                        <td
                            className="px-6 py-4 whitespace-nowrap text-sm text-gray-300"
                            {...props}
                        />
                    ),
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
};
