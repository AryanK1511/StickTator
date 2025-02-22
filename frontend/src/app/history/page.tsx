"use client";

import { FC } from "react";
import { useSession } from "next-auth/react";
import { Sidebar, Loader } from "@/components";

const History: FC = () => {
    const { data: session } = useSession();

    return (
        <div>
            {!session?.user ? (
                <Loader />
            ) : (
                <div>
                    <Sidebar user={session?.user} />
                </div>
            )}
        </div>
    );
};

export default History;
