import uuid
from typing import Optional, List, Dict

from pydantic import BaseModel

from app.Token import Token
from app.TokenType import TokenType
from app.annotations import Bounds, TokenId

from app.TokenTypeLabel import TokenTypeLabel
from app.TokenTypePage import TokenTypePage

from app.Label import Label


class Annotation(BaseModel):
    id: str
    page: int
    label: Label
    bounds: Bounds
    tokens: Optional[List[TokenId]] = None

    def get_distance_from_token(self, token: Token):
        return (
                abs(self.bounds.left - token.x)
                + abs(self.bounds.top - token.y)
                + abs(self.bounds.right - (token.x + token.width))
                + abs(self.bounds.bottom - (token.y + token.height))
        )

    def get_tokens(self, pages: Dict[any, any]) -> List[Token]:
        page = [page_tokens for page_tokens in pages if page_tokens["page"]["index"] == self.page]
        if not page:
            return []

        tokens_to_reorder_indexes = [token.tokenIndex for token in self.tokens]
        page_tokens = [Token(**token, page_index=self.page) for token in page[0]["tokens"]]
        tokens_to_reorder = [token for index, token in enumerate(page_tokens) if index in tokens_to_reorder_indexes]
        return tokens_to_reorder

    @staticmethod
    def from_label(token_type_page: TokenTypePage, token_type_label: TokenTypeLabel, labels: List[Label]):
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

    def to_token_type_label(self) -> TokenTypeLabel:
        return TokenTypeLabel(top=self.bounds.top,
                              left=self.bounds.left,
                              width=self.bounds.right - self.bounds.left,
                              height=self.bounds.bottom - self.bounds.top,
                              token_type=TokenType.from_text(self.label.text))
