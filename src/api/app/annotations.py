from typing import Optional

from pdf_token_type_labels.TokenTypeLabel import TokenTypeLabel
from pydantic import BaseModel



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
    tokens: Optional[list[TokenId]] = None


class RelationGroup(BaseModel):
    sourceIds: list[str]
    targetIds: list[str]
    label: Label


class PdfAnnotation(BaseModel):
    annotations: list[Annotation]
    relations: list[RelationGroup]
