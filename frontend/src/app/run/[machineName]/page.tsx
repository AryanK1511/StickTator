/* eslint-disable */
// @ts-nocheck

"use client";

import { useState, useEffect, useRef, FC } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import {
    VoiceButton,
    TextDisplay,
    ProcessingIndicator,
    Loader,
    Sidebar,
    Button,
} from "@/components";
import { ApiHelper } from "@/lib";

declare global {
    interface Window {
        SpeechRecognition: any;
        webkitSpeechRecognition: any;
    }
}

const RunCommandsInterface: FC = () => {
    const { data: session } = useSession();
    const [isListening, setIsListening] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [interimTranscript, setInterimTranscript] = useState("");
    const [finalTranscript, setFinalTranscript] = useState("");
    const [showButtons, setShowButtons] = useState(false);
    const params = useParams();
    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        if (
            typeof window !== "undefined" &&
            ("SpeechRecognition" in window || "webkitSpeechRecognition" in window)
        ) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = true;
            recognitionRef.current.interimResults = true;

            recognitionRef.current.onresult = (event: any) => {
                let finalTranscript = "";
                let interimTranscript = "";

                for (let i = 0; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                setTranscript(finalTranscript);
                setInterimTranscript(interimTranscript);
            };

            recognitionRef.current.onerror = (event: any) => {
                console.error("Speech recognition error", event.error);
                setIsListening(false);
            };

            recognitionRef.current.onend = () => {
                setIsListening(false);
                setFinalTranscript(transcript);
                setShowButtons(true);
            };
        }
    }, []);

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
        } else {
            recognitionRef.current?.start();
            setTranscript("");
            setInterimTranscript("");
            setFinalTranscript("");
            setShowButtons(false);
        }
        setIsListening(!isListening);
    };

    const reset = () => {
        setTranscript("");
        setInterimTranscript("");
        setFinalTranscript("");
        setShowButtons(false);
    };

    const send = async () => {
        console.log("Sending transcript:", finalTranscript || transcript);
        const api = new ApiHelper();
        const response = await api.post("machines/get-commands", {
            user_intent: finalTranscript || transcript,
        });

        console.log(response);

        // const command_response = await api.post("machines/run-command", {
    };

    const displayText = isListening ? transcript + interimTranscript : "";

    return (
        <div>
            {!session?.user ? (
                <Loader />
            ) : (
                <div className="ml-[90px]">
                    <Sidebar user={session?.user} />
                    <div className="min-h-screen bg-dark flex flex-col items-center justify-center p-6">
                        <motion.h1
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, ease: "easeOut" }}
                            className="text-4xl font-light mb-6 bg-gradient-to-r from-custom-purple via-custom-pink to-custom-yellow bg-clip-text text-transparent"
                        >
                            {params.machineName}
                        </motion.h1>
                        <motion.p
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, ease: "easeOut" }}
                            className="text-xl font-light mb-6 text-gray-500"
                        >
                            Use the mic button at the bottom right to talk to {params.machineName}
                        </motion.p>
                        <div className="w-full max-w-2xl relative">
                            {isListening && (
                                <TextDisplay transcript={displayText} isListening={isListening} />
                            )}

                            {!isListening && (finalTranscript || transcript) && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-gray-800 p-6 rounded-lg shadow-lg mb-6"
                                >
                                    <h2 className="text-gray-400 mb-2 text-sm">
                                        Final Transcript:
                                    </h2>
                                    <p className="text-white text-lg">
                                        {finalTranscript || transcript}
                                    </p>
                                </motion.div>
                            )}

                            <VoiceButton
                                isListening={isListening}
                                toggleListening={toggleListening}
                            />

                            <AnimatePresence>
                                {isProcessing && <ProcessingIndicator />}
                            </AnimatePresence>

                            <AnimatePresence>
                                {showButtons && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: 20 }}
                                        className="flex justify-center mt-4 space-x-4"
                                    >
                                        <Button
                                            onClick={reset}
                                            className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg transition-colors duration-200"
                                        >
                                            Reset
                                        </Button>
                                        <Button
                                            onClick={send}
                                            className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg transition-colors duration-200"
                                        >
                                            Send
                                        </Button>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default VoiceInterface;
