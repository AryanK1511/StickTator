"use client";

import { FC } from "react";
import { motion } from "framer-motion";
import { Mic } from "lucide-react";
import type { VoiceButtonProps } from "@/lib";

export const VoiceButton: FC<VoiceButtonProps> = ({ isListening, toggleListening }) => {
    return (
        <motion.button
            onClick={toggleListening}
            className={`fixed bottom-8 right-8 w-16 h-16 rounded-full flex items-center justify-center ${
                isListening ? "bg-red-500" : "bg-gray-200"
            } shadow-lg transition-colors duration-300`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
        >
            <Mic className={`w-6 h-6 ${isListening ? "text-white" : "text-gray-600"}`} />
            {isListening && (
                <motion.div
                    className="absolute w-full h-full rounded-full border-2 border-red-300"
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.7, 0, 0.7],
                    }}
                    transition={{
                        duration: 1.5,
                        repeat: Number.POSITIVE_INFINITY,
                        ease: "easeInOut",
                    }}
                />
            )}
        </motion.button>
    );
};
