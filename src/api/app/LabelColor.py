from pydantic import BaseModel


class LabelColor(BaseModel):
    name: str
    color: str
    metadata: str = ""
