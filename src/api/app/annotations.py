from typing import Optional

from pdf_token_type_labels.Label import Label
from pydantic import BaseModel

from api.app.LabelColor import LabelColor
from api.app.Token import Token


class Bounds(BaseModel):
    left: float
    top: float
    right: float
    bottom: float

    @staticmethod
    def from_label(label: Label):
        right = label.left + label.width
        bottom = label.top + label.height
        return Bounds(top=label.top, left=label.left, right=right, bottom=bottom)

    @staticmethod
    def from_token(token: Token):
        return Bounds(top=token.y, left=token.x, right=token.x + token.width, bottom=token.y + token.height)

    def area(self):
        return abs(self.right - self.left) * abs(self.bottom - self.top)

    def intersection_percentage(self, other_bounds: "Bounds"):
        x1 = max(self.left, other_bounds.left)
        y1 = max(self.top, other_bounds.top)
        x2 = min(self.right, other_bounds.right)
        y2 = min(self.bottom, other_bounds.bottom)

        if x2 <= x1 or y2 <= y1:
            return 0

        return 100 * (x2 - x1) * (y2 - y1) / self.area()

    def __eq__(self, obj):
        return (
            isinstance(obj, Bounds)
            and obj.left == self.left
            and obj.top == self.top
            and obj.right == self.right
            and obj.bottom == self.bottom
        )


class TokenId(BaseModel):
    pageIndex: int
    tokenIndex: int


class Annotation(BaseModel):
    id: str
    page: int
    label: LabelColor
    bounds: Bounds
    tokens: Optional[list[TokenId]] = None


class PdfAnnotation(BaseModel):
    annotations: list[Annotation]
