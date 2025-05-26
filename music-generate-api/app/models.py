from pydantic import BaseModel


class GenerateRequest(BaseModel):
    prompt: str

class ErrorResponse(BaseModel):
    title: str
    message: str