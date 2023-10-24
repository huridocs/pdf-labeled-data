import uuid
from typing import Optional

from pdf_token_type_labels.Label import Label
from pdf_token_type_labels.PageLabels import PageLabels
from pydantic import BaseModel

from api.app.Page import Page
from api.app.Token import Token
from api.app.annotations import Bounds, TokenId

from api.app.LabelColor import LabelColor


class Annotation(BaseModel):
    id: str
    page: int
    label: LabelColor
    bounds: Bounds
    tokens: Optional[list[TokenId]] = None

    def get_tokens(self, pages: dict[any, any]) -> list[Token]:
        page = [page_tokens for page_tokens in pages if page_tokens["page"]["index"] == self.page]
        if not page:
            return []

        tokens_to_reorder_indexes = [token.tokenIndex for token in self.tokens]
        page_tokens = [Token(**token, page_index=self.page) for token in page[0]["tokens"]]
        tokens_to_reorder = [token for index, token in enumerate(page_tokens) if index in tokens_to_reorder_indexes]
        return tokens_to_reorder

    @staticmethod
    def from_token(page: Page, token: Token):
        return Annotation(
            id=str(uuid.uuid4()),
            page=page.index,
            label=LabelColor(text="", color=""),
            bounds=Bounds.from_token(token),
            tokens=[],
        )

    @staticmethod
    def from_label(
        token_type_page: PageLabels,
        label: Label,
        labels_colors: list[LabelColor],
        is_reading_order: bool,
    ):
        if is_reading_order:
            text = str(label.label_type)

            return Annotation(
                id=str(uuid.uuid4()),
                page=token_type_page.number - 1,
                label=LabelColor(text=text, color=labels_colors[0].color),
                bounds=Bounds.from_label(label),
                tokens=[],
            )

        annotation_labels = [label_color for index, label_color in enumerate(labels_colors) if index == label.label_type]

        if annotation_labels:
            label_color = annotation_labels[0]
        else:
            label_color = labels_colors[0]

        return Annotation(
            id=str(uuid.uuid4()),
            page=token_type_page.number - 1,
            label=label_color,
            bounds=Bounds.from_label(label),
            tokens=[],
        )

    def to_token_type_label(self, labels_colors: list[LabelColor], is_reading_order: bool = False) -> Label:
        label_type = 0

        for index, label_color in enumerate(labels_colors):
            if label_color.text == self.label.text:
                label_type = index

        return Label(
            top=round(self.bounds.top),
            left=round(self.bounds.left),
            width=round(self.bounds.right - self.bounds.left),
            height=round(self.bounds.bottom - self.bounds.top),
            label_type=int(self.label.text) if is_reading_order else label_type,
        )
