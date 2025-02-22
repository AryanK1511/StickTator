"use client";

import React, { useState, useEffect, FC } from "react";
import { Monitor } from "lucide-react";
import { MachineCard } from "@/components";
import type { User, Machine, WebSocketMessage } from "@/lib";

export const Machines: FC<{ user: User }> = ({ user }) => {
    const [machines, setMachines] = useState<Machine[]>([]);
    const [error, setError] = useState<string>("");
    const [ws, setWs] = useState<WebSocket | null>(null);

    useEffect(() => {
        const connectWebSocket = () => {
            const userId = user?.email?.split("@")[0] || "";
            const socket = new WebSocket(
                `ws://${process.env.NEXT_PUBLIC_BACKEND_URL}/ws/v1/frontend/${userId}`
            );

            socket.onopen = () => {
                console.log("WebSocket connected");
                setError("");

                socket.send(
                    JSON.stringify({
                        type: "get_machines",
                        email: user.email,
                    })
                );
            };

            socket.onmessage = (event) => {
                try {
                    const data: WebSocketMessage = JSON.parse(event.data);
                    console.log("Received WebSocket message:", data);

                    switch (data.type) {
                        case "device_connected": {
                            // @ts-expect-error: data is not a Machine[]
                            const connectedMachine = data.data as Machine;
                            // @ts-expect-error: data is not a Machine[]
                            setMachines(connectedMachine);
                            break;
                        }

                        case "device_disconnected": {
                            // @ts-expect-error: data is not a Machine[]
                            const connectedMachine = data.data as Machine;
                            // @ts-expect-error: data is not a Machine[]
                            setMachines(connectedMachine);
                            break;
                        }

                        case "machines_list": {
                            const machineData = data.data as Machine[];
                            setMachines(machineData);
                            break;
                        }

                        case "error":
                            setError(data.message || "An error occurred");
                            break;

                        default:
                            console.warn("Unknown message type:", data.type);
                    }
                } catch (err) {
                    console.error("Error parsing WebSocket message:", err);
                    setError("Error processing server message");
                }
            };

            socket.onclose = (event) => {
                console.log("WebSocket disconnected:", event);
                setError("Connection lost. Reconnecting...");
                setTimeout(connectWebSocket, 5000);
            };

            socket.onerror = (event) => {
                console.error("WebSocket error:", event);
                setError("WebSocket connection error");
            };

            setWs(socket);
        };

        if (user?.email) {
            connectWebSocket();
        }

        return () => {
            if (ws) {
                ws.close();
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user?.email]);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-white text-3xl font-bold">Connected Machines</h1>
            </div>

            {error && (
                <div className="bg-red-900/50 border border-red-500 text-red-200 p-4 rounded-lg">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {machines.length > 0 ? (
                    machines.map((machine) => (
                        <div key={machine.id}>
                            <MachineCard machine={machine} />
                        </div>
                    ))
                ) : (
                    <div
                        key="empty-state"
                        className="col-span-full text-center py-12 bg-gray-800/50 rounded-lg border border-gray-700"
                    >
                        <Monitor className="mx-auto text-gray-600 mb-3" size={48} />
                        <p className="text-gray-400">No machines connected</p>
                        <p className="text-gray-500 text-sm mt-2">
                            Plug in the StickTator USB device to get started
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Machines;
