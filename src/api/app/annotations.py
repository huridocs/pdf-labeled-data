from typing import Optional, List
from pydantic import BaseModel

from app.TokenTypeLabel import TokenTypeLabel


class Bounds(BaseModel):
    left: float
    top: float
    right: float
    bottom: float

    @staticmethod
    def from_label(token_type_label: TokenTypeLabel):
        right = token_type_label.left + token_type_label.width
        bottom = token_type_label.top + token_type_label.height
        return Bounds(top=token_type_label.top, left=token_type_label.left, right=right, bottom=bottom)


class Label(BaseModel):
    text: str
    color: str


class TokenId(BaseModel):
    pageIndex: int
    tokenIndex: int


class Annotation(BaseModel):
    id: str
    page: int
    label: Label
    bounds: Bounds
    tokens: Optional[List[TokenId]] = None


class RelationGroup(BaseModel):
    sourceIds: List[str]
    targetIds: List[str]
    label: Label


class PdfAnnotation(BaseModel):
    annotations: List[Annotation]
    relations: List[RelationGroup]
