"""
Module: endpoints.py
Description: API endpoints for health and status checks

External Dependencies:
- fastapi: https://fastapi.tiangolo.com/

Sample Input:
>>> GET /health

Expected Output:
>>> {"status": "healthy", "services": {"redis": "ok"}}
"""

from fastapi import APIRouter
import redis
from typing import Dict, Any

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    status = "healthy"
    services = {}
    
    # Check Redis
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        services["redis"] = "ok"
    except:
        services["redis"] = "unavailable"
        status = "degraded"
    
    return {
        "status": status,
        "services": services,
        "version": "1.0.0"
    }
