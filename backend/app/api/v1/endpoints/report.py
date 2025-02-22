from fastapi import APIRouter, Response
from fastapi import Request as ServerRequest

from app.database.mongo import MongoDBHandler
from app.database.s3 import S3Handler
from app.services.AIService import AIService
from app.utils.logger import CustomLogger
from app.utils.response import error_response, success_response

router = APIRouter()


@router.post("/generate-report/{user_email}/{machine_name}")
async def generate_report(
    req: ServerRequest, res: Response, user_email: str, machine_name: str
):
    try:
        data = await req.json()

        if not data:
            return error_response("Data is required", 400, res)

        if not user_email:
            return error_response("User email is required", 400, res)
        user_email = user_email.lower() + "@gmail.com"

        CustomLogger.create_log(
            "info", f"Generating report for user: {user_email}, machine: {machine_name}"
        )

        ai_service = AIService()
        report_content, description = ai_service.generate_report(data)

        CustomLogger.create_log("info", f"Report generated: {report_content}")

        s3_handler = S3Handler()
        mongo_handler = MongoDBHandler()

        s3_response = s3_handler.upload_report(user_email, report_content)

        CustomLogger.create_log("info", f"Report uploaded to S3: {s3_response['url']}")

        mongo_handler.add_report(
            email=user_email,
            machine_name=machine_name,
            s3_url=s3_response["url"],
            description=description,
        )

        CustomLogger.create_log(
            "info", f"Report details stored in MongoDB: {s3_response['url']}"
        )

        return success_response(
            "Report generated and stored successfully", 200, res, s3_response
        )
    except ValueError as e:
        CustomLogger.create_log("error", f"Error generating report: {str(e)}")
        return error_response(str(e), 400, res)
    except Exception as e:
        CustomLogger.create_log("error", f"Unexpected Error: {str(e)}")
        raise e
