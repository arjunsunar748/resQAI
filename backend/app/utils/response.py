"""
Standard response formatting utilities.
"""
from typing import Any, Dict, Optional


def success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(code: str, message: str, request_id: Optional[str] = None) -> Dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id or "unknown",
        }
    }
