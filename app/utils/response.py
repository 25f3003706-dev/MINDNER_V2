"""Standard API response envelope and formatting helpers."""

from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = 200,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Formats a standardized success API response dictionary."""
    res: Dict[str, Any] = {
        "success": True,
        "message": message,
        "data": data,
    }
    if meta is not None:
        res["meta"] = meta
    return res


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    details: Optional[Any] = None,
) -> JSONResponse:
    """Creates a standardized error JSONResponse."""
    content: Dict[str, Any] = {
        "success": False,
        "message": message,
    }
    if details is not None:
        content["details"] = details
    return JSONResponse(status_code=status_code, content=content)
