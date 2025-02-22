import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database.mongo import MongoDBHandler
from app.services.WebSocketService import WebSocketService
from app.utils.logger import CustomLogger

router = APIRouter()
db = MongoDBHandler()


@router.websocket("/{machine_id}")
async def machine_websocket_endpoint(websocket: WebSocket, machine_id: str):
    await WebSocketService.connect_machine(websocket, machine_id)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                CustomLogger.create_log(
                    "info", f"Received message from machine: {message}"
                )

                # If a device connects to the websocket, add the device to DB if not there already and then tell the frontend about the device
                if message.get("type") == "device_connected":
                    email = message.get("email")
                    machine_name = message.get("machine_name")
                    result = db.add_machine(email, machine_name)
                    await WebSocketService.broadcast_to_frontends(
                        {"type": "device_connected", "data": result["machines"]}
                    )

                # If a device is disconnected, change the status of the device in the DB and tell the frontend about the disconnection
                elif message.get("type") == "device_disconnected":
                    email = message.get("email")
                    machine_dbid = message.get("machine_dbid")
                    result = db.update_machine_status(
                        email, machine_dbid, "disconnected"
                    )
                    await WebSocketService.broadcast_to_frontends(
                        {
                            "type": "device_disconnected",
                            "data": result["machines"],
                        }
                    )

            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "Invalid JSON format"}
                )

    except WebSocketDisconnect:
        WebSocketService.disconnect_machine(machine_id)
