import { FC } from "react";
import { Button } from "@/components";

export const LPButton: FC<{ text: string }> = ({ text }) => {
    return (
        <Button className="bg-gradient-to-r border-2 text-white hover:opacity-90 transition-opacity">
            {text}
        </Button>
    );
};
