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
            f'wss://{os.getenv("SERVER_URL", "127.0.0.1:8000")}/ws/v1/machine'
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

    async def send_output(
        self,
        websocket,
        output_type: str,
        command: str,
        output: str = None,
        status: int = None,
        success: bool = None,
        error: str = None,
    ):
        """Helper function to send formatted output messages"""
        message = {
            "type": output_type,
            "client_id": self.client_id,
            "computer_name": self.computer_name,
            "command": command,
        }

        if output is not None:
            message["output"] = output
        if status is not None:
            message["status"] = status
        if success is not None:
            message["success"] = success
        if error is not None:
            message["error"] = error

        try:
            await websocket.send(json.dumps(message))
            print(f"Sent {output_type} message: {message}")
        except Exception as e:
            self.logger.error(f"Error sending {output_type} message: {e}")

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
                                    shell=True,
                                )

                                # Buffer for accumulating output
                                output_buffer = []

                                while True:
                                    if self.shutdown_event.is_set():
                                        process.terminate()
                                        break

                                    # Read from both stdout and stderr
                                    try:
                                        stdout_data = await process.stdout.readline()
                                        stderr_data = await process.stderr.readline()

                                        if (
                                            not stdout_data
                                            and not stderr_data
                                            and process.returncode is not None
                                        ):
                                            break

                                        # Handle stdout
                                        if stdout_data:
                                            output_line = stdout_data.decode().strip()
                                            if output_line:
                                                output_buffer.append(output_line)
                                                # Send immediate output update
                                                await self.send_output(
                                                    websocket,
                                                    "command_output",
                                                    combined_cmd,
                                                    output=output_line,
                                                )

                                        # Handle stderr
                                        if stderr_data:
                                            error_line = stderr_data.decode().strip()
                                            if error_line:
                                                output_buffer.append(
                                                    f"ERROR: {error_line}"
                                                )
                                                # Send immediate error output
                                                await self.send_output(
                                                    websocket,
                                                    "command_output",
                                                    combined_cmd,
                                                    output=f"ERROR: {error_line}",
                                                )

                                    except asyncio.TimeoutError:
                                        continue
                                    except Exception as e:
                                        self.logger.error(
                                            f"Error reading process output: {e}"
                                        )
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
                                        process.kill()
                                    returncode = -1

                                # Send final completion message
                                await self.send_output(
                                    websocket,
                                    "command_complete",
                                    combined_cmd,
                                    output="\n".join(output_buffer),
                                    status=returncode,
                                    success=returncode == 0,
                                )

                            except Exception as e:
                                self.logger.error(f"Error executing command: {e}")
                                await self.send_output(
                                    websocket,
                                    "command_error",
                                    combined_cmd,
                                    error=str(e),
                                )

        except json.JSONDecodeError:
            self.logger.error(f"Error: Invalid JSON received: {message}")
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            await self.send_output(websocket, "error", "", error=str(e))

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
