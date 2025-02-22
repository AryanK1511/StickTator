import asyncio
import json
import logging
import os
import platform
import ssl
from pathlib import Path

import websockets
from dotenv import load_dotenv

load_dotenv()


class WSClient:
    def __init__(self):
        print("Initializing WSClient...")
        self.server_url = (
            f'ws://{os.getenv("SERVER_URL", "127.0.0.1:8000")}/ws/v1/machine'
        )
        print(f"Server URL: {self.server_url}")
        self.owner_email = self._read_owner_file()
        print(f"Owner email: {self.owner_email}")
        self.client_id = self.owner_email.split("@")[0] if self.owner_email else None
        print(f"Client ID: {self.client_id}")
        self.computer_name = platform.node()
        print(f"Computer name: {self.computer_name}")
        self.max_retries = 5
        self.retry_delay = 5
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _read_owner_file(self):
        print("Reading owner.txt file...")
        try:
            return Path("owner.txt").read_text().strip()
        except FileNotFoundError:
            print("Error: owner.txt not found")
            return None
        except Exception as e:
            print(f"Error reading owner.txt: {e}")
            return None

    async def handle_message(self, websocket, message: str):
        print(f"Handling message: {message}")
        try:
            data = json.loads(message)
            if data.get("type") == "execute":
                print("Received execute command...")
                execution_plan = data.get("execution_plan")
                if execution_plan:
                    for category in execution_plan.get("categories", []):
                        commands = [
                            cmd.get("command")
                            for cmd in category.get("commands", [])
                            if cmd.get("command")
                        ]
                        if commands:
                            combined_cmd = " && ".join(commands)
                            print(f"Executing combined commands: {combined_cmd}")
                            process = await asyncio.create_subprocess_shell(
                                combined_cmd,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                            )
                            while True:
                                output = await process.stdout.readline()
                                print(f"Output: {output}")
                                if not output:
                                    break
                                if output:
                                    output_str = output.decode().strip()
                                    self.logger.info(f"Command output: {output_str}")
                                    await websocket.send(
                                        json.dumps(
                                            {
                                                "type": "command_output",
                                                "client_id": self.client_id,
                                                "computer_name": self.computer_name,
                                                "command": combined_cmd,
                                                "output": output_str,
                                            }
                                        )
                                    )
                            error = await process.stderr.read()
                            if error:
                                error_str = error.decode().strip()
                                self.logger.error(f"Command error: {error_str}")
                                await websocket.send(
                                    json.dumps(
                                        {
                                            "type": "command_error",
                                            "client_id": self.client_id,
                                            "computer_name": self.computer_name,
                                            "command": combined_cmd,
                                            "error": error_str,
                                        }
                                    )
                                )
                            else:
                                await websocket.send(
                                    json.dumps(
                                        {
                                            "type": "command_output",
                                            "client_id": self.client_id,
                                            "computer_name": self.computer_name,
                                            "command": combined_cmd,
                                            "output": "Command successfully executed with no output",
                                        }
                                    )
                                )
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON received: {message}")
        except Exception as e:
            print(f"Error handling message: {e}")

    async def connect(self):
        print("Attempting to connect...")
        if not self.client_id:
            print("Error: No client ID available")
            return False

        websocket_url = f"{self.server_url}/{self.client_id}"
        print(f"WebSocket URL: {websocket_url}")
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

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
                        print(f"Received message: {message}")
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
                    retries = 0
                else:
                    retries += 1
                    if retries < self.max_retries:
                        wait_time = self.retry_delay * (2 ** (retries - 1))
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
    print("Starting WSClient...")
    client = WSClient()
    try:
        asyncio.run(client.start())
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == "__main__":
    main()
