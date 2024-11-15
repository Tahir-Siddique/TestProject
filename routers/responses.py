from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional, Union

class BaseAPIResponse:
    """
    A standardized response class for API responses, including status codes.
    """

    @staticmethod
    def get_response(
        status: str,
        message: str,
        data: Optional[Union[Dict[str, Any], list]] = None,
        status_code: int = 200,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        """
        Returns a standardized JSON response.

        Args:
            status (str): The response status ("success" or "error").
            message (str): A message associated with the response.
            data (Optional[Union[Dict, list]]): The response data (if any).
            status_code (int): The HTTP status code.
            metadata (Optional[Dict]): Additional metadata (if any).

        Returns:
            JSONResponse: A JSON response with a status code.
        """
        return JSONResponse(
            content={
                "status": status,
                "message": message,
                "data": data,
                "metadata": metadata or {},
            },
            status_code=status_code,
        )

    @staticmethod
    def get_success_response(
        data: Optional[Union[Dict[str, Any], list]] = None,
        message: str = "Success",
        status_code: int = 200,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        """
        Returns a success response.
        """
        return BaseAPIResponse.get_response("success", message, data, status_code, metadata)

    @staticmethod
    def get_error_response(
        error: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        """
        Returns an error response.
        """
        return BaseAPIResponse.get_response(
            "error", error, None, status_code, {"details": details or {}}
        )

    @staticmethod
    def get_paginated_response(
        data: list,
        total_count: int,
        page: int,
        items_per_page: int,
        has_more: bool,
        status_code: int = 200,
    ) -> JSONResponse:
        """
        Returns a paginated response.
        """
        metadata = {
            "pagination": {
                "total_count": total_count,
                "page": page,
                "items_per_page": items_per_page,
                "has_more": has_more,
            }
        }
        return BaseAPIResponse.get_response(
            "success", "Data retrieved successfully", data, status_code, metadata
        )
