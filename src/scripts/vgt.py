import json
from os import listdir
from pathlib import Path

import requests
from pdf_features.PdfFeatures import PdfFeatures
from pdf_features.Rectangle import Rectangle
from sklearn.metrics import accuracy_score
from tqdm import tqdm

from config import ROOT_PATH

def loop_pdf_files():
    for toc_pdf_name in tqdm(listdir(Path(ROOT_PATH, "labeled_data","table_of_content","dataset_1"))):
        if toc_pdf_name in ['11903', "6841", "3427"]:
            continue

        poppler_etree = Path(ROOT_PATH, "pdfs", toc_pdf_name,"etree.xml")
        labels_path = Path(ROOT_PATH, "labeled_data","table_of_content","dataset_1", toc_pdf_name, "labels.json")
        pdf_path = Path(ROOT_PATH, "pdfs", toc_pdf_name, "document.pdf")
        yield str(poppler_etree), str(labels_path), str(pdf_path)


def set_labels(pdf_features: PdfFeatures, pdf_name):
    content = Path(ROOT_PATH, "downloads" , pdf_name + ".json").read_text()
    toc = json.loads(content)
    for page, token in pdf_features.loop_tokens():
        token.prediction = 6
        for title in toc:
            if token.page_number != int(title["bounding_box"]["page"]):
                continue
            bounding_box = Rectangle.from_width_height(
                left=title["bounding_box"]["left"],
                top=title["bounding_box"]["top"],
                width=title["bounding_box"]["width"],
                height=title["bounding_box"]["height"],
            )
            if bounding_box.get_intersection_percentage(token.bounding_box) > 0:
                token.prediction = 5
                break

def get_labeled_data():
    pdfs_features = list()

    for poppler_etree, labels_path, pdf_path in loop_pdf_files():
        pdf_features = PdfFeatures.from_poppler_etree(str(poppler_etree))
        pages_labels = pdf_features.load_labels(str(labels_path))
        for page in pages_labels.pages:
            for label in page.labels:
                label.label_type = 5
        pdf_features.set_token_types(pages_labels)
        set_labels(pdf_features, Path(labels_path).parent.name)
        pdfs_features.append(pdf_features)
    return pdfs_features


def get_prediction(fast: bool):
    for poppler_etree, labels_path, pdf_path in loop_pdf_files():
        if fast:
            toc_path = Path(ROOT_PATH, "downloads", Path(labels_path).parent.name + '.json')
        else:
            toc_path = Path(ROOT_PATH, "downloads", "vgt" + Path(labels_path).parent.name + '.json')

        if toc_path.exists():
            continue

        with open(pdf_path, "rb") as stream:
            files = {"file": stream}
            data = {"fast": fast}
            response = requests.post(f"http://localhost:5060/toc", files=files, data=data)
            toc_path.write_text(json.dumps(response.json()))

def get_benchmark():
    pdfs_features = get_labeled_data()
    truth = []
    prediction = []
    for pdf_features in pdfs_features:
        for page, token in pdf_features.loop_tokens():
            prediction.append(token.prediction)
            truth.append(token.token_type.get_index())

    print(accuracy_score(truth, prediction))

def get_wrong_tocs():
    for poppler_etree, labels_path, pdf_path in loop_pdf_files():
        file = Path(labels_path).parent.name
        try:
            content = Path(ROOT_PATH, "downloads", file + '.json').read_text()
            loads = json.loads(content)
            if type(loads) != list:
                raise Exception('buuuh')
        except:
            print("error", file)

if __name__ == '__main__':
    get_prediction(False)

