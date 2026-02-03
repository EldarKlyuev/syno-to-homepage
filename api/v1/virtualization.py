"""
Virtualization API endpoints for VM management.
"""
from fastapi import APIRouter, Depends, status

from core.deps import SynologyServiceDep
from schema.synology import GuestListResponse, HomepageResponse, HomepageStats
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


@router.get("/homepage", response_model=HomepageResponse, status_code=status.HTTP_200_OK)
async def get_homepage_stats(
    service: SynologyService = SynologyServiceDep,
) -> HomepageResponse:
    """
    Get aggregated VM statistics for homepage.
    
    Args:
        service: Synology service dependency
        
    Returns:
        Aggregated statistics for running VMs
    """
    guests_response = await service.list_guests()
    
    # Фильтруем только running VM и агрегируем
    running_vms = [g for g in guests_response.guests if g.status == "running"]
    
    return HomepageResponse(
        data=HomepageStats(
            runningram=sum(g.vram_size or 0 for g in running_vms),
            runningcpu=sum(g.vcpu_num or 0 for g in running_vms),
            runningcount=len(running_vms)
        )
    )