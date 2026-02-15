import json
from typing import Callable, Optional

from genson import SchemaBuilder
from jsonschema import ValidationError, validate

from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.utils import get_prompt_header
from Tools.core.ai_client import AIClient


class SchemaErrorCodes:
    SCHEMA_COULD_NOT_VALIDATED: str = "SCHEMA_COULD_NOT_VALIDATED"
    UNKNOWN_ERROR: str = "UNKNOWN_ERROR"
    EXPECTION_ERROR: str = "EXPECTION_ERROR"


def INVALID_RETURN_SCHEMA(schema: str, response: str):
    return {
        "messages": [
            {
                "role": "system",
                "content": "Invlid schema returned. Please take the respose and parse it into the requested schema.",
            },
            {"role": "system", "content": f"SCHEMA:\n{schema}"},
            {"role": "system", "content": f"LAST RESPONSE:\n{response}"},
        ],
        "format": "json",
        "stream": False,
    }


def SCHEMA_COULD_NOT_VALIDATED_RESPONSE(schema: str, response: str):
    return {
        "error": "Schema could not be validated multiple times.",
        "schema": schema,
        "response": response,
        "code": SchemaErrorCodes.SCHEMA_COULD_NOT_VALIDATED,
    }


def request_with_schema(
    obj: dict, payload: dict, role: Agents, optional_parser: Optional[Callable[[dict], dict]] = None
):
    """
    Call the AI with the schema information in the payload.
    Automaticly validate the response schema.
    If the response schema does not fit the requested schema, we try three times to get a valid response.
    If the response does not fit 3 times, we return an error with the schema and the response.

    Args:
        obj (dict): The example object to be parsed into a schema
        payload (dict): The requested payload with prompts
        role (Agents): The agent who resolve the request

    Return:
        dict: The response from the AI

    Raise:
        ValueError: If the input 'obj' is not a dictionary.
        ValidationError: If the schema does not fit
    """
    ai = AIClient()
    schema = get_valid_json_schema(obj, optional_parser)

    header = get_prompt_header(role)

    schema_message = {
        "role": "system",
        "content": f"Return ONLY a JSON object that strictly follows this schema:\n{schema}",
    }

    parsed_payload = payload
    parsed_payload["format"] = "json"
    parsed_payload["messages"] = [header, schema_message, *payload["messages"]]
    # Always set the stream to false. As we have event driven requests, we do not need to wait for a response
    parsed_payload["stream"] = False

    # After the 3. invalid schema validation, we return the response with an error
    validation_tries = 0

    try:
        res = ai.ask_direct(parsed_payload)
        is_valid = validate_ai_response(res, schema)

        while not is_valid and validation_tries <= 3:
            validation_tries += 1
            res = ai.ask_direct(INVALID_RETURN_SCHEMA(schema, res))
            is_valid = validate_ai_response(res, schema)

        if not is_valid:
            return SCHEMA_COULD_NOT_VALIDATED_RESPONSE(schema, res)

        return res
    except Exception as e:
        return {"error": str(e), "schema": schema, "payload": parsed_payload, "code": SchemaErrorCodes.EXPECTION_ERROR}
    except ValueError as e:
        return {
            "error": f"Unknown error. {e}",
            "schema": schema,
            "payload": parsed_payload,
            "code": SchemaErrorCodes.UNKNOWN_ERROR,
        }


def validate_ai_response(obj: dict, schema: str) -> bool:
    """
    Validates the response from the AI with the related schema.

    Args:
        obj (dict): Response from the AI
        schema (str): JSON schema to validate

    Return:
        bool: True if the response is valid. False otherwise.

    """
    schema_dict = json.loads(schema)

    try:
        validate(instance=obj, schema=schema_dict)
        return True
    except ValidationError:
        return False


def get_valid_json_schema(obj: dict, optional_parser: Optional[Callable[[dict], dict]] = None) -> str:
    """
    Generates a JSON schema from a given dictionary.

    This schema is used to guide the AI's response format,
    ensuring the output matches the required structure.

    Args:
        obj (dict): The example object to be parsed into a schema.

    Returns:
        str: The generated JSON schema as a formatted string.
    """
    # Prevent the function to parse non dict input
    if not isinstance(obj, dict):
        raise ValueError("Input 'obj' must be a dictionary.")

    builder = SchemaBuilder()
    builder.add_object(obj)

    # Convert the builder content to a schema dictionary
    schema = builder.to_schema()

    # Restrict the AI from adding unexpected fields
    schema["additionalProperties"] = False

    if optional_parser:
        # Optional. Parse the schema with the attached parser
        schema = optional_parser(schema)

    # Return the schema as a pretty-printed string
    return json.dumps(schema, indent=2)
