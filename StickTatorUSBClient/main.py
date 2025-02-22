import asyncio
import json
import os
import platform
import ssl
from pathlib import Path

import websockets
from dotenv import load_dotenv

load_dotenv()


class WSClient:
    def __init__(self):
        self.server_url = (
            f'ws://{os.getenv("SERVER_URL", "127.0.0.1:8000")}/ws/v1/connection'
        )
        self.owner_email = self._read_owner_file()
        self.client_id = self.owner_email.split("@")[0] if self.owner_email else None
        self.computer_name = platform.node()
        self.max_retries = 5
        self.retry_delay = 5

    def _read_owner_file(self):
        try:
            return Path("owner.txt").read_text().strip()
        except FileNotFoundError:
            print("Error: owner.txt not found")
            return None
        except Exception as e:
            print(f"Error reading owner.txt: {e}")
            return None

    async def handle_message(self, websocket, message: str):
        try:
            data = json.loads(message)
            if data.get("type") == "ping":
                await websocket.send(
                    json.dumps(
                        {
                            "type": "pong",
                            "client_id": self.client_id,
                            "computer_name": self.computer_name,
                        }
                    )
                )
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON received: {message}")
        except Exception as e:
            print(f"Error handling message: {e}")

    async def connect(self):
        if not self.client_id:
            print("Error: No client ID available")
            return False

        websocket_url = f"{self.server_url}/{self.client_id}"
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE  # Only for development/testing

        try:
            async with websockets.connect(
                websocket_url,
                # ssl=ssl_context,
                ping_interval=30,
                ping_timeout=10,
            ) as websocket:
                print(f"Connected as {self.client_id} from {self.computer_name}")

                await websocket.send(
                    json.dumps(
                        {
                            "type": "device_connected",
                            "email": self.owner_email,
                            "machine_name": self.computer_name,
                        }
                    )
                )

                while True:
                    try:
                        message = await websocket.recv()
                        await self.handle_message(websocket, message)
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed")
                        return False
                    except Exception as e:
                        print(f"Error in message loop: {e}")
                        return False

        except (websockets.exceptions.WebSocketException, ssl.SSLError) as e:
            print(f"Connection error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    async def start(self):
        retries = 0
        while retries < self.max_retries:
            try:
                if await self.connect():
                    retries = 0  # Reset retry counter on successful connection
                else:
                    retries += 1
                    if retries < self.max_retries:
                        wait_time = self.retry_delay * (
                            2 ** (retries - 1)
                        )  # Exponential backoff
                        print(
                            f"Reconnecting in {wait_time} seconds... (Attempt {retries}/{self.max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        print("Max retries reached. Exiting...")
                        break
            except Exception as e:
                print(f"Critical error: {e}")
                break


def main():
    client = WSClient()
    try:
        asyncio.run(client.start())
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == "__main__":
    main()
