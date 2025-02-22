import json
import os
from typing import Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class ValidationError(Exception):
    pass


class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def generate_commands(self, user_intent: str) -> Dict:
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert Ubuntu system administrator tasked with converting user intentions into precise, safe Ubuntu commands. 
                    Return a JSON response that can be used for both command execution and UI display.
                    
                    The response must follow this exact structure:
                    {
                        "metadata": {
                            "id": "unique-operation-id",
                            "title": "Brief descriptive title",
                            "description": "Concise operation description",
                        },
                        "execution_plan": {
                            "categories": [
                                {
                                    "id": "category-1",
                                    "name": "Category name",
                                    "description": "Category purpose",
                                    "order": 1,
                                    "commands": [
                                        {
                                            "id": "cmd-1",
                                            "command": "actual command",
                                            "description": "what this command does",
                                            "order": 1,
                                            "requires_sudo": true|false,
                                        }
                                    ]
                                }
                            ]
                        },
                    }""",
                },
                {
                    "role": "user",
                    "content": f"Convert this user intention into Ubuntu commands: {user_intent}",
                },
            ]

            while True:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )

                try:
                    structured_response = json.loads(
                        response.choices[0].message.content
                    )
                    self._validate_response_structure(structured_response)
                    return structured_response
                except json.JSONDecodeError:
                    raise ValueError("Invalid response format from AI")
                except ValidationError:
                    continue

        except Exception:
            raise

    def _validate_response_structure(self, response: Dict) -> None:
        required_sections = ["metadata", "execution_plan"]
        for section in required_sections:
            if section not in response:
                raise ValidationError(f"Response missing required section: {section}")

        if "categories" not in response["execution_plan"]:
            raise ValidationError("Response missing categories in execution_plan")

        dangerous_patterns = [
            "rm -rf /",
            "mkfs",
            "> /dev/sda",
            "dd if=/dev/zero",
            ":(){:|:&};:",
        ]

        for category in response["execution_plan"]["categories"]:
            for command in category["commands"]:
                for pattern in dangerous_patterns:
                    if pattern in command["command"]:
                        raise ValidationError(
                            f"Dangerous command pattern detected: {pattern}"
                        )


if __name__ == "__main__":
    service = AIService()
    try:
        operation = service.generate_commands(
            "install and configure postgresql with a new database"
        )

        print(operation)

    except Exception as e:
        print(f"Error: {e}")
