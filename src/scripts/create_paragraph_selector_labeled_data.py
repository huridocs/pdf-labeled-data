import os
import re
import shutil
from os import listdir
from os.path import join, exists
from pathlib import Path
from time import time

from pdf_features.PdfFeatures import PdfFeatures
from pdf_features.PdfPage import PdfPage
from tqdm import tqdm

from config import PROJECT_PATH, LABELED_XML_DESTINATION, PDF_NAME, LABELED_DATA_DESTINATION


def loop_pdfs():
    pdfs_paths = join(PROJECT_PATH, "uwazi", "uploaded_documents")
    for pdf_name in tqdm(listdir(pdfs_paths)):
        if ".pdf" not in pdf_name:
            continue

        yield Path(join(pdfs_paths, pdf_name)), pdf_name


def get_text(page: PdfPage):
    return " ".join([token.content for token in page.tokens])


def it_matches(pdf_path):
    pdf_features = PdfFeatures.from_pdf_path(pdf_path)
    page_text = get_text(pdf_features.pages[0])
    matches_2 = re.findall(r"A/HRC", page_text)

    if not matches_2:
        return False

    matches_1 = re.findall(r"\d/\d", page_text)
    if len(matches_1) < 2:
        return False

    return True


def check_pdfs():
    pdfs_titles = list()
    for pdf_path, pdf_name in loop_pdfs():
        if not it_matches(pdf_path):
            continue

        pdf_new_path = join(LABELED_XML_DESTINATION, pdf_name.replace(".pdf", ""), PDF_NAME)

        if not exists(pdf_new_path):
            os.makedirs(Path(pdf_new_path).parent, exist_ok=True)
            shutil.copyfile(pdf_path, pdf_new_path)

        xml_path = join(LABELED_DATA_DESTINATION, "paragraph_selector", "rightdocs_titles", pdf_name.replace(".pdf", ""))
        if not exists(xml_path):
            os.makedirs(xml_path, exist_ok=True)
        pdfs_titles.append(pdf_name)

    print(pdfs_titles)
    print(len(pdfs_titles))


if __name__ == "__main__":
    print("start")
    start = time()
    check_pdfs()
    print("finished in", round(time() - start, 1), "seconds")
