import { NextAuthOptions } from "next-auth";
import Google from "next-auth/providers/google";
import { ApiHelper } from "@/lib";

const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || "";
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET || "";

export const authOptions: NextAuthOptions = {
    session: {
        strategy: "jwt",
    },
    secret: process.env.NEXTAUTH_SECRET,
    providers: [
        Google({
            clientId: GOOGLE_CLIENT_ID,
            clientSecret: GOOGLE_CLIENT_SECRET,
            authorization: {
                params: {
                    prompt: "select_account",
                },
            },
        }),
    ],
    callbacks: {
        async signIn({ profile }) {
            if (!profile || !profile.email) {
                return false;
            }
            try {
                const api = new ApiHelper();
                const response = await api.post("users/add", {
                    name: profile.name,
                    email: profile.email,
                    // @ts-expect-error: Property 'picture' does not exist on type 'Profile'.
                    image: profile.picture,
                });
                console.log(response);
                if (!response.status) {
                    return false;
                }
                return true;
            } catch (error) {
                console.error("Error signing in:", error);
                return false;
            }
        },
        async redirect({ baseUrl }) {
            return `${baseUrl}/dashboard`;
        },
    },
};
