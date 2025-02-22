"use client";

import { motion } from "framer-motion";
import { FC } from "react";

export const ProcessingIndicator: FC = () => {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-80"
        >
            <motion.div
                animate={{
                    scale: [1, 1.2, 1],
                    rotate: [0, 180, 360],
                }}
                transition={{
                    duration: 2,
                    repeat: Number.POSITIVE_INFINITY,
                    ease: "easeInOut",
                }}
                className="w-12 h-12 border-4 border-gray-300 border-t-gray-600 rounded-full"
            />
        </motion.div>
    );
};
