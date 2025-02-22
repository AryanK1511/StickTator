import type { Config } from "tailwindcss";
import tailwindcssAnimate from "tailwindcss-animate";

const config: Config = {
    darkMode: ["class"],
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "var(--background)",
                foreground: "var(--foreground)",
                dark: "#070314",
                "custom-yellow": "#FFC746",
                "custom-purple": "#9747FF",
                "custom-pink": "#FF7B91",
                "color-1": "hsl(var(--color-1))",
                "color-2": "hsl(var(--color-2))",
                "color-3": "hsl(var(--color-3))",
                "color-4": "hsl(var(--color-4))",
                "color-5": "hsl(var(--color-5))",
            },
            borderRadius: {
                lg: "var(--radius)",
                md: "calc(var(--radius) - 2px)",
                sm: "calc(var(--radius) - 4px)",
            },
            animation: {
                gradient: "gradient 8s linear infinite",
                shine: "shine var(--duration) infinite linear",
                rainbow: "rainbow var(--speed, 4s) infinite linear",
            },
            keyframes: {
                gradient: {
                    to: {
                        backgroundPosition: "var(--bg-size) 0",
                    },
                },
                shine: {
                    "0%": {
                        "background-position": "0% 0%",
                    },
                    "50%": {
                        "background-position": "100% 100%",
                    },
                    to: {
                        "background-position": "0% 0%",
                    },
                },
                rainbow: {
                    "0%": {
                        "background-position": "0%",
                    },
                    "100%": {
                        "background-position": "300%",
                    },
                },
            },
        },
    },
    plugins: [tailwindcssAnimate],
};
export default config;
