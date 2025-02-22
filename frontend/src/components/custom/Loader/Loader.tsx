"use client";

import { FC } from "react";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

export const Loader: FC = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-background text-white">
            <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
            >
                <Loader2 className="w-12 h-12 text-primary" />
            </motion.div>
            <motion.h1
                className="mt-4 text-2xl font-semibold text-foreground"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
            >
                Loading...
            </motion.h1>
        </div>
    );
};
