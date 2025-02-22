from typing import Any, Optional

from fastapi import Response
from pydantic import BaseModel, Field


class StandardResponse(BaseModel):
    status: bool = Field(..., description="Indicates success (true) or failure (false)")
    message: Optional[str] = Field(
        None, description="A descriptive message about the response"
    )
    data: Optional[Any] = Field(
        None, description="The payload data for success responses"
    )


def success_response(
    message: Optional[str] = "Success",
    code: int = 200,
    response: Optional[Response] = None,
    data: Optional[Any] = None,
) -> StandardResponse:
    if response:
        response.status_code = code
    return StandardResponse(status=True, message=message, data=data)


def error_response(
    message: Optional[str] = "An error occurred",
    code: int = 500,
    response: Optional[Response] = None,
    data: Optional[Any] = None,
) -> StandardResponse:
    if response:
        response.status_code = code
    return StandardResponse(status=False, message=message, data=data)
