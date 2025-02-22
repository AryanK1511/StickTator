import { FC } from "react";
import { ChevronRight } from "lucide-react";
import { Navbar, AnimatedGradientText, GoogleSignInButton } from "@/components";
import { cn } from "@/lib";

export const LandingPage: FC = () => {
    return (
        <div className="min-h-screen">
            <Navbar />
            <main className="max-w-6xl mx-auto px-6 pt-24 pb-16 text-center">
                <AnimatedGradientText className="bg-white/10 px-4 py-1.5 text-sm text-white/80 mb-8">
                    🎉 <hr className="mx-2 h-4 w-px shrink-0 bg-gray-300" />{" "}
                    <span
                        className={cn(
                            `inline animate-gradient bg-gradient-to-r from-custom-yellow via-custom-purple to-custom-yellow bg-[length:var(--bg-size)_100%] bg-clip-text text-transparent`
                        )}
                    >
                        Introducing StickTator
                    </span>
                    <ChevronRight className="ml-1 size-3 transition-transform duration-300 ease-in-out group-hover:translate-x-0.5" />
                </AnimatedGradientText>

                <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6">
                    <span className="text-white">Control Any Device with</span>
                    <br />
                    <span className="inline-block mt-2">
                        <span className="bg-gradient-to-r from-custom-purple via-custom-pink to-custom-yellow bg-clip-text text-transparent">
                            Just Your Voice
                        </span>
                    </span>
                </h1>

                <p className="text-gray-400 text-xl mb-12">
                    Transform any computer into an AI-powered assistant with a single USB stick
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-md mx-auto">
                    <GoogleSignInButton />
                </div>
            </main>
        </div>
    );
};
