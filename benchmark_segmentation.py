import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from statistics import mode

from py_markdown_table.markdown_table import markdown_table

from pdf_annotate import PdfAnnotator, Location, Appearance
from pdf_features.Rectangle import Rectangle
from pdf_token_type_labels.Label import Label
from pdf_token_type_labels.PdfLabels import PdfLabels
from pydantic import BaseModel

PDFS_PATH = "pdfs"
SEGMENTATION_DATASET_PATH = "labeled_data/benchmark_segmentation/dataset"


class ResultType(StrEnum):
    CORRECT = "CORRECT"
    MISTAKE = "MISTAKE"
    NOT_FOUND_LABEL = "NOT FOUND LABEL"
    WRONG_TOKEN_TYPE = "WRONG TOKEN TYPE"
    FOUND_LABEL = "FOUND LABEL"


@dataclass
class ResultBox:
    page_number: int
    page_width: int
    page_height: int
    segment_type: str
    result_type: ResultType
    bounding_box: Rectangle


@dataclass
class PredictionBox:
    text: str
    segment_type: str
    bounding_box: Rectangle

    def __hash__(self):
        return hash((self.text, self.segment_type, self.bounding_box))

    @staticmethod
    def from_box_json(box_json: dict):
        bounding_box = Rectangle.from_width_height(box_json["left"], box_json["top"], box_json["width"], box_json["height"])
        return PredictionBox(text=box_json["text"], segment_type=box_json["type"], bounding_box=bounding_box)


@dataclass
class LabelBox:
    bounding_box: Rectangle
    label_type: int

    def __hash__(self):
        return hash((self.bounding_box, self.label_type))

    @staticmethod
    def from_label(label: Label):
        bounding_box = Rectangle.from_width_height(label.left, label.top, label.width, label.height)
        return LabelBox(bounding_box, label.label_type)


class BenchmarkResult(BaseModel):
    document_name: str
    model: str
    labels: int
    not_found_labels: int
    wrong_segmentation: int
    wrong_token_type: int
    mistakes: int
    accuracy: float


old_types_to_doclaynet_types = {
    "FORMULA": "Formula",
    "FOOTNOTE": "Footnote",
    "LIST": "List item",
    "TABLE": "Table",
    "FIGURE": "Picture",
    # "TITLE": "Title",
    "TEXT": "Text",
    "HEADER": "Page header",
    "TITLE": "Section header",
    "IMAGE_CAPTION": "Caption",
    "FOOTER": "Page footer",
}


label_no_to_label = {
    0: "Formula",
    1: "Footnote",
    2: "List item",
    3: "Table",
    4: "Picture",
    5: "Title",
    6: "Text",
    7: "Page header",
    8: "Section header",
    9: "Caption",
    10: "Page footer",
}


def add_annotation(annotator: PdfAnnotator, result_box: ResultBox, text: str = "", color: tuple = ()):
    if not color:
        if result_box.result_type == ResultType.FOUND_LABEL:
            color = (70 / 255, 139 / 255, 242 / 255, 1)
        elif result_box.result_type == ResultType.CORRECT:
            color = (92 / 255, 191 / 255, 95 / 255, 1)
        elif result_box.result_type == ResultType.MISTAKE:
            color = (227 / 255, 9 / 255, 56 / 255, 1)
        elif result_box.result_type == ResultType.WRONG_TOKEN_TYPE:
            color = (179 / 255, 194 / 255, 17 / 255, 1)
        elif result_box.result_type == ResultType.NOT_FOUND_LABEL:
            color = (158 / 255, 50 / 255, 217 / 255, 1)

    left, top, right, bottom = (
        result_box.bounding_box.left,
        result_box.page_height - result_box.bounding_box.top,
        result_box.bounding_box.right,
        result_box.page_height - result_box.bounding_box.bottom,
    )

    if not text:
        text = result_box.segment_type + " | " + result_box.result_type.value
    text_box_size = len(text) * 5 + 8

    annotator.add_annotation(
        "square",
        Location(x1=left, y1=bottom, x2=right, y2=top, page=result_box.page_number - 1),
        Appearance(stroke_color=color),
    )

    if result_box.result_type in {ResultType.FOUND_LABEL, ResultType.NOT_FOUND_LABEL}:
        left = right - left
        # top = top + 10

    annotator.add_annotation(
        "square",
        Location(x1=left, y1=top, x2=left + text_box_size, y2=top + 10, page=result_box.page_number - 1),
        Appearance(fill=color),
    )

    annotator.add_annotation(
        "text",
        Location(x1=left, y1=top, x2=left + text_box_size, y2=top + 10, page=result_box.page_number - 1),
        Appearance(content=text, font_size=8, fill=(1, 1, 1), stroke_width=3),
    )


def create_result_boxes(
    found_labels: set,
    correct_predictions: set,
    not_found_labels: set,
    mistakes: set,
    wrong_token_types: set,
    predictions_to_skip: list,
    page_number: int,
    page_height: int,
) -> list[ResultBox]:
    result_boxes: list[ResultBox] = []

    # Found labels
    result_boxes.extend(
        [
            ResultBox(
                page_number, 0, page_height, label_no_to_label[label.label_type], ResultType.FOUND_LABEL, label.bounding_box
            )
            for label in found_labels
        ]
    )

    # Correct predictions
    result_boxes.extend(
        [
            ResultBox(page_number, 0, page_height, prediction.segment_type, ResultType.CORRECT, prediction.bounding_box)
            for prediction in correct_predictions
        ]
    )

    # Not found labels
    result_boxes.extend(
        [
            ResultBox(
                page_number,
                0,
                page_height,
                label_no_to_label[label.label_type],
                ResultType.NOT_FOUND_LABEL,
                label.bounding_box,
            )
            for label in not_found_labels
        ]
    )

    # Wrong predictions
    result_boxes.extend(
        [
            ResultBox(page_number, 0, page_height, prediction.segment_type, ResultType.MISTAKE, prediction.bounding_box)
            for prediction in mistakes
            if prediction not in predictions_to_skip
        ]
    )

    # Wrong token types
    result_boxes.extend(
        [
            ResultBox(
                page_number, 0, page_height, prediction.segment_type, ResultType.WRONG_TOKEN_TYPE, prediction.bounding_box
            )
            for prediction in wrong_token_types
            if prediction not in predictions_to_skip
        ]
    )

    return result_boxes


def get_intersecting_elements(source_elements: list, target_elements: list, intersection_threshold: int = 20) -> dict:
    intersection_map = {}
    for source in source_elements:
        intersected = [
            target
            for target in target_elements
            if target.bounding_box.get_intersection_percentage(source.bounding_box) > intersection_threshold
            or source.bounding_box.get_intersection_percentage(target.bounding_box) > 90
        ]
        intersection_map[source] = intersected
    return intersection_map


def check_overlapping_elements(label_to_predictions: dict, prediction_to_labels: dict) -> tuple[set, set]:
    not_found_labels = set()
    wrong_predictions = set()

    for label, predictions in label_to_predictions.items():
        if len(predictions) < 2:
            continue
        for prediction in predictions:
            if len(prediction_to_labels[prediction]) > 1:
                not_found_labels.add(label)
                wrong_predictions.add(prediction)

    return not_found_labels, wrong_predictions


def get_allowed_types(label_type: int) -> set[str]:
    if label_type in {5, 8}:
        return {"Section header", "Title"}
    elif label_type == 6:
        return {"Text", "List item"}
    return set()


def process_label_to_predictions(
    label: LabelBox, predictions: list[PredictionBox], not_found_labels: set
) -> tuple[set, set, set, set]:
    if not predictions:
        not_found_labels.add(label)
        return set(), set(), set(), set()

    allowed_types = get_allowed_types(label.label_type)
    if mode([p.segment_type for p in predictions]) not in allowed_types:
        not_found_labels.add(label)
        return set(), set(), set(), set(predictions)

    merged_bounding_box = Rectangle.merge_rectangles([p.bounding_box for p in predictions])
    if merged_bounding_box.get_intersection_percentage(label.bounding_box) > 50:
        return {label}, set(predictions), set(), set()

    not_found_labels.add(label)
    return set(), set(), set(predictions), set()


def process_prediction_to_labels(
    prediction: PredictionBox,
    labels: list[LabelBox],
    not_found_labels: set,
) -> tuple[set, set, set, set]:
    if not labels:
        return set(), set(), {prediction}, set()

    allowed_types = get_allowed_types(labels[0].label_type)
    if prediction.segment_type not in allowed_types:
        not_found_labels.update(labels)
        return set(), set(), set(), {prediction}

    merged_bounding_box = Rectangle.merge_rectangles([l.bounding_box for l in labels])
    if merged_bounding_box.get_intersection_percentage(prediction.bounding_box) > 50:
        # if prediction.bounding_box.get_intersection_percentage(merged_bounding_box) > 50:
        return set(labels), {prediction}, set(), set()

    not_found_labels.update(labels)
    return set(), set(), {prediction}, set()


def get_predictions_to_skip(label_to_predictions, prediction_to_labels, predictions):
    predictions_to_skip = [p for p in predictions if len(prediction_to_labels[p]) == 0]
    for predictions_in_label in label_to_predictions.values():
        to_remove = []
        for p in predictions_to_skip:
            if p in predictions_in_label:
                to_remove.append(p)
        for p in to_remove:
            predictions_to_skip.remove(p)
    return predictions_to_skip


def benchmark_single_page(page_labels: list[LabelBox], predictions: list[PredictionBox], page_number: int, page_height: int):
    if not page_labels:
        return []

    found_labels: set[LabelBox] = set()
    not_found_labels: set[LabelBox] = set()
    correct_predictions: set[PredictionBox] = set()
    mistakes: set[PredictionBox] = set()
    wrong_token_types: set[PredictionBox] = set()

    label_to_predictions = get_intersecting_elements(page_labels, predictions)
    prediction_to_labels = get_intersecting_elements(predictions, page_labels)

    initial_not_found, initial_wrong = check_overlapping_elements(label_to_predictions, prediction_to_labels)
    not_found_labels.update(initial_not_found)
    mistakes.update(initial_wrong)

    for label in page_labels:
        if label in not_found_labels:
            continue
        if not label_to_predictions[label]:
            not_found_labels.add(label)
        if len(label_to_predictions[label]) < 2:
            continue
        found, correct, _mistakes, wrong_type = process_label_to_predictions(
            label, label_to_predictions[label], not_found_labels
        )
        found_labels.update(found)
        correct_predictions.update(correct)
        mistakes.update(_mistakes)
        wrong_token_types.update(wrong_type)

    for prediction in predictions:
        if prediction in mistakes or prediction in correct_predictions:
            continue
        found, correct, mistake, wrong_type = process_prediction_to_labels(
            prediction, prediction_to_labels[prediction], not_found_labels
        )
        found_labels.update(found)
        correct_predictions.update(correct)
        mistakes.update(mistake)
        wrong_token_types.update(wrong_type)

    predictions_to_skip = get_predictions_to_skip(label_to_predictions, prediction_to_labels, predictions)

    return create_result_boxes(
        found_labels,
        correct_predictions,
        not_found_labels,
        mistakes,
        wrong_token_types,
        predictions_to_skip,
        page_number,
        page_height,
    )


def benchmark_a_document(predictions_path: Path, save_visualizations: bool = True, model_name: str = "docling"):
    document_name = predictions_path.name.replace(".json", "")
    document_labels_path = Path(SEGMENTATION_DATASET_PATH, document_name, "labels.json")
    if not document_labels_path.exists():
        print(f"Label does not exist for: {predictions_path.name}")
        return []
    pdf_labels = PdfLabels(**json.loads(document_labels_path.read_text()))
    predictions = json.load(predictions_path.open())
    result_boxes: list[ResultBox] = []
    for page in pdf_labels.pages:
        predictions_in_page = [p for p in predictions if p["page_number"] == page.number]
        page_height = predictions_in_page[0]["page_height"]
        prediction_boxes: list[PredictionBox] = [PredictionBox.from_box_json(p) for p in predictions_in_page]
        page_labels = [l for l in page.labels if l.label_type in {5, 6, 8}]
        page_label_boxes = [LabelBox.from_label(label) for label in page_labels]
        page_result_boxes = benchmark_single_page(page_label_boxes, prediction_boxes, page.number, page_height)
        result_boxes.extend(page_result_boxes)

    if save_visualizations:
        pdf_path = Path(PDFS_PATH, document_name, "document.pdf")
        annotator = PdfAnnotator(str(pdf_path))
        for result_box in result_boxes:
            add_annotation(annotator, result_box)
        output_model_path = Path("results", model_name)
        if not output_model_path.exists():
            output_model_path.mkdir(exist_ok=True)
        output_pdf_path = Path(output_model_path, document_name + ".pdf")
        annotator.write(output_pdf_path)
    return result_boxes


def get_benchmark_result(document_name: str, model: str, result_boxes: list[ResultBox]):
    labels = len([r for r in result_boxes if r.result_type in {ResultType.FOUND_LABEL, ResultType.NOT_FOUND_LABEL}])
    not_found_labels = len([r for r in result_boxes if r.result_type == ResultType.NOT_FOUND_LABEL])
    wrong_segmentation = len([r for r in result_boxes if r.result_type == ResultType.MISTAKE])
    wrong_token_type = len([r for r in result_boxes if r.result_type == ResultType.WRONG_TOKEN_TYPE])
    mistakes = wrong_segmentation + wrong_token_type + not_found_labels
    accuracy = round((labels - mistakes) / labels * 100, 2) if labels else 0
    return BenchmarkResult(
        document_name=document_name,
        model=model,
        labels=labels,
        not_found_labels=not_found_labels,
        wrong_segmentation=wrong_segmentation,
        wrong_token_type=wrong_token_type,
        mistakes=mistakes,
        accuracy=accuracy,
    )


def get_average(benchmark_results: list[BenchmarkResult], model: str):
    labels = sum([r.labels for r in benchmark_results])
    not_found_labels = sum([r.not_found_labels for r in benchmark_results])
    wrong_segmentation = sum([r.wrong_segmentation for r in benchmark_results])
    wrong_token_type = sum([r.wrong_token_type for r in benchmark_results])
    mistakes = sum([r.mistakes for r in benchmark_results])
    accuracy = round((labels - mistakes) / labels * 100, 2)
    return BenchmarkResult(
        document_name="Average",
        model=model,
        labels=labels,
        not_found_labels=not_found_labels,
        wrong_segmentation=wrong_segmentation,
        wrong_token_type=wrong_token_type,
        mistakes=mistakes,
        accuracy=accuracy,
    )


def benchmark(predictions_dir: Path, model: str = "docling", save_visualizations: bool = True):
    benchmark_results: list[BenchmarkResult] = []
    for prediction_path in predictions_dir.iterdir():
        result_boxes = benchmark_a_document(prediction_path, save_visualizations, model)
        if not result_boxes:
            continue
        document_name = prediction_path.name.replace(".json", "")
        benchmark_results.append(get_benchmark_result(document_name, model, result_boxes))
    benchmark_results.sort(key=lambda x: x.document_name)
    benchmark_results.append(get_average(benchmark_results, model))
    markdown = markdown_table([x.model_dump() for x in benchmark_results]).set_params(padding_width=5).get_markdown()
    markdown_output_path: Path = Path("results", model + ".md")
    markdown_output_path.write_text(markdown)
    print(markdown)


if __name__ == "__main__":
    predictions_dir = Path("/path/to/lightgbm_jsons")
    benchmark(predictions_dir, "lightgbm")
