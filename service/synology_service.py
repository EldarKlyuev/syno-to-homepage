"""
Synology API service with HTTP client for File Station and Virtualization APIs.
"""
import asyncio
import json
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import httpx
from fastapi import HTTPException, status

from core.config import settings
from schema.synology import (
    FileListRequest,
    FileListResponse,
    GuestListResponse,
    LoginResponse,
    SearchRequest,
    ShareListResponse,
    SynologyBaseResponse,
)


class SynologyService:
    """
    Synology NAS API service.
    
    Handles authentication and provides methods for File Station and Virtualization APIs.
    """
    
    def __init__(self):
        self.base_url = settings.SYNOLOGY_URL.rstrip('/')
        self.username = settings.SYNOLOGY_USER
        self.password = settings.SYNOLOGY_PASSWORD
        self.verify_ssl = settings.SYNOLOGY_VERIFY_SSL
        self.session_timeout = settings.SYNOLOGY_SESSION_TIMEOUT
        
        # Session management
        self._sid: Optional[str] = None
        self._session_expires: Optional[datetime] = None
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                verify=self.verify_ssl,
                timeout=30.0,
                follow_redirects=True
            )
        return self._client
    
    async def close(self):
        """Close HTTP client and logout if needed."""
        if self._sid:
            try:
                await self.logout()
            except Exception:
                pass  # Ignore logout errors during cleanup
        
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _is_session_valid(self) -> bool:
        """Check if current session is valid."""
        return (
            self._sid is not None 
            and self._session_expires is not None 
            and datetime.now() < self._session_expires
        )
    
    async def _make_request(
        self, 
        endpoint: str, 
        params: Dict[str, Any],
        require_auth: bool = True
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Synology API.
        
        Args:
            endpoint: API endpoint (e.g., 'auth.cgi', 'entry.cgi')
            params: Request parameters
            require_auth: Whether to include session ID
            
        Returns:
            Response data dictionary
            
        Raises:
            HTTPException: On API errors
        """
        client = await self._ensure_client()
        url = f"{self.base_url}/webapi/{endpoint}"
        
        # Add session ID if required and available
        if require_auth and self._sid:
            params["_sid"] = self._sid
        
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check Synology API success flag
            if not data.get("success", False):
                error_info = data.get("error", {})
                error_code = error_info.get("code", 0)
                
                # Handle session expired
                if error_code == 105:  # Session expired
                    self._sid = None
                    self._session_expires = None
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Session expired. Please login again."
                    )
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Synology API error: {error_info}"
                )
            
            return data
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to Synology NAS: {str(e)}"
            )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invalid response from Synology NAS"
            )
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid session, login if needed."""
        if not self._is_session_valid():
            await self.login()
    
    # Authentication methods
    async def login(self, account: Optional[str] = None, passwd: Optional[str] = None) -> LoginResponse:
        """
        Login to Synology NAS.
        
        Args:
            account: Username (uses config if not provided)
            passwd: Password (uses config if not provided)
            
        Returns:
            Login response with session ID
        """
        params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": account or self.username,
            "passwd": passwd or self.password,
            "session": "FileStation",
            "format": "sid"
        }
        
        data = await self._make_request("auth.cgi", params, require_auth=False)
        
        # Extract session ID
        self._sid = data.get("data", {}).get("sid")
        if self._sid:
            self._session_expires = datetime.now() + timedelta(seconds=self.session_timeout)
        
        return LoginResponse(
            success=data.get("success", False),
            data=data.get("data"),
            sid=self._sid
        )
    
    async def logout(self) -> bool:
        """
        Logout from Synology NAS.
        
        Returns:
            True if logout successful
        """
        if not self._sid:
            return True
        
        params = {
            "api": "SYNO.API.Auth",
            "version": "1",
            "method": "logout",
            "session": "FileStation"
        }
        
        try:
            data = await self._make_request("auth.cgi", params, require_auth=True)
            success = data.get("success", False)
        except Exception:
            success = False
        
        # Clear session regardless of logout result
        self._sid = None
        self._session_expires = None
        
        return success
    
    # File Station API methods
    async def get_filestation_info(self) -> Dict[str, Any]:
        """Get File Station information."""
        await self._ensure_authenticated()
        
        params = {
            "api": "SYNO.FileStation.Info",
            "version": "2",
            "method": "get"
        }
        
        data = await self._make_request("entry.cgi", params)
        return data.get("data", {})
    
    async def list_shares(self, additional: Optional[List[str]] = None) -> ShareListResponse:
        """
        List shared folders.
        
        Args:
            additional: Additional info to include
            
        Returns:
            List of shared folders
        """
        await self._ensure_authenticated()
        
        params = {
            "api": "SYNO.FileStation.List",
            "version": "2",
            "method": "list_share"
        }
        
        if additional:
            params["additional"] = json.dumps(additional)
        
        data = await self._make_request("entry.cgi", params)
        shares_data = data.get("data", {}).get("shares", [])
        
        return ShareListResponse(
            shares=shares_data,
            offset=data.get("data", {}).get("offset", 0),
            total=data.get("data", {}).get("total", len(shares_data))
        )
    
    async def list_files(self, request: FileListRequest) -> FileListResponse:
        """
        List files in a directory.
        
        Args:
            request: File listing request parameters
            
        Returns:
            List of files and folders
        """
        await self._ensure_authenticated()
        
        params = {
            "api": "SYNO.FileStation.List",
            "version": "2",
            "method": "list",
            "folder_path": request.folder_path,
            "offset": request.offset,
            "limit": request.limit,
            "sort_by": request.sort_by,
            "sort_direction": request.sort_direction,
            "filetype": request.filetype
        }
        
        if request.pattern:
            params["pattern"] = request.pattern
        if request.goto_path:
            params["goto_path"] = request.goto_path
        if request.additional:
            params["additional"] = json.dumps(request.additional)
        
        data = await self._make_request("entry.cgi", params)
        files_data = data.get("data", {}).get("files", [])
        
        return FileListResponse(
            files=files_data,
            offset=data.get("data", {}).get("offset", 0),
            total=data.get("data", {}).get("total", len(files_data))
        )
    
    async def search_files(self, request: SearchRequest) -> FileListResponse:
        """
        Search for files.
        
        Args:
            request: Search request parameters
            
        Returns:
            Search results
        """
        await self._ensure_authenticated()
        
        params = {
            "api": "SYNO.FileStation.Search",
            "version": "2",
            "method": "start",
            "folder_path": request.folder_path,
            "recursive": "true" if request.recursive else "false",
            "pattern": request.pattern,
            "filetype": request.filetype
        }
        
        # Add optional parameters
        if request.extension:
            params["extension"] = request.extension
        if request.size_from is not None:
            params["size_from"] = request.size_from
        if request.size_to is not None:
            params["size_to"] = request.size_to
        if request.mtime_from is not None:
            params["mtime_from"] = request.mtime_from
        if request.mtime_to is not None:
            params["mtime_to"] = request.mtime_to
        
        data = await self._make_request("entry.cgi", params)
        
        # Search is async, we get a task ID and need to poll for results
        task_id = data.get("data", {}).get("taskid")
        if not task_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start search task"
            )
        
        # Poll for search results (simplified - in production, consider websockets)
        for _ in range(30):  # Max 30 attempts
            await asyncio.sleep(1)
            
            list_params = {
                "api": "SYNO.FileStation.Search",
                "version": "2",
                "method": "list",
                "taskid": task_id
            }
            
            try:
                result_data = await self._make_request("entry.cgi", list_params)
                if result_data.get("data", {}).get("finished"):
                    files = result_data.get("data", {}).get("files", [])
                    return FileListResponse(
                        files=files,
                        offset=0,
                        total=len(files)
                    )
            except Exception:
                continue
        
        # Cleanup search task
        try:
            cleanup_params = {
                "api": "SYNO.FileStation.Search",
                "version": "2",
                "method": "stop",
                "taskid": task_id
            }
            await self._make_request("entry.cgi", cleanup_params)
        except Exception:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Search timeout"
        )
    
    # Virtualization API methods
    async def list_guests(self) -> GuestListResponse:
        """
        List virtual machines.
        
        Returns:
            List of VMs
        """
        await self._ensure_authenticated()
        
        params = {
            "api": "SYNO.Virtualization.API.Guest",
            "version": "1",
            "method": "list"
        }
        
        data = await self._make_request("entry.cgi", params)
        guests_data = data.get("data", {}).get("guests", [])
        
        return GuestListResponse(
            guests=guests_data,
            offset=0,
            total=len(guests_data)
        )
    