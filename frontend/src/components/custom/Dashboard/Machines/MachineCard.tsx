"use client";

import { FC, useState, useEffect } from "react";
import { Mic, Power, Cpu } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components";
import type { Machine } from "@/lib";

export const MachineCard: FC<{ machine: Machine }> = ({ machine }) => {
    const [isConnected, setIsConnected] = useState(machine.status === "connected");

    useEffect(() => {
        setIsConnected(machine.status === "connected");
    }, [machine.status]);

    console.log(machine);

    return (
        <div className="relative w-full max-w-sm h-64 rounded-2xl overflow-hidden transition-all duration-500 ease-out transform hover:scale-105">
            <div className="absolute inset-0 bg-gradient-to-r from-custom-purple via-custom-pink to-custom-yellow animate-gradient-xy opacity-75"></div>

            <div className="absolute inset-[2px] bg-dark rounded-2xl z-10"></div>

            <div className="relative h-full p-6 flex flex-col justify-between z-20">
                <div>
                    <div className="flex items-center justify-between mb-1">
                        <h3 className="text-2xl font-bold text-white">{machine.name}</h3>
                        <div
                            className={`w-3 h-3 rounded-full ${isConnected ? "bg-green-400" : "bg-red-400"} animate-pulse`}
                        ></div>
                    </div>
                    <div className="flex items-center text-gray-200 text-sm">
                        <Cpu className="w-4 h-4 mr-1" />
                        <span
                            className={`ml-1 font-semibold ${isConnected ? "text-green-400" : "text-red-400"}`}
                        >
                            {isConnected ? "Connected" : "Disconnected"}
                        </span>
                    </div>
                </div>

                <div className="flex justify-between items-center">
                    <Button
                        variant="ghost"
                        size="icon"
                        className="w-12 h-12 rounded-full bg-white/10 text-white"
                        disabled
                    >
                        <Power
                            className={`w-6 h-6 ${isConnected ? "text-green-400" : "text-red-400"}`}
                        />
                    </Button>
                    <Link href={isConnected ? `/talk/${machine.name}` : "#"}>
                        <Button
                            variant="ghost"
                            className="flex items-center px-4 py-2 rounded-full bg-custom-purple/70 hover:bg-custom-purple/50 hover:text-white duration-200 text-white"
                            onClick={(e) => {
                                if (!isConnected) {
                                    e.preventDefault();
                                    console.log(
                                        `Cannot interact with ${machine.name} as it is disconnected`
                                    );
                                } else {
                                    console.log(`Interacting with ${machine.name}`);
                                }
                            }}
                            disabled={!isConnected}
                        >
                            <Mic className="w-4 h-4 mr-2" />
                            <span className="font-medium">Talk</span>
                        </Button>
                    </Link>
                </div>
            </div>
        </div>
    );
};
