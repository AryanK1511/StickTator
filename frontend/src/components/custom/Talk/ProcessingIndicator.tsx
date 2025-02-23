"use client";

import { motion } from "framer-motion";
import { type FC, useState, useEffect } from "react";
import { Loader2 } from "lucide-react";

export const ProcessingIndicator: FC = () => {
    const [message, setMessage] = useState("Processing your request. This may take a while...");

    useEffect(() => {
        const messages = [
            "Processing your request. This may take a while...",
            "Go get coffee while Stickatator handles this operation for you!",
        ];
        let index = 0;

        const intervalId = setInterval(() => {
            index = (index + 1) % messages.length;
            setMessage(messages[index]);
        }, 5000);

        return () => clearInterval(intervalId);
    }, []);

    return (
        <div className="fixed inset-0 flex flex-col items-center justify-center bg-dark text-white">
            <motion.div
                animate={{
                    rotate: 360,
                }}
                transition={{
                    duration: 2,
                    repeat: Number.POSITIVE_INFINITY,
                    ease: "linear",
                }}
                className="mb-8"
            >
                <Loader2 className="w-24 h-24 text-white" />
            </motion.div>
            <h2 className="text-3xl font-bold mb-4">Stickatator</h2>
            <p className="text-xl text-center max-w-md px-4">{message}</p>
        </div>
    );
};
