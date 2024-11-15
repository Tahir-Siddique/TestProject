from typing import Generic, TypeVar, Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse

T = TypeVar('T')

class BaseAPIResponse(Generic[T], BaseModel):
    data: Union[T, dict, None] = None
    error: Union[str, None] = None
    status_code: int = 200

    def __call__(self, *args, **kwargs):
        return JSONResponse(
            status_code=self.status_code,
            content=self.dict(exclude_none=True)
        )