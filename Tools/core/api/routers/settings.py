from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from Tools.core.config_manager import ConfigManager, get_config

router = APIRouter(prefix="/settings", tags=["settings"])

class SettingUpdate(BaseModel):
    key: str
    value: str

@router.get("/list")
async def list_settings():
    config = get_config()
    # Flatten the config for the UI for backward compatibility
    flat_settings = []
    
    config_dict = config.model_dump()
    for group, settings in config_dict.items():
        for key, value in settings.items():
            flat_settings.append({
                "key": f"{group}.{key}",
                "value": str(value),
                "description": f"Setting in group {group}"
            })
            
    return {"settings": flat_settings}

@router.get("/structure")
async def get_settings_structure():
    """Returns the dynamic structure of all settings groups and keys."""
    try:
        return ConfigManager.get_structure()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update")
async def update_setting(req: SettingUpdate):
    try:
        config = ConfigManager.load_config()
        
        # Support dot notation: "ai.num_thread"
        parts = req.key.split(".")
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Key must be in format 'group.key'")
        
        group, key = parts
        
        if not hasattr(config, group):
            raise HTTPException(status_code=404, detail=f"Group {group} not found")
            
        group_obj = getattr(config, group)
        
        if not hasattr(group_obj, key):
            raise HTTPException(status_code=404, detail=f"Key {key} not found in group {group}")
            
        # Get target type for casting (Pydantic V2 style)
        field = group_obj.model_fields[key]
        target_type = field.annotation
        
        # Cast value (bool is tricky)
        if target_type is bool:
            casted_value = req.value.lower() in ("true", "1", "yes")
        else:
            # Handle possible Optional types or Unions if necessary, but here we assume simple types
            casted_value = target_type(req.value)
            
        setattr(group_obj, key, casted_value)
        
        # Save validated config
        ConfigManager.save_config(config)
        
        return {"status": "success", "message": f"Setting {req.key} updated."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid value for {req.key}: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
