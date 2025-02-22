from fastapi import APIRouter, Response
from fastapi import Request as ServerRequest

from app.services.AIService import AIService
from app.utils.logger import CustomLogger
from app.utils.response import error_response, success_response

router = APIRouter()


@router.get("/get-commands")
async def get_commands(req: ServerRequest, res: Response):
    try:
        data = await req.json()
        user_intent = data.get("user_intent")

        if not user_intent:
            return error_response("User intent is required", 400, res)

        service = AIService()
        operation = service.generate_commands(user_intent)
        CustomLogger.create_log("info", f"Commands generated successfully: {operation}")
        return success_response("Commands generated successfully", 200, res, operation)
    except ValueError as e:
        CustomLogger.create_log("error", f"Error generating commands: {str(e)}")
        return error_response(str(e), 400, res)
    except Exception as e:
        CustomLogger.create_log("error", f"Error creating user: {str(e)}")
        raise e
