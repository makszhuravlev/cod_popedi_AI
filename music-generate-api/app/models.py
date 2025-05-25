from pydantic import BaseModel


class GenerateRequest(BaseModel):
    text: str