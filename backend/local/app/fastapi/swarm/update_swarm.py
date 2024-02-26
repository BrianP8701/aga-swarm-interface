from fastapi import FastAPI, Depends, APIRouter, HTTPException, Query
from typing import Dict
from pydantic import BaseModel

from app.utils.security.validate_token import validate_token
from app.utils.mongodb import update_kv, get_kv
app = FastAPI()
router = APIRouter()

class UpdateSwarmRequest(BaseModel):
    swarm_id: str
    swarm_updates: Dict

@router.put('/spawn/update_swarm')
async def update_swarm(update_swarm_request: UpdateSwarmRequest, user_id: str = Depends(validate_token)):
    try:        
        swarm_id = update_swarm_request.swarm_id
        swarm_updates = update_swarm_request.swarm_updates

        if not swarm_updates or not swarm_id:
            raise HTTPException(status_code=400, detail="Swarm updates and swarm_id is required")

        try:
            existing_swarm = get_kv("swarms", swarm_id)
        except:
            raise HTTPException(status_code=404, detail="Swarm not found")

        # Update the existing swarm with the new values
        for key, value in swarm_updates.items():
            if key not in existing_swarm:
                raise HTTPException(status_code=400, detail=f"Key '{key}' is not a valid swarm attribute")
            existing_swarm[key] = value

        update_kv("swarms", swarm_id, existing_swarm)
        return {"swarm": existing_swarm}
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
