"use client";

import { FC } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Home, Album, LogOut } from "lucide-react";
import { default as NextImage } from "next/image";
import { signOut } from "next-auth/react";
import { Avatar } from "@/components";
import type { User } from "@/lib";

export const Sidebar: FC<{ user: User }> = ({ user }) => {
    const pathname = usePathname();

    return (
        <div className="fixed left-0 top-0 bottom-0 w-[80px] bg-black flex flex-col items-center py-6 gap-8">
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="w-10 h-10 bg-custom-purple rounded-xl"
            />

            <nav className="flex-1 flex flex-col items-center gap-4">
                <Link href="/dashboard" passHref>
                    <motion.div
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        className={`w-10 h-10 flex items-center justify-center ${pathname === "/dashboard" ? "text-white" : "text-gray-500"} hover:text-white`}
                    >
                        <Home className="w-5 h-5" />
                    </motion.div>
                </Link>
                <Link href="/history" passHref>
                    <motion.div
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        className={`w-10 h-10 flex items-center justify-center ${pathname === "/history" ? "text-white" : "text-gray-500"} hover:text-white`}
                    >
                        <Album className="w-5 h-5" />
                    </motion.div>
                </Link>
            </nav>

            <div className="flex flex-col items-center gap-4">
                <motion.div whileHover={{ scale: 1.1 }} className="relative">
                    <Avatar className="w-10 h-10 border-2 border-custom-purple">
                        <NextImage
                            alt="Profile Picture"
                            src={user.image || "placeholder"}
                            height={100}
                            width={100}
                        />
                    </Avatar>
                </motion.div>
                <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="w-10 h-10 flex items-center justify-center text-gray-500 hover:text-white"
                    onClick={() => signOut({ callbackUrl: "/" })}
                >
                    <LogOut className="w-5 h-5" />
                </motion.button>
            </div>
        </div>
    );
};
