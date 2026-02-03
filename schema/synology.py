"""
Pydantic schemas for Synology API requests and responses.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


# Base response models
class SynologyBaseResponse(BaseModel):
    """Base Synology API response."""
    success: bool
    error: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None


class SynologyError(BaseModel):
    """Synology API error details."""
    code: int
    errors: Optional[Dict[str, Any]] = None


# Authentication schemas
class LoginRequest(BaseModel):
    """Login request (optional, can use env vars)."""
    account: Optional[str] = None
    passwd: Optional[str] = None
    session: str = "FileStation"
    format: str = "sid"


class LoginResponse(BaseModel):
    """Login response with session ID."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    sid: Optional[str] = None


class LogoutResponse(BaseModel):
    """Logout response."""
    success: bool


# File Station schemas
class FileStationInfo(BaseModel):
    """File Station info response."""
    hostname: Optional[str] = None
    is_manager: Optional[bool] = None
    support_sharing: Optional[bool] = None
    support_virtual_protocol: Optional[List[str]] = None


class ShareInfo(BaseModel):
    """Shared folder information."""
    name: str
    path: str
    desc: Optional[str] = None
    vol_path: Optional[str] = None
    additional: Optional[Dict[str, Any]] = None


class ShareListResponse(BaseModel):
    """List of shared folders."""
    shares: List[ShareInfo]
    offset: int = 0
    total: int = 0


class FileInfo(BaseModel):
    """File/folder information."""
    isdir: bool
    name: str
    path: str
    additional: Optional[Dict[str, Any]] = None


class FileListRequest(BaseModel):
    """File listing request."""
    folder_path: str
    offset: int = 0
    limit: int = 1000
    sort_by: str = "name"
    sort_direction: str = "asc"
    pattern: Optional[str] = None
    filetype: str = "all"
    goto_path: Optional[str] = None
    additional: Optional[List[str]] = None


class FileListResponse(BaseModel):
    """File listing response."""
    files: List[FileInfo]
    offset: int = 0
    total: int = 0


class SearchRequest(BaseModel):
    """File search request."""
    folder_path: str
    recursive: bool = True
    pattern: str
    extension: Optional[str] = None
    filetype: str = "all"
    size_from: Optional[int] = None
    size_to: Optional[int] = None
    mtime_from: Optional[int] = None
    mtime_to: Optional[int] = None
    crtime_from: Optional[int] = None
    crtime_to: Optional[int] = None
    atime_from: Optional[int] = None
    atime_to: Optional[int] = None


# Virtualization schemas
class GuestInfo(BaseModel):
    """Virtual machine guest information."""
    guest_id: str = Field(..., alias="guest_id")
    guest_name: str = Field(..., alias="guest_name")
    status: str  # running, stopped, paused, etc.
    autorun: Optional[int] = None
    vcpu_num: Optional[int] = None
    vram_size: Optional[int] = None
    description: Optional[str] = None
    storage_id: Optional[str] = None
    
    class Config:
        populate_by_name = True


class GuestListResponse(BaseModel):
    """List of virtual machines."""
    guests: List[GuestInfo]
    offset: int = 0
    total: int = 0


class GuestDetailsResponse(BaseModel):
    """Detailed VM information."""
    guest: GuestInfo
    network: Optional[List[Dict[str, Any]]] = None
    storage: Optional[List[Dict[str, Any]]] = None
    snapshot: Optional[List[Dict[str, Any]]] = None


class GuestActionRequest(BaseModel):
    """VM action request."""
    action: str  # poweron, shutdown, reboot, reset, pause, resume
    guest_id: Optional[str] = None
    guest_name: Optional[str] = None


class GuestActionResponse(BaseModel):
    """VM action response."""
    success: bool
    task_id: Optional[str] = None


class TaskInfo(BaseModel):
    """Task information."""
    task_id: str
    type: str
    status: str  # running, finished, error
    progress: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    create_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None


class TaskStatusResponse(BaseModel):
    """Task status response."""
    task: TaskInfo


# Generic API request/response
class GenericAPIRequest(BaseModel):
    """Generic Synology API request."""
    api: str
    version: str | int
    method: str
    additional_params: Optional[Dict[str, Any]] = None


class GenericAPIResponse(BaseModel):
    """Generic Synology API response."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[SynologyError] = None


# Homepage schemas
class HomepageStats(BaseModel):
    """Aggregated VM statistics for homepage."""
    runningram: int    # Сумма vram_size для running VM
    runningcpu: int    # Сумма vcpu_num для running VM
    runningcount: int  # Количество running VM


class HomepageResponse(BaseModel):
    """Homepage response wrapper."""
    data: HomepageStats