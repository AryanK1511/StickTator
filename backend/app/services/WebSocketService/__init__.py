from typing import Dict

from fastapi import WebSocket

from app.utils.logger import CustomLogger


class WebSocketService:
    _machine_connections: Dict[str, WebSocket] = {}
    _frontend_connections: Dict[str, WebSocket] = {}

    @staticmethod
    async def connect_machine(websocket: WebSocket, machine_id: str):
        await websocket.accept()
        WebSocketService._machine_connections[machine_id] = websocket
        CustomLogger.create_log("info", f"Machine connected: {machine_id}")
        CustomLogger.create_log(
            "debug", f"Machine connections: {WebSocketService._machine_connections}"
        )
        CustomLogger.create_log(
            "debug", f"Frontend connections: {WebSocketService._frontend_connections}"
        )

    @staticmethod
    async def connect_frontend(websocket: WebSocket, client_id: str):
        await websocket.accept()
        WebSocketService._frontend_connections[client_id] = websocket
        CustomLogger.create_log("info", f"Frontend client connected: {client_id}")
        CustomLogger.create_log(
            "debug", f"Machine connections: {WebSocketService._machine_connections}"
        )
        CustomLogger.create_log(
            "debug", f"Frontend connections: {WebSocketService._frontend_connections}"
        )

    @staticmethod
    def disconnect_machine(machine_id: str):
        if machine_id in WebSocketService._machine_connections:
            del WebSocketService._machine_connections[machine_id]
            CustomLogger.create_log("info", f"Machine disconnected: {machine_id}")
            CustomLogger.create_log(
                "debug", f"Machine connections: {WebSocketService._machine_connections}"
            )
            CustomLogger.create_log(
                "debug",
                f"Frontend connections: {WebSocketService._frontend_connections}",
            )

    @staticmethod
    def disconnect_frontend(client_id: str):
        if client_id in WebSocketService._frontend_connections:
            del WebSocketService._frontend_connections[client_id]
            CustomLogger.create_log(
                "info", f"Frontend client disconnected: {client_id}"
            )
            CustomLogger.create_log(
                "debug", f"Machine connections: {WebSocketService._machine_connections}"
            )
            CustomLogger.create_log(
                "debug",
                f"Frontend connections: {WebSocketService._frontend_connections}",
            )

    @staticmethod
    async def broadcast_to_frontends(message: dict):
        CustomLogger.create_log("debug", f"Broadcasting message: {message}")
        CustomLogger.create_log(
            "debug", f"Frontend connections: {WebSocketService._frontend_connections}"
        )

        disconnected = []
        for client_id, connection in WebSocketService._frontend_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                CustomLogger.create_log(
                    "error", f"Failed to send message to frontend {client_id}: {e}"
                )
                disconnected.append(client_id)

        for client_id in disconnected:
            WebSocketService.disconnect_frontend(client_id)

    @staticmethod
    async def send_to_machine(machine_id: str, message: dict) -> bool:
        if machine_id in WebSocketService._machine_connections:
            try:
                await WebSocketService._machine_connections[machine_id].send_json(
                    message
                )
                return True
            except Exception as e:
                CustomLogger.create_log(
                    "error", f"Failed to send message to machine {machine_id}. {e}"
                )
                WebSocketService.disconnect_machine(machine_id)
                return False
        return False
