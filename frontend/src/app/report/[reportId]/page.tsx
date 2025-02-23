"use client";

import { type FC, useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useParams } from "next/navigation";
import { Clock, Server } from "lucide-react";

import { MarkdownRenderer, Sidebar, Loader } from "@/components";
import { ApiHelper } from "@/lib";

interface ReportData {
    machine_name: string;
    created_at: string;
    description: string;
    markdown_report_s3_url: string;
}

interface ApiResponse {
    status: boolean;
    data: ReportData;
}

const Report: FC = () => {
    const { data: session } = useSession();
    const [data, setData] = useState<ReportData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const { reportId } = useParams();

    useEffect(() => {
        const api = new ApiHelper();
        const fetchData = async () => {
            const response = await api.get<ApiResponse>(
                `report/reports/aryankhurana2324/${reportId}`
            );
            if (response.status) {
                // @ts-expect-error: data is present in response
                setData(response.data);
            }
            setLoading(false);
        };

        fetchData();
    }, [reportId]);

    if (loading || !session?.user) {
        return <Loader />;
    }

    return (
        <div className="flex min-h-screen">
            <Sidebar user={session.user} />
            <main className="flex-1 p-6 ml-[90px]">
                <div className="max-w-4xl mx-auto space-y-8">
                    <section className="bg-dark dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-all duration-300 hover:shadow-xl">
                        <h1 className="text-4xl mb-6 bg-gradient-to-r from-custom-purple via-custom-pink to-custom-yellow  bg-clip-text text-transparent">
                            {data?.machine_name} Report
                        </h1>
                        <div className="flex items-center text-gray-600 dark:text-gray-400 mb-4">
                            <Clock className="w-4 h-4 mr-2" />
                            <time dateTime={data?.created_at}>
                                {data && new Date(data.created_at).toLocaleString()}
                            </time>
                        </div>
                        <p className="text-lg text-gray-400 dark:text-gray-300">
                            {data?.description}
                        </p>
                    </section>

                    <section className="bg-dark dark:bg-gray-800 rounded-lg shadow-lg p-6">
                        <h2 className="text-2xl font-semibold text-gray-400 dark:text-gray-100 mb-4 flex items-center">
                            <Server className="w-6 h-6 mr-2" />
                            Detailed Report
                        </h2>
                        <div className="prose dark:prose-invert max-w-none">
                            {data && <MarkdownRenderer url={data.markdown_report_s3_url} />}
                        </div>
                    </section>
                </div>
            </main>
        </div>
    );
};

export default Report;
