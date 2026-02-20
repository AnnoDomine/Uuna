import json
from typing import Callable, Optional

from genson import SchemaBuilder
from jsonschema import ValidationError, validate

from Tools.agents.get_agent_skill_set import Agents
from Tools.core.ai_client import AIClient
from Tools.core.prompt_builder import get_prompt_header


class SchemaErrorCodes:
    SCHEMA_COULD_NOT_VALIDATED: str = "SCHEMA_COULD_NOT_VALIDATED"
    UNKNOWN_ERROR: str = "UNKNOWN_ERROR"
    EXCEPTION_ERROR: str = "EXCEPTION_ERROR"


def _get_invalid_schema_payload(schema: str, response: str) -> dict:
    return {
        "messages": [
            {
                "role": "system",
                "content": "Invalid schema returned. Please take the response and parse it into the requested schema.",
            },
            {"role": "system", "content": f"SCHEMA:\n{schema}"},
            {"role": "system", "content": f"LAST RESPONSE:\n{response}"},
        ],
        "format": "json",
        "stream": False,
    }


def request_with_schema(
    obj: dict, payload: dict, role: Agents, optional_parser: Optional[Callable[[dict], dict]] = None
) -> dict:
    """
    Calls the AI with schema enforcement and automatic validation/retries.

    Args:
    - obj: An example dictionary used to generate the expected JSON schema.
    - payload: The request payload containing messages.
    - role: The agent role responsible for the request.
    - optional_parser: An optional function to post-process the generated schema.
    """
    ai = AIClient()
    schema = get_json_schema(obj, optional_parser)
    header = get_prompt_header(role)

    schema_msg_content = f"Return ONLY a JSON object that strictly follows this schema:\n{schema}"
    schema_message = {
        "role": "system",
        "content": schema_msg_content,
    }

    # Prepare final payload
    parsed_payload = payload.copy()
    parsed_payload["format"] = "json"
    parsed_payload["messages"] = [header, schema_message, *payload.get("messages", [])]
    parsed_payload["stream"] = False

    validation_tries = 0
    max_retries = 3

    try:
        res = ai.ask_direct(parsed_payload)
        is_valid = validate_ai_response(res, schema)

        while not is_valid and validation_tries < max_retries:
            validation_tries += 1
            # Re-request with error context
            res = ai.ask_direct(_get_invalid_schema_payload(schema, str(res)))
            is_valid = validate_ai_response(res, schema)

        if not is_valid:
            return {
                "error": "Schema could not be validated after retries.",
                "schema": schema,
                "response": res,
                "code": SchemaErrorCodes.SCHEMA_COULD_NOT_VALIDATED,
            }

        return res

    except Exception as e:
        return {
            "error": str(e),
            "schema": schema,
            "payload": parsed_payload,
            "code": SchemaErrorCodes.EXCEPTION_ERROR,
        }


def validate_ai_response(obj: any, schema: str) -> bool:
    """Validates an object against a JSON schema string."""
    try:
        if isinstance(obj, str):
            # Attempt to parse if string
            obj = json.loads(obj)
        schema_dict = json.loads(schema)
        validate(instance=obj, schema=schema_dict)
        return True
    except (ValidationError, json.JSONDecodeError):
        return False


def get_json_schema(obj: dict, optional_parser: Optional[Callable[[dict], dict]] = None) -> str:
    """Generates a JSON schema string from a template dictionary."""
    if not isinstance(obj, dict):
        raise ValueError("Input 'obj' must be a dictionary.")

    builder = SchemaBuilder()
    builder.add_object(obj)
    schema = builder.to_schema()
    schema["additionalProperties"] = False

    if optional_parser:
        schema = optional_parser(schema)

    return json.dumps(schema, indent=2)
