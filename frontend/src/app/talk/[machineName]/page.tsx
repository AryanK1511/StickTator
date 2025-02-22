"use client";
import { useState, useEffect, useRef, FC } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSession } from "next-auth/react";
import { VoiceButton, TextDisplay, ProcessingIndicator, Loader, Sidebar } from "@/components";

declare global {
    interface Window {
        SpeechRecognition: any;
        webkitSpeechRecognition: any;
    }
}

const VoiceInterface: FC = () => {
    const { data: session } = useSession();
    const [isListening, setIsListening] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [interimTranscript, setInterimTranscript] = useState("");
    const [showButtons, setShowButtons] = useState(false);
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
            };
        }
    }, []);

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
            setIsProcessing(true);
            setTimeout(() => {
                setIsProcessing(false);
                setShowButtons(true);
            }, 2000); // Simulating processing time
        } else {
            recognitionRef.current?.start();
            setTranscript("");
            setInterimTranscript("");
            setShowButtons(false);
        }
        setIsListening(!isListening);
    };

    const reset = () => {
        setTranscript("");
        setInterimTranscript("");
        setShowButtons(false);
    };

    const send = () => {
        // Implement the send functionality here
        console.log("Sending transcript:", transcript);
        setShowButtons(false);
    };

    const displayText = transcript + (isListening ? interimTranscript : "");

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
                            className="text-4xl font-light mb-12 text-gray-800"
                        >
                            voice<span className="font-bold">interface</span>
                        </motion.h1>
                        <div className="w-full max-w-2xl relative">
                            <TextDisplay transcript={displayText} isListening={isListening} />
                            <VoiceButton
                                isListening={isListening}
                                toggleListening={toggleListening}
                            />
                            <AnimatePresence>
                                {isProcessing && <ProcessingIndicator />}
                            </AnimatePresence>
                            {showButtons && (
                                <div className="flex justify-center mt-4">
                                    <button
                                        onClick={reset}
                                        className="bg-red-500 text-white px-4 py-2 rounded mr-2"
                                    >
                                        Reset
                                    </button>
                                    <button
                                        onClick={send}
                                        className="bg-green-500 text-white px-4 py-2 rounded"
                                    >
                                        Send
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default VoiceInterface;
