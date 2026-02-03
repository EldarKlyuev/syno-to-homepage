"""
Virtualization API endpoints for VM management.
"""
from fastapi import APIRouter, Depends, status

from core.deps import SynologyServiceDep
from schema.synology import GuestListResponse
from service.synology_service import SynologyService

router = APIRouter(prefix="/virtualization", tags=["Virtualization"])


@router.get("/guests", response_model=GuestListResponse, status_code=status.HTTP_200_OK)
async def list_guests(
    service: SynologyService = SynologyServiceDep,
) -> GuestListResponse:
    """
    List all virtual machines.
    
    Args:
        service: Synology service dependency
        
    Returns:
        List of virtual machines
    """
    return await service.list_guests()