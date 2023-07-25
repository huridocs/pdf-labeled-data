from enum import Enum


class TokenType(Enum):
    FORMULA = "FORMULA"
    FOOTNOTE = "FOOTNOTE"
    LIST = "LIST"
    TABLE = "TABLE"
    CODE = "CODE"
    FIGURE = "FIGURE"
    TITLE = "TITLE"
    TEXT = "TEXT"

    @staticmethod
    def from_text(text: str):
        try:
            return TokenType[text.upper()]
        except KeyError:
            return TokenType.TEXT

    @staticmethod
    def from_value(value: int):
        try:
            return TokenType(value).name.lower()
        except ValueError:
            return TokenType.TEXT.name.lower()

    def get_number(self):
        return self._member_names_.index(self.name)