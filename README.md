# Synology API Proxy

FastAPI-based proxy for Synology File Station and Virtualization APIs with authentication through SYNO.API.Auth.

## Features

- **File Station API**: Complete proxy for file operations (list shares, browse files, search)
- **Virtualization API**: VM management (list VMs, power on/off, reboot, pause/resume)
- **Authentication**: Automatic session management with Synology NAS
- **FastAPI Architecture**: Following pseudo 3-tier architecture pattern
- **Type Safety**: Full Pydantic schema validation
- **Async Support**: Built with httpx for async HTTP operations

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Synology NAS details
   ```

3. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API:**
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

## API Endpoints

### File Station API (`/api/v1/filestation/`)

- `POST /login` - Login to Synology NAS
- `POST /logout` - Logout from session
- `GET /info` - Get File Station information
- `GET /shares` - List shared folders
- `GET /list` - List files in directory
- `GET /search` - Search for files

### Virtualization API (`/api/v1/virtualization/`)

- `GET /guests` - List virtual machines

## Configuration

Environment variables in `.env`:

```bash
# Synology NAS Configuration
SYNOLOGY_URL=https://192.168.1.100:5001
SYNOLOGY_USER=admin
SYNOLOGY_PASSWORD=your_password_here
SYNOLOGY_VERIFY_SSL=false
SYNOLOGY_SESSION_TIMEOUT=3600

# Application Configuration
APP_NAME=Synology API Proxy
DEBUG=false
API_V1_PREFIX=/api/v1
```

## Architecture

The project follows FastAPI best practices with a pseudo 3-tier architecture:

```
├── api/v1/              # API endpoints (routers)
├── core/                # Core configurations and dependencies
├── schema/              # Pydantic models for validation
├── service/             # Business logic and HTTP client
└── main.py              # Application entry point
```

## Authentication

The service automatically handles Synology authentication:

1. Uses environment variables for credentials
2. Maintains session with automatic renewal
3. Handles session expiration gracefully
4. Supports manual login/logout via API

## Error Handling

- Consistent error response format
- Proper HTTP status codes
- Synology API error mapping
- Connection failure handling

## Development

The codebase follows these conventions:

- **Type hints** for all functions
- **Async/await** patterns
- **Dependency injection** via FastAPI
- **Pydantic models** for data validation
- **Exception handling** with proper HTTP responses

## Example Usage

```python
import httpx

# List shared folders
response = httpx.get("http://localhost:8000/api/v1/filestation/shares")
shares = response.json()

# List VMs
response = httpx.get("http://localhost:8000/api/v1/virtualization/guests")
vms = response.json()
```