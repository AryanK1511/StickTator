"use client";

import { FC } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { TextDisplayProps } from "@/lib";

export const TextDisplay: FC<TextDisplayProps> = ({ transcript, isListening }) => {
    const words = transcript.split(" ");

    return (
        <div className="min-h-[200px] bg-gray-50 rounded-lg p-6 shadow-sm">
            <AnimatePresence>
                {words.map((word, index) => (
                    <motion.span
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                        className="inline-block mr-2 text-gray-800 text-lg"
                    >
                        {word}
                    </motion.span>
                ))}
            </AnimatePresence>
            {isListening && (
                <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY }}
                    className="inline-block w-2 h-5 bg-gray-400 ml-1"
                />
            )}
        </div>
    );
};
