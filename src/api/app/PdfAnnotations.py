import json
from pathlib import Path
from typing import List
from pydantic import BaseModel

from api.app.Label import Label
from api.app.Token import Token
from api.app.TokenTypeLabel import TokenTypeLabel

from api.app.TokenTypeLabels import TokenTypeLabels

from api.app.Annotation import Annotation
from api.app.TokenTypePage import TokenTypePage


class Bounds(BaseModel):
    left: float
    top: float
    right: float
    bottom: float


class TokenId(BaseModel):
    pageIndex: int
    tokenIndex: int


class PdfAnnotation(BaseModel):
    annotations: List[Annotation]

    def get_reordered_pdf_annotation(self, tokens_to_reorder: List[Token]):
        page_index = tokens_to_reorder[0].page_index
        page_annotations = [annotation for annotation in self.annotations if annotation.page == page_index]
        other_pages_annotations = [annotation for annotation in self.annotations if annotation.page != page_index]

        annotation_to_reorder = [self.get_annotation_from_token(token) for token in tokens_to_reorder]
        starting_label = min(
            [int(annotation.label.text) for annotation in annotation_to_reorder if annotation.label.text.isdigit()]
        )

        annotations_before = [
            annotation
            for annotation in page_annotations
            if annotation.label.text.isdigit() and int(annotation.label.text) < starting_label
        ]

        annotation_to_reorder = sorted(
            annotation_to_reorder, key=lambda annotation: (annotation.bounds.top, annotation.bounds.left)
        )

        annotations_after = [
            annotation
            for annotation in page_annotations
            if annotation not in annotations_before and annotation not in annotation_to_reorder
        ]

        annotations_reordered = annotations_before + annotation_to_reorder + annotations_after

        for index, annotation in enumerate(annotations_reordered):
            annotation.label.text = str(index + 1)

        return PdfAnnotation(annotations=annotations_reordered + other_pages_annotations)

    def get_reordered_pdf_annotation_by_position(self, token_to_reorder: Token, position: int) -> "PdfAnnotation":
        position_index = position - 1
        annotation_to_reorder = self.get_annotation_from_token(token_to_reorder)
        page_annotations = [annotation for annotation in self.annotations if annotation.page == token_to_reorder.page_index]
        other_pages_annotations = [
            annotation for annotation in self.annotations if annotation.page != token_to_reorder.page_index
        ]
        other_annotations_in_page = [annotation for annotation in page_annotations if annotation != annotation_to_reorder]
        annotations_reordered = (
                other_annotations_in_page[:position_index] + [annotation_to_reorder] + other_annotations_in_page[
                                                                                       position_index:]
        )

        for index, annotation in enumerate(annotations_reordered):
            annotation.label.text = str(index + 1)

        return PdfAnnotation(annotations=annotations_reordered + other_pages_annotations)

    def get_annotation_from_token(self, token: Token) -> Annotation:
        page_annotations = [annotation for annotation in self.annotations if annotation.page == token.page_index]
        distances = [annotation.get_distance_from_token(token) for annotation in page_annotations]
        annotation_index = distances.index(min(distances))
        return page_annotations[annotation_index]

    def save(self, annotations_path):
        with open(annotations_path, "w+") as f:
            f.write(self.json())

    @staticmethod
    def get_empty_annotation():
        return PdfAnnotation(annotations=[])

    @staticmethod
    def from_path(labels_path: Path, labels: List[Label]):
        labels_text = labels_path.read_text()
        labels_dict = json.loads(labels_text)
        token_type_labels = TokenTypeLabels(**labels_dict)
        annotations: List[Annotation] = list()
        for token_type_page, token_type_label in PdfAnnotation.loop_token_type_tokens(token_type_labels):
            annotations.append(Annotation.from_label(token_type_page, token_type_label, labels))

        return PdfAnnotation(annotations=annotations)

    def to_token_type_labels(self) -> TokenTypeLabels:
        page_numbers = {annotation.page for annotation in self.annotations}
        token_type_pages: List[TokenTypePage] = list()
        for page_number in page_numbers:
            page_annotations = [annotation for annotation in self.annotations if annotation.page == page_number]
            token_type_labels: List[TokenTypeLabel] = [annotation.to_token_type_label() for annotation in page_annotations]
            token_type_labels.sort(key=lambda token_type_label: (token_type_label.top, token_type_label.left))
            token_type_pages.append(TokenTypePage(number=page_number + 1, labels=token_type_labels))

        return TokenTypeLabels(pages=token_type_pages)

    @staticmethod
    def loop_token_type_tokens(token_type_labels: TokenTypeLabels):
        for token_type_page in token_type_labels.pages:
            for token_type_label in token_type_page.labels:
                yield token_type_page, token_type_label
