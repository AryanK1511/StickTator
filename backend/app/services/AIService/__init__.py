import json
import os
from typing import Dict, List, Tuple, Union

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
                    model="gpt-4o-mini",
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

    def generate_report(
        self, execution_result: Dict[str, Union[str, List[str]]]
    ) -> Tuple[str, str]:
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert system administrator and technical writer. Your task is to create detailed, 
                    professional markdown reports from command execution results. The report should include:

                    1. A clear title and timestamp
                    2. Command execution context and purpose
                    3. Detailed analysis of the command output
                    4. Any potential implications or recommendations
                    5. Next steps or related commands that might be useful

                    Format the report professionally using markdown, including:
                    - Clear section headers
                    - Code blocks for commands and outputs
                    - Tables where appropriate
                    - Bold/italic emphasis for important points
                    
                    Make the report informative yet concise, focusing on what's most relevant to a system administrator
                    or developer. Avoid any placeholder text - all content should be specific to the actual command and output provided.""",
                },
                {
                    "role": "user",
                    "content": f"""Generate a detailed markdown report for this command execution:
                    
                    Machine ID: {execution_result['machine_id']}
                    Command: {execution_result['command']}
                    Output: {json.dumps(execution_result['output'])}
                    Type: {execution_result['type']}
                    
                    Analyze the output and provide meaningful insights.""",
                },
            ]

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
            )

            report_content = response.choices[0].message.content

            # Generate a one-liner description
            description_messages = [
                {
                    "role": "system",
                    "content": """You are an expert system administrator and technical writer. Your task is to create a concise, 
                    one-liner description of the command execution result.""",
                },
                {
                    "role": "user",
                    "content": f"""Generate a one-liner description for this command execution:
                    
                    Machine ID: {execution_result['machine_id']}
                    Command: {execution_result['command']}
                    Output: {json.dumps(execution_result['output'])}
                    Type: {execution_result['type']}""",
                },
            ]

            description_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=description_messages,
                temperature=0.7,
            )

            description = description_response.choices[0].message.content

            return report_content, description

        except Exception as e:
            raise Exception(f"Error generating report: {str(e)}")
