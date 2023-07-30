import json
import logging
import os
from os.path import exists, join
from pathlib import Path
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.responses import FileResponse

from api.app.Label import Label
from api.app.Pages import Pages
from api.app.PdfStatus import PdfStatus
from api.app.PdfAnnotations import PdfAnnotation
from api.app.Annotation import Annotation
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


def get_object_from_file(path: str):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)

    return None


@app.post("/api/annotation/reading_order/{task}/{sha}/{position}")
def reorder_annotation(
        task: str, sha: str, position: int, annotation: Annotation, x_auth_request_email: str = Header(None)
) -> PdfAnnotation:
    # user = get_user_from_header(x_auth_request_email)
    #
    # base_path = configuration.output_directory
    # pdf_annotations_dict = get_object_from_file(os.path.join(base_path, task, sha, f"{user}_annotations.json"))
    # pages = get_object_from_file(os.path.join(base_path, task, sha, "pdf_structure.json"))
    #
    # if not pdf_annotations_dict or not pages:
    #     raise HTTPException(status_code=404, detail="No reading order available")
    #
    # pdf_annotation = PdfAnnotation(**pdf_annotations_dict)
    # tokens_to_reorder = annotation.get_tokens(pages)
    # pdf_annotation = pdf_annotation.get_reordered_pdf_annotation_by_position(tokens_to_reorder[0], position)
    # pdf_annotation.save(os.path.join(configuration.output_directory, task, sha, f"{user}_annotations.json"))
    return {}


@app.post("/api/annotation/reading_order/{task}/{sha}")
def reorder_annotations(
        task: str, sha: str, annotation: Annotation, x_auth_request_email: str = Header(None)
) -> PdfAnnotation:
    # user = get_user_from_header(x_auth_request_email)
    #
    # base_path = configuration.output_directory
    # pdf_annotations_dict = get_object_from_file(os.path.join(base_path, task, sha, f"{user}_annotations.json"))
    # pages = get_object_from_file(os.path.join(base_path, task, sha, "pdf_structure.json"))
    #
    # if not pdf_annotations_dict or not pages:
    #     raise HTTPException(status_code=404, detail="No reading order available")
    #
    # pdf_annotation = PdfAnnotation(**pdf_annotations_dict)
    # tokens_to_reorder = annotation.get_tokens(pages)
    # reordered_pdf_annotation = pdf_annotation.get_reordered_pdf_annotation(tokens_to_reorder)
    # reordered_pdf_annotation.save(os.path.join(configuration.output_directory, task, sha, f"{user}_annotations.json"))
    return {}


@app.get("/", status_code=204)
def read_root():
    """
    Skiff's sonar, and the Kubernetes health check, require
    that the server returns a 2XX response from it's
    root URL, so it can tell the service is ready for requests.
    """
    return Response(status_code=204)


def valid_folder(dataset_path):
    if os.path.isdir(dataset_path) and os.listdir(dataset_path):
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


@app.get("/api/annotation/real_datasets/{task}")
async def get_real_datasets(task: str = None) -> List[str]:
    path = get_task_folder_path(task)
    datasets = [dataset for dataset in os.listdir(path) if valid_folder(join(path, dataset))]
    if not exists_active_dataset():
        active_dataset = datasets[0]
        remove_active_datasets()
        Path(join(path, "active_dataset.txt")).write_text(active_dataset)

    return datasets


@app.post("/api/annotation/real_active_dataset/{task}/{dataset}")
async def post_real_datasets(task: str = None, dataset: str = None):
    path = get_task_folder_path(task)
    remove_active_datasets()
    Path(join(path, "active_dataset.txt")).write_text(dataset)
    return {}


@app.get("/api/annotation/real_active_task")
async def get_real_active_task() -> str:
    for task in os.listdir(LABELED_DATA_PATH):
        path = get_task_folder_path(task)
        if exists(Path(join(path, "active_dataset.txt"))):
            return await lower_snake_case_to_title_case(task)

    return await lower_snake_case_to_title_case(os.listdir(LABELED_DATA_PATH)[0])


async def lower_snake_case_to_title_case(task):
    return " ".join([x[0].upper() + x[1:] for x in task.split("_")])


@app.get("/api/annotation/real_active_dataset")
async def get_real_active_dataset() -> str:
    for task in os.listdir(LABELED_DATA_PATH):
        path = get_task_folder_path(task)
        if exists(Path(join(path, "active_dataset.txt"))):
            return Path(join(path, "active_dataset.txt")).read_text()

    return ""


@app.get("/api/pdf/{name}")
async def get_pdf(name: str):
    pdf_path = join(PDFS_PATH, name, f"document.pdf")
    pdf_exists = os.path.exists(pdf_path)
    if not pdf_exists:
        raise HTTPException(status_code=404, detail=f"pdf {name} not found.")

    return FileResponse(pdf_path, media_type="application/pdf")


@app.post("/api/doc/{task}/{sha}/delete")
def delete_pdf_junk(task: str, sha: str, x_auth_request_email: str = Header(None)):
    # user = get_user_from_header(x_auth_request_email)
    # status_path = os.path.join(configuration.output_directory, task, "status", f"{user}.json")
    # exists = os.path.exists(status_path)
    # if not exists:
    #     # Not an allocated user. Do nothing.
    #     return {}
    #
    # shutil.rmtree(os.path.join(configuration.output_directory, task, sha))
    return {}


# @app.post("/api/doc/{task}/delete/all/junk")
# def delete_junk(task: str, dataset: str):
#     dataset_folder_path = join(get_task_folder_path(task), dataset)
#     status_path = Path(join(dataset_folder_path, name, "status.txt"))
#     if not exists(status_path):
#         return {}
#
#     if finished:
#         status_path.write_text("finished")
#         return {}
#
#     if not finished:
#         os.remove(status_path)
#
#     return {}


@app.post("/api/doc/{task}/{dataset}/{name}/finished/{finished}")
def set_pdf_finished(task: str, dataset: str, name: str, finished: bool):
    dataset_folder_path = join(get_task_folder_path(task), dataset)
    status_path = Path(join(dataset_folder_path, name))
    if not exists(status_path):
        return {}

    if finished:
        Path(join(status_path, 'status.txt')).write_text("finished")
        return {}

    if not finished:
        os.remove(join(status_path, 'status.txt'))

    return {}


@app.post("/api/doc/{task}/{dataset}/{name}/junk/{junk}")
def set_pdf_junk(task: str, dataset: str, name: str, junk: bool):
    dataset_folder_path = join(get_task_folder_path(task), dataset)
    status_path = Path(join(dataset_folder_path, name))
    if not exists(status_path):
        return {}

    if junk:
        Path(join(status_path, 'status.txt')).write_text("junk")
        return {}

    if not junk:
        os.remove(join(status_path, 'status.txt'))

    return {}


def get_labels_path(task: str, dataset: str, name: str):
    task_snake_case = task.lower().replace(" ", "_")
    labels_path = join(LABELED_DATA_PATH, task_snake_case, dataset, name, "labels.json")
    return labels_path


@app.get("/api/pdf/{task}/{dataset}/{name}/annotations")
def get_annotations(task: str, dataset: str, name: str) -> PdfAnnotation:

    labels_file_path = get_labels_path(task, dataset, name)

    if not exists(labels_file_path):
        return PdfAnnotation.get_empty_annotation()

    labels_definitions = get_labels_definition(task)
    annotation = PdfAnnotation.from_path(Path(labels_file_path), labels_definitions)

    if annotation:
        return annotation

    return PdfAnnotation.get_empty_annotation()


@app.post("/api/doc/{task}/{dataset}/{name}/annotations")
def save_annotations(
        task: str,
        dataset: str,
        name: str,
        annotations: PdfAnnotation
):
    labels_file_path = get_labels_path(task, dataset, name)

    token_type_labels = annotations.to_token_type_labels()
    Path(labels_file_path).write_text(token_type_labels.model_dump_json(indent=4))
    os.chmod(labels_file_path , 0o777)
    return {}


@app.get("/api/pdf/{name}/tokens")
def get_tokens(name: str):
    pdf_tokens = os.path.join(PDFS_PATH, name, "etree.xml")
    if not os.path.exists(pdf_tokens):
        raise HTTPException(status_code=403, detail="No tokens for pdf.")

    return Pages.from_etree(pdf_tokens)


def get_labels_definition(task: str) -> List[Label]:
    labels_path = Path(join(get_task_folder_path(task), "labels.json"))

    if not exists(labels_path):
        Path(labels_path).write_text('[{ "text": "No labels", "color": "#e6194b" }]')

    labels = [Label(**x) for x in json.loads(labels_path.read_text())]
    return labels


@app.get("/api/annotation/{task}/labels")
def get_real_labels(task: str) -> List[Label]:
    return get_labels_definition(task)


def get_task_folder_path(task):
    task = task if task else "token_type"
    task_folder_name = join(task.replace(" ", "_").lower())
    return join(LABELED_DATA_PATH, task_folder_name)


def loop_pdfs(task, dataset):
    dataset_folder_path = join(get_task_folder_path(task), dataset)
    for pdf_name in sorted(os.listdir(dataset_folder_path)):
        pdf_folder_path = join(dataset_folder_path, pdf_name)
        if valid_folder(pdf_folder_path):
            yield pdf_name, pdf_folder_path


@app.get("/api/annotation/get_pdfs_statuses/{task}/{dataset}")
def get_pdfs_statuses(task: str, dataset: str) -> List[PdfStatus]:
    pdf_statuses: List[PdfStatus] = list()
    for pdf_name, pdf_folder__path in loop_pdfs(task, dataset):
        status_path = Path(join(pdf_folder__path, "status.txt"))
        finished = exists(status_path) and "finished" == status_path.read_text()
        junk = exists(status_path) and "junk" == status_path.read_text()
        pdf_statuses.append(PdfStatus(name=pdf_name, finished=finished, junk=junk))

    return pdf_statuses
