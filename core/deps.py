"""
FastAPI dependencies for Synology API service.
"""
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status

from service.synology_service import SynologyService


async def get_synology_service() -> AsyncGenerator[SynologyService, None]:
    """
    Dependency to get an authenticated Synology service instance.
    
    Yields:
        SynologyService: Authenticated service instance
        
    Raises:
        HTTPException: If connection to Synology NAS fails
    """
    service = SynologyService()
    
    try:
        async with service:
            # Ensure we can connect and authenticate
            await service._ensure_authenticated()
            yield service
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Synology NAS: {str(e)}"
        )


# Convenience alias for dependency injection
SynologyServiceDep = Depends(get_synology_service)