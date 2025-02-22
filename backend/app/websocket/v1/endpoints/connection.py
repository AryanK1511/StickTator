import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database.mongo import MongoDBHandler
from app.services.WebSocketService import WebSocketService
from app.utils.logger import CustomLogger

manager = WebSocketService()
router = APIRouter()


@router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    db = MongoDBHandler()

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                CustomLogger.create_log("info", f"Received message: {message}")

                if message.get("type") == "device_connected":
                    email = message.get("email")
                    machine_name = message.get("machine_name")

                    result = db.add_machine(email, machine_name)

                    response = {"type": "device_connected", "data": result["machines"]}

                    await manager.broadcast(json.dumps(response.data))

                elif message.get("type") == "get_machines":
                    email = message.get("email")
                    machines = db.get_machines(email)

                    response = {"type": "machines_list", "data": machines}

                    await websocket.send_json(response)

            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "Invalid JSON format"}
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
