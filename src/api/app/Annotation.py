import uuid
from typing import Optional

from pdf_token_type_labels.TokenType import TokenType
from pdf_token_type_labels.TokenTypeLabel import TokenTypeLabel
from pdf_token_type_labels.TokenTypePage import TokenTypePage
from pydantic import BaseModel

from api.app.Page import Page
from api.app.Token import Token
from api.app.annotations import Bounds, TokenId

from api.app.Label import Label


class Annotation(BaseModel):
    id: str
    page: int
    label: Label
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
            label=Label(text="", color=""),
            bounds=Bounds.from_token(token),
            tokens=[],
        )

    @staticmethod
    def from_label(
        token_type_page: TokenTypePage,
        token_type_label: TokenTypeLabel,
        labels: list[Label],
        is_reading_order: bool,
    ):
        if is_reading_order:
            try:
                text = str(token_type_label.token_type.get_index())
            except AttributeError:
                text = str(token_type_label.token_type)

            return Annotation(
                id=str(uuid.uuid4()),
                page=token_type_page.number - 1,
                label=Label(text=text, color=labels[0].color),
                bounds=Bounds.from_label(token_type_label),
                tokens=[],
            )

        annotation_labels = [label for label in labels if label.text == token_type_label.token_type.value]

        if annotation_labels:
            label = annotation_labels[0]
        else:
            label = labels[0]

        return Annotation(
            id=str(uuid.uuid4()),
            page=token_type_page.number - 1,
            label=label,
            bounds=Bounds.from_label(token_type_label),
            tokens=[],
        )

    def to_token_type_label(self, is_reading_order: bool = False) -> TokenTypeLabel:
        return TokenTypeLabel(
            top=self.bounds.top,
            left=self.bounds.left,
            width=self.bounds.right - self.bounds.left,
            height=self.bounds.bottom - self.bounds.top,
            token_type=int(self.label.text) if is_reading_order else TokenType.from_text(self.label.text),
        )
