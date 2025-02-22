import os
import uuid
from typing import Dict, List

import boto3
from dotenv import load_dotenv

load_dotenv()


class S3Handler:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION"),
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME")

    def upload_report(self, user_email: str, markdown_content: str) -> Dict[str, str]:
        try:
            report_id = str(uuid.uuid4())
            key = f"{user_email}/{report_id}.md"

            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=markdown_content.encode("utf-8"),
                ContentType="text/markdown",
            )

            url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"

            return {"report_id": report_id, "url": url}

        except Exception as e:
            print(f"Error uploading report: {str(e)}")
            raise

    def get_report(self, user_email: str, report_id: str) -> str:
        try:
            key = f"{user_email}/{report_id}.md"

            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)

            return response["Body"].read().decode("utf-8")

        except Exception as e:
            print(f"Error fetching report: {str(e)}")
            raise

    def get_all_reports(self, user_email: str) -> List[Dict[str, str]]:
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name, Prefix=f"{user_email}/"
            )

            if "Contents" not in response:
                return []

            reports = []
            for item in response["Contents"]:
                report_id = item["Key"].split("/")[1].replace(".md", "")
                reports.append(
                    {
                        "report_id": report_id,
                        "url": f"https://{self.bucket_name}.s3.amazonaws.com/{item['Key']}",
                        "last_modified": item["LastModified"].isoformat(),
                    }
                )

            reports.sort(key=lambda x: x["last_modified"], reverse=True)
            return reports

        except Exception as e:
            print(f"Error fetching all reports: {str(e)}")
            raise

    def delete_report(self, user_email: str, report_id: str) -> None:
        try:
            key = f"{user_email}/{report_id}.md"

            self.s3.delete_object(Bucket=self.bucket_name, Key=key)

        except Exception as e:
            print(f"Error deleting report: {str(e)}")
            raise
