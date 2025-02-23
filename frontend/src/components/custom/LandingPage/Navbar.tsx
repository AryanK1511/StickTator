import { FC } from "react";
import { LPButton } from "@/components";

export const Navbar: FC = () => {
    return (
        <nav className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-2">
                <span className="text-white font-medium">StickTator</span>
            </div>

            <div className="flex items-center gap-8">
                <LPButton text="DoraHacks" />
            </div>
        </nav>
    );
};
