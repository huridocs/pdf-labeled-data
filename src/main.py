import json
import logging
import os
import shutil
from os.path import exists, join
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse

from api.app.Annotation import Annotation
from api.app.LabelColor import LabelColor
from api.app.Pages import Pages
from api.app.PdfStatus import PdfStatus
from api.app.PdfAnnotations import PdfAnnotation
from api.app.utils import StackdriverJsonFormatter

IN_PRODUCTION = os.getenv("IN_PRODUCTION", "dev")

LABELED_DATA_PATH = Path(join("/", "labeled_data"))
PDFS_PATH = Path(join("/", "pdfs"))

handlers = None

if IN_PRODUCTION == "prod":
    json_handler = logging.StreamHandler()
    json_handler.setFormatter(StackdriverJsonFormatter())
    handlers = [json_handler]

logging.basicConfig(level=os.environ.get("LOG_LEVEL", default=logging.INFO), handlers=handlers)
logger = logging.getLogger("uvicorn")

# boto3 logging is _super_ verbose.
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("nose").setLevel(logging.CRITICAL)
logging.getLogger("s3transfer").setLevel(logging.CRITICAL)

app = FastAPI()


def update_status_json(status_path: str, sha: str, status_type: str, status_value: bool):
    status_folder = "/".join(status_path.split("/")[:-1])
    if not exists(status_folder):
        os.mkdir(status_folder)

    status_dict = dict()
    if exists(status_path):
        with open(status_path, "r") as st:
            status_dict = json.load(st)

    if sha in status_dict and not status_value:
        del status_dict[sha]
    else:
        status_dict[sha] = {status_type: status_value}

    with open(status_path, "w") as st:
        json.dump(status_dict, st)


@app.get("/", status_code=204)
def read_root():
    """
    Skiff's sonar, and the Kubernetes health check, require
    that the server returns a 2XX response from it's
    root URL, so it can tell the service is ready for requests.
    """
    return Response(status_code=204)


def valid_folder(dataset_path):
    if os.path.isdir(dataset_path):
        return True

    return False


def remove_active_datasets():
    for task_name in os.listdir(LABELED_DATA_PATH):
        active_dataset_path = join(LABELED_DATA_PATH, task_name, "active_dataset.txt")
        if exists(active_dataset_path):
            os.remove(active_dataset_path)


def exists_active_dataset():
    for task_name in os.listdir(LABELED_DATA_PATH):
        active_dataset_path = join(LABELED_DATA_PATH, task_name, "active_dataset.txt")
        if exists(active_dataset_path):
            return True
    return False


@app.get("/api/annotation/datasets/{task}")
async def get_datasets(task: str = None) -> list[str]:
    path = get_task_folder_path(task)
    datasets = [dataset for dataset in os.listdir(path) if valid_folder(join(path, dataset))]

    if datasets:
        return datasets

    return ["No datasets"]


@app.post("/api/annotation/active_dataset/{task}/{dataset}")
async def post_active_dataset(task: str = None, dataset: str = None):
    remove_active_datasets()
    path = get_task_folder_path(task)
    path_active_dataset = Path(join(path, "active_dataset.txt"))
    path_active_dataset.write_text(dataset)
    os.chmod(path_active_dataset, 0o777)
    return {}


@app.get("/api/annotation/active_task")
async def get_active_task() -> str:
    for task in os.listdir(LABELED_DATA_PATH):
        path = get_task_folder_path(task)
        if exists(Path(join(path, "active_dataset.txt"))):
            return task

    return os.listdir(LABELED_DATA_PATH)[0]


@app.get("/api/annotation/active_dataset")
async def get_active_dataset() -> str:
    for task in os.listdir(LABELED_DATA_PATH):
        path = get_task_folder_path(task)
        if exists(Path(join(path, "active_dataset.txt"))) and Path(join(path, "active_dataset.txt")).read_text():
            return Path(join(path, "active_dataset.txt")).read_text()

    return "No datasets"


@app.get("/api/pdf/{name}")
async def get_pdf(name: str):
    pdf_path = join(PDFS_PATH, name, f"document.pdf")
    pdf_exists = os.path.exists(pdf_path)
    if not pdf_exists:
        raise HTTPException(status_code=404, detail=f"pdf {name} not found.")

    return FileResponse(pdf_path, media_type="application/pdf")


@app.post("/api/pdf/{task}/{dataset}/{name}/delete")
def delete_pdf_junk(task: str, dataset: str, name: str):
    for pdf_name, pdf_folder_path in loop_pdfs(task, dataset):
        if pdf_name != name:
            continue

        status_path = Path(join(pdf_folder_path, "status.txt"))
        junk = exists(status_path) and "junk" == status_path.read_text()

        if junk:
            shutil.rmtree(pdf_folder_path)

    return {}


@app.post("/api/pdfs/{task}/{dataset}/delete/all/junk")
def delete_all_junk(task: str, dataset: str):
    for pdf_name, pdf_folder_path in loop_pdfs(task, dataset):
        status_path = Path(join(pdf_folder_path, "status.txt"))
        junk = exists(status_path) and "junk" == status_path.read_text()

        if junk:
            shutil.rmtree(pdf_folder_path)

    return {}


@app.post("/api/doc/{task}/{dataset}/{name}/finished/{finished}")
def set_pdf_finished(task: str, dataset: str, name: str, finished: bool):
    dataset_folder_path = join(get_task_folder_path(task), dataset)
    status_folder_path = Path(join(dataset_folder_path, name))
    if not exists(status_folder_path):
        return {}

    status_path = join(status_folder_path, "status.txt")
    if finished:
        Path(status_path).write_text("finished")
        return {}

    if not finished and exists(status_path):
        os.remove(status_path)

    return {}


@app.post("/api/doc/{task}/{dataset}/{name}/junk/{junk}")
def set_pdf_junk(task: str, dataset: str, name: str, junk: bool):
    dataset_folder_path = join(get_task_folder_path(task), dataset)
    status_folder_path = Path(join(dataset_folder_path, name))
    if not exists(status_folder_path):
        return {}

    status_file_path = join(status_folder_path, "status.txt")

    if junk:
        Path(status_file_path).write_text("junk")
        return {}

    if not junk and exists(status_file_path):
        os.remove(status_file_path)

    return {}


def get_labels_path(task: str, dataset: str, name: str):
    return join(LABELED_DATA_PATH, task, dataset, name, "labels.json")


@app.get("/api/pdf/{task}/{dataset}/{name}/annotations")
def get_annotations(task: str, dataset: str, name: str) -> PdfAnnotation:
    is_reading_order = task == "reading_order"
    labels_file_path = get_labels_path(task, dataset, name)

    if not exists(labels_file_path):
        return PdfAnnotation.get_empty_annotation()

    labels_definitions = get_labels_colors(task)
    pdf_annotation = PdfAnnotation.from_path(Path(labels_file_path), labels_definitions, is_reading_order)

    if pdf_annotation:
        return pdf_annotation

    return PdfAnnotation.get_empty_annotation()


@app.post("/api/doc/{task}/{dataset}/{name}/annotations")
def save_annotations(task: str, dataset: str, name: str, annotations: PdfAnnotation):
    is_reading_order = task == "reading_order"

    if is_reading_order:
        pass

    labels_file_path = get_labels_path(task, dataset, name)
    labels_colors = get_labels_colors(task)
    token_type_labels = annotations.to_token_type_labels(labels_colors=labels_colors)
    Path(labels_file_path).write_text(token_type_labels.model_dump_json(indent=4))
    os.chmod(labels_file_path, 0o777)
    return {}


@app.get("/api/pdf/{name}/tokens")
def get_tokens(name: str):
    pdf_tokens_path = os.path.join(PDFS_PATH, name, "etree.xml")
    if not os.path.exists(pdf_tokens_path):
        raise HTTPException(status_code=403, detail="No tokens for pdf.")

    return Pages.from_etree(pdf_tokens_path)


def get_labels_colors(task: str) -> list[LabelColor]:
    labels_path = Path(join(get_task_folder_path(task), "labels.json"))

    if not exists(labels_path):
        Path(labels_path).write_text('[{ "text": "No labels", "color": "#e6194b" }]')

    labels_colors = [LabelColor(**x) for x in json.loads(labels_path.read_text())]
    return labels_colors


@app.get("/api/annotation/{task}/labels")
def get_labels(task: str) -> list[LabelColor]:
    return get_labels_colors(task)


def get_task_folder_path(task):
    task = task if task else "token_type"
    return join(LABELED_DATA_PATH, task)


def loop_pdfs(task, dataset):
    dataset_folder_path = join(get_task_folder_path(task), dataset)
    if not os.path.isdir(dataset_folder_path):
        return []

    for pdf_name in sorted(os.listdir(dataset_folder_path)):
        pdf_folder_path = join(dataset_folder_path, pdf_name)
        if valid_folder(pdf_folder_path):
            yield pdf_name, pdf_folder_path


@app.get("/api/annotation/get_pdfs_statuses/{task}/{dataset}")
def get_pdfs_statuses(task: str, dataset: str) -> list[PdfStatus]:
    pdf_statuses: list[PdfStatus] = list()
    for pdf_name, pdf_folder_path in loop_pdfs(task, dataset):
        status_path = Path(join(pdf_folder_path, "status.txt"))
        finished = exists(status_path) and "finished" == status_path.read_text()
        junk = exists(status_path) and "junk" == status_path.read_text()
        pdf_statuses.append(PdfStatus(name=pdf_name, finished=finished, junk=junk))

    return pdf_statuses


@app.post("/api/annotation/reading_order/{dataset}/{name}/{position}")
def save_reading_order_annotation(dataset: str, name: str, position: int, annotation: Annotation) -> PdfAnnotation:
    labels_file_path = get_labels_path("reading_order", dataset, name)

    pdf_tokens_path = os.path.join(PDFS_PATH, name, "etree.xml")
    pages = Pages.from_etree(pdf_tokens_path)

    labels_colors = get_labels_colors("reading_order")
    pdf_annotations = PdfAnnotation.from_path(Path(labels_file_path), labels_colors, True)

    pdf_annotations = pdf_annotations.get_reordered_pdf_annotation_by_position(pages, annotation, position)

    token_type_labels = pdf_annotations.to_token_type_labels(labels_colors=labels_colors, is_reading_order=True)
    Path(labels_file_path).write_text(token_type_labels.model_dump_json(indent=4))
    return pdf_annotations


@app.post("/api/annotations/reading_order/{dataset}/{name}")
def save_reading_order_annotations(dataset: str, name: str, annotation: Annotation) -> PdfAnnotation:
    labels_file_path = get_labels_path("reading_order", dataset, name)

    pdf_tokens_path = os.path.join(PDFS_PATH, name, "etree.xml")
    pages = Pages.from_etree(pdf_tokens_path)

    labels_colors = get_labels_colors("reading_order")
    pdf_annotations = PdfAnnotation.from_path(Path(labels_file_path), labels_colors, True)

    pdf_annotations = pdf_annotations.get_reordered_pdf_annotations(pages, annotation)

    token_type_labels = pdf_annotations.to_token_type_labels(labels_colors=labels_colors, is_reading_order=True)
    Path(labels_file_path).write_text(token_type_labels.model_dump_json(indent=4))

    return pdf_annotations
