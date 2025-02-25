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
    MessageDisplay,
} from "@/components";
import { ApiHelper } from "@/lib";

const VoiceInterface: FC = () => {
    const { data: session } = useSession();
    const [isListening, setIsListening] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [interimTranscript, setInterimTranscript] = useState("");
    const [finalTranscript, setFinalTranscript] = useState("");
    const [showControls, setShowControls] = useState(false);
    const [messages, setMessages] = useState<string[]>([]);
    const [showLogs, setShowLogs] = useState(false);
    const [isCreatingReport, setIsCreatingReport] = useState(false);
    const params = useParams();
    const recognitionRef = useRef<any>(null);
    const socketRef = useRef<WebSocket | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

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
                setShowControls(true);
            };
        }
    }, []);

    useEffect(() => {
        socketRef.current = new WebSocket(
            `ws://${process.env.NEXT_PUBLIC_BACKEND_URL}/ws/v1/frontend/aryankhurana2324@gmail.com`
        );

        socketRef.current.onmessage = (event) => {
            const message = event.data;
            console.log(message);
            setMessages((prevMessages) => [...prevMessages, message]);
        };

        socketRef.current.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        socketRef.current.onclose = () => {
            console.log("WebSocket connection closed");
        };

        return () => {
            socketRef.current?.close();
        };
    }, []);

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
        } else {
            recognitionRef.current?.start();
            setTranscript("");
            setInterimTranscript("");
            setFinalTranscript("");
            setShowControls(false);
            setShowLogs(false);
            setMessages([]);
        }
        setIsListening(!isListening);
    };

    const reset = () => {
        setTranscript("");
        setInterimTranscript("");
        setFinalTranscript("");
        setShowControls(false);
        setShowLogs(false);
        setMessages([]);
    };

    const send = async () => {
        setIsProcessing(true);
        setShowLogs(true);

        try {
            console.log("Sending message:", finalTranscript || transcript);
            const api = new ApiHelper();
            const response = await api.post("machines/get-commands", {
                user_intent: finalTranscript || transcript,
            });

            console.log(response);

            const machine_execution = await api.post(`machines/send_message/aryankhurana2324`, {
                type: "execute",
                ...response.data,
            });

            console.log(machine_execution);
            console.log(messages);
        } catch (error) {
            console.error("Error sending message:", error);
            setMessages((prev) => [...prev, "Error processing your request"]);
        } finally {
            setIsProcessing(false);
        }
    };

    const createReport = async () => {
        console.log("Creating report with the following logs and output:");
        console.log(messages);
        setIsCreatingReport(true);

        try {
            const api = new ApiHelper();

            // get the first index of messages an convert to json and send it
            const firstMessage = JSON.parse(messages[0]);
            const response = await api.post(
                `report/generate-report/aryankhurana2324/${params.machineName}`,
                firstMessage
            );

            if (response.status) {
                window.location.href = "/history";
            } else {
                console.error("Failed to create report:", response.statusText);
            }
        } catch (error) {
            console.error("Error creating report:", error);
        } finally {
            setIsCreatingReport(false);
        }
    };

    return (
        <div>
            {!session?.user ? (
                <div className="flex justify-center items-center min-h-screen">
                    <h1>Loading...</h1>
                </div>
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
                            Use the mic button to talk to {params.machineName}
                        </motion.p>

                        <div className="w-full max-w-2xl relative">
                            {/* Only show transcript during or after recording */}
                            {(isListening ||
                                (!isListening && !showLogs && (finalTranscript || transcript))) && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-gray-800 p-6 rounded-lg shadow-lg mb-6"
                                >
                                    <h2 className="text-gray-400 mb-2 text-sm">Your message:</h2>
                                    <p className="text-white text-lg">
                                        {isListening
                                            ? transcript + interimTranscript
                                            : finalTranscript || transcript}
                                    </p>
                                </motion.div>
                            )}

                            <VoiceButton
                                isListening={isListening}
                                toggleListening={toggleListening}
                            />

                            <AnimatePresence>
                                {showControls && !showLogs && (
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

                            <AnimatePresence>
                                {isProcessing && <ProcessingIndicator />}
                            </AnimatePresence>

                            <AnimatePresence>
                                {showLogs && (
                                    <div className="bg-gray-800 p-6 rounded-lg shadow-lg mt-6 w-full">
                                        <h2 className="text-gray-400 mb-2 text-sm">
                                            Execution Logs:
                                        </h2>
                                        <div className="text-white text-lg max-h-96 overflow-y-auto">
                                            {messages.map((msg, index) => (
                                                <MessageDisplay message={msg} key={index} />
                                            ))}
                                            <div ref={messagesEndRef} />
                                        </div>
                                        <Button
                                            onClick={createReport}
                                            className="bg-custom-purple hover:bg-custom-purple/50 text-white px-6 py-2 rounded-lg transition-colors duration-200 mt-4"
                                            disabled={isCreatingReport}
                                        >
                                            {isCreatingReport
                                                ? "Creating Report..."
                                                : "Create Report"}
                                        </Button>
                                    </div>
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
