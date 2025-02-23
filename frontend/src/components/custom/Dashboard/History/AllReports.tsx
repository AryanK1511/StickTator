import { formatDistanceToNow } from "date-fns";
import { FileText, Server } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { FC } from "react";

interface Report {
    _id: string;
    machine_name: string;
    created_at: string;
    description: string;
}

interface ReportCardProps {
    report: Report;
}

export function ReportCard({ report }: ReportCardProps) {
    const formattedDate = formatDistanceToNow(new Date(report.created_at), { addSuffix: true });

    return (
        <Card className="w-full max-w-md overflow-hidden transition-all duration-300 hover:shadow-lg">
            <CardHeader className="bg-gradient-to-r from-custom-purple to-custom-pink text-white">
                <CardTitle className="flex items-center gap-2 text-lg font-semibold">
                    <Server className="h-5 w-5" />
                    {report.machine_name}
                </CardTitle>
            </CardHeader>
            <CardContent className="p-6 bg-dark text-gray-300">
                <div className="mb-4 flex items-center text-sm text-muted-foreground">
                    <FileText className="mr-2 h-4 w-4" />
                    Created {formattedDate}
                </div>
                <p className="text-sm text-gray-600 line-clamp-3">{report.description}</p>
            </CardContent>
            <CardFooter className="bg-dark p-4">
                <Link href={`/report/${report._id}`} passHref>
                    <Button className="w-full bg-gradient-to-r from-custom-purple to-custom-pink text-white transition-all duration-300 hover:from-purple-600 hover:to-indigo-700">
                        See More
                    </Button>
                </Link>
            </CardFooter>
        </Card>
    );
}

export const AllReports: FC<{ reports: Report[] }> = ({ reports }) => {
    return (
        <div className="container mx-auto">
            <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                {reports.map((report) => (
                    <ReportCard key={report._id} report={report} />
                ))}
            </div>
        </div>
    );
};
