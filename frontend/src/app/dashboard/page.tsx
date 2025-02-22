"use client";

import { FC } from "react";
import { useSession } from "next-auth/react";
import { Sidebar, Loader, Machines, Statistics } from "@/components";

const Dashboard: FC = () => {
    const { data: session } = useSession();

    return (
        <div>
            {!session?.user ? (
                <Loader />
            ) : (
                <div>
                    <Sidebar user={session?.user} />
                    <div className="flex-1 p-6 ml-[90px] mt-8">
                        <div className="flex flex-col items-left mb-8">
                            <h1 className="text-6xl font-bold text-white mb-6">
                                Hello{" "}
                                <span className="bg-gradient-to-r from-custom-purple via-custom-pink to-custom-yellow  bg-clip-text text-transparent">
                                    Aryan
                                </span>
                            </h1>
                            <p className="text-white">
                                Lorem ipsum dolor sit amet, consectetur adipisicing elit. Voluptatum
                                minus temporibus quam?
                            </p>
                        </div>
                        <Statistics />
                        <Machines user={session?.user} />
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
