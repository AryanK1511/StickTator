"use client";

import { FC, useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { Sidebar, Loader, AllReports } from "@/components";
import { ApiHelper } from "@/lib";

interface ReportData {
    _id: string;
    markdown_report_s3_url: string;
    machine_name: string;
    created_at: string;
    description: string;
}

interface ApiResponse {
    status: boolean;
    message: string;
    data: ReportData;
}

const History: FC = () => {
    const { data: session } = useSession();

    const api = new ApiHelper();

    const [data, setData] = useState<ReportData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchData = async () => {
            const response = await api.get<ApiResponse>("report/reports/aryankhurana2324");
            if (response.status) {
                // @ts-expect-error: data is not null
                setData(response.data);
            }
            setLoading(false);
        };

        fetchData();
    }, [session]);

    if (loading) {
        return <Loader />;
    }

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
                                <span className="bg-gradient-to-r from-custom-purple via-custom-pink to-custom-yellow  bg-clip-text text-transparent">
                                    Reports History
                                </span>
                            </h1>
                            <p className="text-white">
                                Welcome to your reports history. Here you can see all the reports
                                for the commands that you have ran on your devices.
                            </p>
                        </div>
                        {/* @ts-expect-error: data is not null */}
                        <AllReports reports={data} />
                    </div>
                </div>
            )}
        </div>
    );
};

export default History;
