import os
import sys
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from os import listdir
from os.path import join, exists
from pathlib import Path
from config import PROJECT_PATH, ROOT_PATH, PDF_NAME

PDFS_SOURCE = join(PROJECT_PATH, "ml_pdf_editor", "pdf_files")
PDFS_DESTINATION = join(ROOT_PATH, "pdfs")
LABELED_DATA_BASE_DIR = "token_type"


def loop_files():
    labeled_data_base_path: Path = Path(join("labeled_data", LABELED_DATA_BASE_DIR))
    for dataset in sorted(listdir(labeled_data_base_path)):
        if ".json" in dataset:
            continue
        dataset_path: Path = Path(join(labeled_data_base_path, dataset))
        for file_folder in sorted(listdir(dataset_path)):
            yield file_folder


def import_pdf():
    for file_folder in loop_files():
        pdf_source_path: Path = Path(join(PDFS_SOURCE, file_folder + ".pdf"))
        pdf_destination_folder: Path = Path(join(PDFS_DESTINATION, file_folder))

        if not exists(pdf_destination_folder):
            os.makedirs(pdf_destination_folder, exist_ok=True)

        pdf_destination_path: Path = Path(join(pdf_destination_folder, PDF_NAME))
        shutil.copy(pdf_source_path, pdf_destination_path)


if __name__ == "__main__":
    import_pdf()
