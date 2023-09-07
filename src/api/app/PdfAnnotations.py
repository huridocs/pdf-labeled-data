import json
from pathlib import Path

from pdf_token_type_labels.TokenTypeLabel import TokenTypeLabel
from pdf_token_type_labels.TokenTypeLabels import TokenTypeLabels
from pdf_token_type_labels.TokenTypePage import TokenTypePage
from pydantic import BaseModel

from api.app.Label import Label
from api.app.Pages import Pages

from api.app.Annotation import Annotation


class Bounds(BaseModel):
    left: float
    top: float
    right: float
    bottom: float


class TokenId(BaseModel):
    pageIndex: int
    tokenIndex: int


class PdfAnnotation(BaseModel):
    annotations: list[Annotation]
    sorted_annotation_by_area: list[Annotation] = []

    def get_reordered_pdf_annotation_by_position(
        self, pages: Pages, annotation_to_reorder: Annotation, position: int
    ) -> "PdfAnnotation":
        tokens_annotations = self.get_annotations_from_pages(pages)
        pdf_annotation_from_tokens = PdfAnnotation(annotations=tokens_annotations).set_labels_for_reading_order()

        matching_annotations = [
            a
            for a in pdf_annotation_from_tokens.annotations
            if annotation_to_reorder.page == a.page and annotation_to_reorder.bounds == a.bounds
        ]

        if not matching_annotations:
            return pdf_annotation_from_tokens

        annotation_to_reorder = matching_annotations[0]
        other_annotations = [a for a in pdf_annotation_from_tokens.annotations if a != annotation_to_reorder]

        annotations_pages_before = [a for a in other_annotations if a.page < annotation_to_reorder.page]
        annotations_from_page = [a for a in other_annotations if a.page == annotation_to_reorder.page]
        annotations_pages_after = [a for a in other_annotations if a.page > annotation_to_reorder.page]

        page_annotations_reordered = (
            annotations_from_page[: position - 1] + [annotation_to_reorder] + annotations_from_page[position - 1 :]
        )

        for index, annotation in enumerate(page_annotations_reordered):
            annotation.label.text = str(index + 1)

        return PdfAnnotation(annotations=annotations_pages_before + page_annotations_reordered + annotations_pages_after)

    def get_reordered_pdf_annotations(self, pages: Pages, annotation: Annotation) -> "PdfAnnotation":
        tokens_annotations = self.get_annotations_from_pages(pages)
        pdf_annotation_from_tokens = PdfAnnotation(annotations=tokens_annotations).set_labels_for_reading_order()

        matching_annotations = [
            a
            for a in pdf_annotation_from_tokens.annotations
            if a.page == annotation.page and a.bounds.intersection_percentage(annotation.bounds) > 0
        ]

        if not matching_annotations:
            return pdf_annotation_from_tokens

        matching_annotations.sort(key=lambda a: (a.bounds.top, a.bounds.left))
        position = min([int(a.label.text) if a.label.text.isdigit() else 9999 for a in matching_annotations])

        other_annotations = [a for a in pdf_annotation_from_tokens.annotations if a not in matching_annotations]

        annotations_pages_before = [a for a in other_annotations if a.page < matching_annotations[0].page]
        annotations_from_page = [a for a in other_annotations if a.page == matching_annotations[0].page]
        annotations_pages_after = [a for a in other_annotations if a.page > matching_annotations[0].page]

        page_annotations_reordered = (
            annotations_from_page[: position - 1] + matching_annotations + annotations_from_page[position - 1 :]
        )

        for index, annotation in enumerate(page_annotations_reordered):
            annotation.label.text = str(index + 1)

        return PdfAnnotation(annotations=annotations_pages_before + page_annotations_reordered + annotations_pages_after)

    def set_labels_for_reading_order(self) -> "PdfAnnotation":
        if not self.annotations:
            return PdfAnnotation.get_empty_annotation()

        self.annotations.sort(key=lambda a: (a.page, int(a.label.text) if a.label.text.isdigit() else 99999))
        index = 1
        current_page = self.annotations[0].page
        for annotation in self.annotations:
            if current_page != annotation.page:
                current_page = annotation.page
                index = 1

            annotation.label.text = str(index)
            annotation.label.color = "#E8D3A2"
            index += 1

        return self

    def get_annotations_from_pages(self, pages: Pages) -> list[Annotation]:
        self.sorted_annotation_by_area = sorted(self.annotations, key=lambda a: a.bounds.area())
        annotations = []
        for page in pages.pages:
            for token in page.tokens:
                annotations.append(Annotation.from_token(page, token))
                self.set_label_to_annotation(annotations[-1])

        return annotations

    def set_label_to_annotation(self, annotation: Annotation):
        for annotation_by_size in self.sorted_annotation_by_area:
            if annotation_by_size.bounds.intersection_percentage(annotation.bounds) > 98:
                annotation.label = annotation_by_size.label

    @staticmethod
    def get_empty_annotation():
        return PdfAnnotation(annotations=[])

    @staticmethod
    def from_path(labels_path: Path, labels: list[Label], is_reading_order: bool):
        labels_text = labels_path.read_text()
        labels_dict = json.loads(labels_text)
        token_type_labels = TokenTypeLabels(**labels_dict)
        annotations: list[Annotation] = list()
        for token_type_page, token_type_label in PdfAnnotation.loop_token_type_tokens(token_type_labels):
            annotations.append(Annotation.from_label(token_type_page, token_type_label, labels, is_reading_order))

        return PdfAnnotation(annotations=annotations)

    def to_token_type_labels(self, is_reading_order=False) -> TokenTypeLabels:
        page_numbers = {annotation.page for annotation in self.annotations}
        token_type_pages: list[TokenTypePage] = list()
        for page_number in page_numbers:
            page_annotations = [annotation for annotation in self.annotations if annotation.page == page_number]
            token_type_labels: list[TokenTypeLabel] = [
                annotation.to_token_type_label(is_reading_order) for annotation in page_annotations
            ]
            token_type_labels.sort(
                key=lambda token_type_label: (
                    token_type_label.top,
                    token_type_label.left,
                )
            )
            token_type_pages.append(TokenTypePage(number=page_number + 1, labels=token_type_labels))

        return TokenTypeLabels(pages=token_type_pages)

    @staticmethod
    def loop_token_type_tokens(token_type_labels: TokenTypeLabels):
        for token_type_page in token_type_labels.pages:
            for token_type_label in token_type_page.labels:
                yield token_type_page, token_type_label
