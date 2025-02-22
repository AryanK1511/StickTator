from fastapi import APIRouter, Response
from fastapi import Request as ServerRequest

from app.services.UserService import UserService
from app.utils.logger import CustomLogger
from app.utils.response import error_response, success_response

router = APIRouter()


@router.post("/add")
async def add_new_user(req: ServerRequest, res: Response):
    try:
        data = await req.json()
        name = data.get("name")
        email = data.get("email")
        image = data.get("image")

        new_user = UserService.create_user(name, email, image)
        new_user["_id"] = str(new_user["_id"])
        CustomLogger.create_log("info", f"User created: {new_user}")
        return success_response("User created successfully", 201, res, new_user)
    except ValueError as e:
        if str(e).startswith("User with email"):
            CustomLogger.create_log("info", "User already exists, skipping creation")
            return success_response("User already exists, skipping creation")
        CustomLogger.create_log("error", f"Error creating user: {str(e)}")
        return error_response(str(e) or "An Error Occurred", 400, res)
    except Exception as e:
        CustomLogger.create_log("error", f"Error creating user: {str(e)}")
        raise e
