"""
File Station API endpoints.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.deps import SynologyServiceDep
from schema.synology import (
    FileListRequest,
    FileListResponse,
    LoginRequest,
    LoginResponse,
    SearchRequest,
    ShareListResponse,
    SynologyBaseResponse,
)
from service.synology_service import SynologyService

router = APIRouter(prefix="/filestation", tags=["File Station"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    service: SynologyService = SynologyServiceDep,
) -> LoginResponse:
    """
    Login to Synology NAS.
    
    Args:
        login_data: Login credentials (optional, uses env vars if not provided)
        service: Synology service dependency
        
    Returns:
        Login response with session information
    """
    return await service.login(
        account=login_data.account,
        passwd=login_data.passwd
    )


@router.post("/logout", response_model=Dict[str, bool], status_code=status.HTTP_200_OK)
async def logout(service: SynologyService = SynologyServiceDep) -> Dict[str, bool]:
    """
    Logout from Synology NAS.
    
    Args:
        service: Synology service dependency
        
    Returns:
        Logout success status
    """
    success = await service.logout()
    return {"success": success}


@router.get("/info", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_info(service: SynologyService = SynologyServiceDep) -> Dict[str, Any]:
    """
    Get File Station information.
    
    Args:
        service: Synology service dependency
        
    Returns:
        File Station info
    """
    return await service.get_filestation_info()


@router.get("/shares", response_model=ShareListResponse, status_code=status.HTTP_200_OK)
async def list_shares(
    additional: Optional[str] = Query(None, description="Additional info as JSON array"),
    service: SynologyService = SynologyServiceDep,
) -> ShareListResponse:
    """
    List shared folders.
    
    Args:
        additional: Additional information to include (JSON array string)
        service: Synology service dependency
        
    Returns:
        List of shared folders
    """
    additional_list = None
    if additional:
        try:
            import json
            additional_list = json.loads(additional)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format for additional parameter"
            )
    
    return await service.list_shares(additional=additional_list)


@router.get("/list", response_model=FileListResponse, status_code=status.HTTP_200_OK)
async def list_files(
    folder_path: str = Query(..., description="Path to folder"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(1000, ge=1, le=5000, description="Number of items to return"),
    sort_by: str = Query("name", description="Sort by field"),
    sort_direction: str = Query("asc", regex="^(asc|desc)$", description="Sort direction"),
    pattern: Optional[str] = Query(None, description="Search pattern"),
    filetype: str = Query("all", description="File type filter"),
    goto_path: Optional[str] = Query(None, description="Go to specific path"),
    additional: Optional[str] = Query(None, description="Additional info as JSON array"),
    service: SynologyService = SynologyServiceDep,
) -> FileListResponse:
    """
    List files and folders in a directory.
    
    Args:
        folder_path: Path to the folder to list
        offset: Pagination offset
        limit: Number of items to return
        sort_by: Field to sort by
        sort_direction: Sort direction (asc/desc)
        pattern: Search pattern for filtering
        filetype: File type filter
        goto_path: Go to specific path
        additional: Additional information to include (JSON array string)
        service: Synology service dependency
        
    Returns:
        List of files and folders
    """
    additional_list = None
    if additional:
        try:
            import json
            additional_list = json.loads(additional)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format for additional parameter"
            )
    
    request = FileListRequest(
        folder_path=folder_path,
        offset=offset,
        limit=limit,
        sort_by=sort_by,
        sort_direction=sort_direction,
        pattern=pattern,
        filetype=filetype,
        goto_path=goto_path,
        additional=additional_list,
    )
    
    return await service.list_files(request)


@router.get("/search", response_model=FileListResponse, status_code=status.HTTP_200_OK)
async def search_files(
    folder_path: str = Query(..., description="Path to search in"),
    pattern: str = Query(..., description="Search pattern"),
    recursive: bool = Query(True, description="Recursive search"),
    extension: Optional[str] = Query(None, description="File extension filter"),
    filetype: str = Query("all", description="File type filter"),
    size_from: Optional[int] = Query(None, ge=0, description="Minimum file size"),
    size_to: Optional[int] = Query(None, ge=0, description="Maximum file size"),
    mtime_from: Optional[int] = Query(None, description="Modified time from (timestamp)"),
    mtime_to: Optional[int] = Query(None, description="Modified time to (timestamp)"),
    crtime_from: Optional[int] = Query(None, description="Created time from (timestamp)"),
    crtime_to: Optional[int] = Query(None, description="Created time to (timestamp)"),
    atime_from: Optional[int] = Query(None, description="Accessed time from (timestamp)"),
    atime_to: Optional[int] = Query(None, description="Accessed time to (timestamp)"),
    service: SynologyService = SynologyServiceDep,
) -> FileListResponse:
    """
    Search for files.
    
    Args:
        folder_path: Path to search in
        pattern: Search pattern
        recursive: Whether to search recursively
        extension: File extension filter
        filetype: File type filter
        size_from: Minimum file size in bytes
        size_to: Maximum file size in bytes
        mtime_from: Modified time from (Unix timestamp)
        mtime_to: Modified time to (Unix timestamp)
        crtime_from: Created time from (Unix timestamp)
        crtime_to: Created time to (Unix timestamp)
        atime_from: Accessed time from (Unix timestamp)
        atime_to: Accessed time to (Unix timestamp)
        service: Synology service dependency
        
    Returns:
        Search results
    """
    request = SearchRequest(
        folder_path=folder_path,
        pattern=pattern,
        recursive=recursive,
        extension=extension,
        filetype=filetype,
        size_from=size_from,
        size_to=size_to,
        mtime_from=mtime_from,
        mtime_to=mtime_to,
        crtime_from=crtime_from,
        crtime_to=crtime_to,
        atime_from=atime_from,
        atime_to=atime_to,
    )
    
    return await service.search_files(request)