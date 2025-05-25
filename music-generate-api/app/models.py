from pydantic import BaseModel


class GenerateRequest(BaseModel):
    text: str

class ErrorResponse(BaseModel):
    title: str
    message: str