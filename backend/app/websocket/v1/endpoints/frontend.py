import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database.mongo import MongoDBHandler
from app.services.WebSocketService import WebSocketService
from app.utils.logger import CustomLogger

router = APIRouter()
db = MongoDBHandler()


@router.websocket("/{client_id}")
async def frontend_websocket_endpoint(websocket: WebSocket, client_id: str):
    await WebSocketService.connect_frontend(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                CustomLogger.create_log(
                    "info", f"Received message from frontend: {message}"
                )

                # If the frontend requests for machines, send the list of machines
                if message.get("type") == "get_machines":
                    email = message.get("email")
                    machines = db.get_machines(email)
                    await websocket.send_json(
                        {"type": "machines_list", "data": machines}
                    )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "Invalid JSON format"}
                )

    except WebSocketDisconnect:
        WebSocketService.disconnect_frontend(client_id)
