import asyncio
import json
import logging
import os
import platform
import signal
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
        self.shutdown_event = asyncio.Event()
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
                        if self.shutdown_event.is_set():
                            break

                        commands = [
                            cmd.get("command")
                            for cmd in category.get("commands", [])
                            if cmd.get("command")
                        ]

                        if commands:
                            combined_cmd = " && ".join(commands)
                            print(f"Executing combined commands: {combined_cmd}")

                            try:
                                process = await asyncio.create_subprocess_shell(
                                    combined_cmd,
                                    stdout=asyncio.subprocess.PIPE,
                                    stderr=asyncio.subprocess.PIPE,
                                )

                                # Handle stdout in real-time
                                while True:
                                    if self.shutdown_event.is_set():
                                        process.terminate()
                                        break

                                    try:
                                        output = await asyncio.wait_for(
                                            process.stdout.readline(), timeout=1.0
                                        )
                                        if not output:  # Process has finished
                                            break

                                        output_str = output.decode().strip()
                                        if output_str:  # Only send non-empty output
                                            self.logger.info(
                                                f"Command output: {output_str}"
                                            )
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
                                    except asyncio.TimeoutError:
                                        # Check if process has finished
                                        if process.returncode is not None:
                                            break
                                        continue
                                    except Exception as e:
                                        self.logger.error(f"Error reading stdout: {e}")
                                        break

                                # Wait for process to complete
                                try:
                                    returncode = await asyncio.wait_for(
                                        process.wait(), timeout=5.0
                                    )
                                except asyncio.TimeoutError:
                                    self.logger.warning(
                                        "Process took too long to complete, terminating..."
                                    )
                                    process.terminate()
                                    try:
                                        await asyncio.wait_for(
                                            process.wait(), timeout=2.0
                                        )
                                    except asyncio.TimeoutError:
                                        process.kill()  # Force kill if terminate doesn't work
                                    returncode = -1

                                # Handle any remaining stderr
                                error = await process.stderr.read()
                                error_str = error.decode().strip() if error else None

                                if error_str:
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

                                # Send completion message
                                await websocket.send(
                                    json.dumps(
                                        {
                                            "type": "command_complete",
                                            "client_id": self.client_id,
                                            "computer_name": self.computer_name,
                                            "command": combined_cmd,
                                            "status": returncode,
                                            "success": returncode == 0,
                                        }
                                    )
                                )

                            except Exception as e:
                                self.logger.error(f"Error executing command: {e}")
                                await websocket.send(
                                    json.dumps(
                                        {
                                            "type": "command_error",
                                            "client_id": self.client_id,
                                            "computer_name": self.computer_name,
                                            "command": combined_cmd,
                                            "error": str(e),
                                        }
                                    )
                                )

        except json.JSONDecodeError:
            self.logger.error(f"Error: Invalid JSON received: {message}")
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            # Send error to server to maintain connection
            try:
                await websocket.send(
                    json.dumps(
                        {
                            "type": "error",
                            "client_id": self.client_id,
                            "computer_name": self.computer_name,
                            "error": str(e),
                        }
                    )
                )
            except:
                pass  # If we can't send the error, don't crash

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

                while not self.shutdown_event.is_set():
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        print(f"Received message: {message}")
                        await self.handle_message(websocket, message)
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed")
                        return False
                    except Exception as e:
                        print(f"Error in message loop: {e}")
                        return False

                return True

        except (websockets.exceptions.WebSocketException, ssl.SSLError) as e:
            print(f"Connection error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    async def start(self):
        retries = 0
        while not self.shutdown_event.is_set() and retries < self.max_retries:
            try:
                if await self.connect():
                    retries = 0
                else:
                    retries += 1
                    if retries < self.max_retries and not self.shutdown_event.is_set():
                        wait_time = self.retry_delay * (2 ** (retries - 1))
                        print(
                            f"Reconnecting in {wait_time} seconds... (Attempt {retries}/{self.max_retries})"
                        )
                        try:
                            await asyncio.wait_for(
                                self.shutdown_event.wait(), timeout=wait_time
                            )
                        except asyncio.TimeoutError:
                            continue
                    else:
                        print("Max retries reached or shutdown requested. Exiting...")
                        break
            except Exception as e:
                print(f"Critical error: {e}")
                break

    async def shutdown(self):
        print("Initiating shutdown...")
        self.shutdown_event.set()

        if self.client_id:
            websocket_url = f"{self.server_url}/{self.client_id}"
            try:
                async with websockets.connect(
                    websocket_url,
                    ping_interval=30,
                    ping_timeout=10,
                ) as websocket:
                    await websocket.send(
                        json.dumps(
                            {
                                "type": "device_disconnected",
                                "email": self.owner_email,
                                "machine_name": self.computer_name,
                            }
                        )
                    )
                    print("Disconnect message sent")
            except Exception as e:
                print(f"Error sending disconnect message: {e}")


def main():
    print("Starting WSClient...")
    client = WSClient()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def handle_exit(signum, frame):
        print("\nShutting down...")
        loop.create_task(client.shutdown())

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        loop.run_until_complete(client.start())
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        pending = asyncio.all_tasks(loop)
        loop.run_until_complete(asyncio.gather(*pending))
        loop.close()


if __name__ == "__main__":
    main()
