/* eslint-disable */
// @ts-nocheck

import React from "react";
import { AlertCircle, CheckCircle2, Terminal, Wifi } from "lucide-react";

export const MessageDisplay = ({ message }) => {
    const data = typeof message === "string" ? JSON.parse(message) : message;

    const getMessageStyle = (type) => {
        switch (type) {
            case "device_connected":
                return {
                    icon: <Wifi className="text-green-500" size={20} />,
                    bgColor: "bg-green-500/10",
                    borderColor: "border-green-500/20",
                };
            case "command_error":
                return {
                    icon: <AlertCircle className="text-red-500" size={20} />,
                    bgColor: "bg-red-500/10",
                    borderColor: "border-red-500/20",
                };
            case "command_output":
                return {
                    icon: <CheckCircle2 className="text-blue-500" size={20} />,
                    bgColor: "bg-blue-500/10",
                    borderColor: "border-blue-500/20",
                };
            default:
                return {
                    icon: <Terminal className="text-gray-500" size={20} />,
                    bgColor: "bg-gray-500/10",
                    borderColor: "border-gray-500/20",
                };
        }
    };

    const style = getMessageStyle(data.type);

    const renderContent = () => {
        switch (data.type) {
            case "device_connected":
                return (
                    <div className="space-y-1">
                        <p className="font-medium text-white">Device Connected</p>
                        <div className="text-gray-400 text-sm">
                            <p>Name: {data.data[0].name}</p>
                            <p>Status: {data.data[0].status}</p>
                            <p>
                                Connected at: {new Date(data.data[0].created_at).toLocaleString()}
                            </p>
                        </div>
                    </div>
                );

            case "command_error":
            case "command_complete":
                return (
                    <div className="space-y-1">
                        <p className="font-medium text-white">
                            {data.type === "command_error" ? "Command Error" : "Command Output"}
                        </p>
                        <div className="text-gray-400 text-sm">
                            <p>
                                Command:{" "}
                                <code className="bg-gray-700 px-2 py-0.5 rounded">
                                    {data.command}
                                </code>
                            </p>
                            <p className="mt-1">
                                {data.type === "command_error" ? "Error: " : "Output: "}
                                <span
                                    className={
                                        data.type === "command_error"
                                            ? "text-red-400"
                                            : "text-green-400"
                                    }
                                >
                                    {data.error || data.output}
                                </span>
                            </p>
                        </div>
                    </div>
                );

            default:
                return <pre className="text-gray-400 text-sm">{JSON.stringify(data, null, 2)}</pre>;
        }
    };

    return (
        <div className={`p-4 rounded-lg border ${style.bgColor} ${style.borderColor} mb-2`}>
            <div className="flex items-start gap-3">
                {style.icon}
                {renderContent()}
            </div>
        </div>
    );
};
