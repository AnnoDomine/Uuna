import json
from typing import Type, List, Dict, Any
from pydantic import BaseModel
from loguru import logger

from Tools.agents.get_agent_skill_set import Agents
from Tools.core.ai_client import AIClient
from Tools.core.ai_schema_validator import validate_ai_response

class TrainingResult(BaseModel):
    success_count: int
    total_retries: int
    failed_rounds: List[int]
    status: str

def run_pattern_training(role: Agents, model_class: Type[BaseModel]) -> Dict[str, Any]:
    """
    Isolated training loop to ensure the AI respects the Pydantic pattern.
    Loop: 5 successful rounds, 3 attempts per round.
    """
    ai = AIClient()
    schema = json.dumps(model_class.model_json_schema(), indent=2)
    
    success_needed = 5
    max_retries_per_round = 3
    
    rounds_completed = 0
    total_retries = 0
    failed_rounds = []
    
    logger.info(f"Starting Pattern Training for {role.value} using {model_class.__name__}")
    
    while rounds_completed < success_needed:
        round_id = rounds_completed + 1
        current_round_success = False
        attempts = 0
        
        while attempts < max_retries_per_round:
            attempts += 1
            
            prompt = f"""
            TRAINING MODE: PATTERN COMPLIANCE
            ROLE: {role.value}
            TASK: Generate a valid, fictional example object that strictly follows the JSON schema provided below.
            
            SCHEMA:
            {schema}
            
            The data should be logically consistent with your role's identity.
            Return ONLY raw JSON.
            """
            
            try:
                # Direct AI call without orchestration overhead
                payload = {
                    "messages": [{"role": "user", "content": prompt}],
                    "format": "json",
                    "stream": False
                }
                
                response = ai.ask_direct(payload)
                
                if validate_ai_response(response, schema):
                    current_round_success = True
                    rounds_completed += 1
                    logger.success(f"Round {round_id} successful on attempt {attempts}")
                    break
                else:
                    logger.warning(f"Round {round_id}, Attempt {attempts}: Schema validation failed.")
                    total_retries += 1
            except Exception as e:
                logger.error(f"Round {round_id}, Attempt {attempts}: Error during AI call: {e}")
                total_retries += 1
        
        if not current_round_success:
            logger.error(f"Round {round_id} failed after {max_retries_per_round} attempts. Aborting training.")
            failed_rounds.append(round_id)
            break

    status = "SUCCESS" if len(failed_rounds) == 0 and rounds_completed == success_needed else "FAILED"
    
    return {
        "role": role.value,
        "model": model_class.__name__,
        "rounds_completed": rounds_completed,
        "total_retries": total_retries,
        "failed_rounds": failed_rounds,
        "status": status
    }
