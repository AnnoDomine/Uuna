import json
from typing import Callable, Optional, Type, Union

from genson import SchemaBuilder
from jsonschema import ValidationError, validate
from pydantic import BaseModel

from Tools.agents.get_agent_skill_set import Agents
from Tools.core.ai_client import AIClient
from Tools.core.prompt_builder import get_prompt_header
from Tools.core.shared_debugger import debugger


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
    obj: Union[dict, Type[BaseModel]], payload: dict, role: Agents, optional_parser: Optional[Callable[[dict], dict]] = None
) -> dict:
    """
    Calls the AI with schema enforcement, automatic validation/retries, and RAG context injection.
    """
    from Tools.core.api.managers.vector_manager import VectorManager
    
    ai = AIClient()
    vm = VectorManager()
    
    agent_name = role.value if hasattr(role, "value") else str(role)
    debugger.add_log(f"Requesting schema-validated output for {agent_name}", agent=agent_name, process="AI:SchemaRequest")

    # 1. RAG: Search Memory for relevant context
    from Tools.core.config_manager import get_config
    config = get_config()
    limit = config.ai.memory_limit
    
    user_msgs = [m.get("content", "") for m in payload.get("messages", []) if m.get("role") == "user"]
    search_query = user_msgs[-1] if user_msgs else ""
    
    memory_context = ""
    if search_query:
        # Search enough to allow quality filtering
        raw_memories = vm.search_memory(agent_name, search_query, limit=limit * 2)
        # Sort by quality_score in metadata (DESC)
        sorted_memories = sorted(
            raw_memories, 
            key=lambda x: x.get("metadata", {}).get("quality_score", 0), 
            reverse=True
        )
        # Take requested amount of high-quality memories
        top_memories = sorted_memories[:limit]
        
        if top_memories:
            ctx_lines = [f"- {m['content']} (Quality: {m['metadata'].get('quality_score', 'N/A')}%)" for m in top_memories]
            memory_context = "LONG-TERM MEMORY (HIGH QUALITY PREVIOUS FINDINGS):\n" + "\n".join(ctx_lines)
            debugger.add_log(f"Injected {len(top_memories)} high-quality memories into context.", agent=agent_name, process="AI:RAG")

    # 2. Schema Generation
    if isinstance(obj, type) and issubclass(obj, BaseModel):
        schema_dict = obj.model_json_schema()
        schema_dict["additionalProperties"] = False
        if optional_parser:
            schema_dict = optional_parser(schema_dict)
        schema = json.dumps(schema_dict, indent=2)
    else:
        schema = get_json_schema(obj, optional_parser)

    header = get_prompt_header(role)
    
    # 3. Assemble Payload with Memory Context
    schema_msg_content = f"Return ONLY a JSON object that strictly follows this schema:\n{schema}"
    
    messages = [header]
    if memory_context:
        messages.append({"role": "system", "content": memory_context})
    
    messages.append({"role": "system", "content": schema_msg_content})
    messages.extend(payload.get("messages", []))

    parsed_payload = payload.copy()
    parsed_payload["format"] = "json"
    parsed_payload["messages"] = messages
    parsed_payload["stream"] = False

    validation_tries = 0
    max_retries = 3

    try:
        res = ai.ask_direct(parsed_payload)
        is_valid = validate_ai_response(res, schema)

        while not is_valid and validation_tries < max_retries:
            validation_tries += 1
            debugger.add_log(f"Schema validation failed! Retry {validation_tries}/{max_retries}...", agent=agent_name, level="WARNING", process="AI:SchemaValidation")
            # Re-request with error context
            res = ai.ask_direct(_get_invalid_schema_payload(schema, str(res)))
            is_valid = validate_ai_response(res, schema)

        if not is_valid:
            debugger.add_log("Schema could not be validated after all retries.", agent=agent_name, level="ERROR", process="AI:SchemaValidation")
            return {
                "error": "Schema could not be validated after retries.",
                "schema": schema,
                "response": res,
                "code": SchemaErrorCodes.SCHEMA_COULD_NOT_VALIDATED,
            }

        debugger.add_log("AI response validated successfully.", agent=agent_name, level="SUCCESS", process="AI:SchemaValidation")
        return res

    except Exception as e:
        debugger.add_log(f"Request crashed during validation: {e}", agent=agent_name, level="ERROR", process="AI:SchemaValidation")
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
