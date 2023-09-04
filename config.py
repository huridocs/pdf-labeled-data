from os.path import join
from pathlib import Path

ROOT_PATH = Path(__file__).parent
PROJECT_PATH = ROOT_PATH.parent
XML_NAME = "etree.xml"
LABELS_FILE_NAME = "labels.json"
PDF_FEATURES_PICKLE_NAME = "pdf_features.pickle"
FEATURES_PICKLE_NAME = "features.pickle"
PDF_NAME = "document.pdf"

LABELED_DATA_SOURCE = join(PROJECT_PATH, "ml_pdf_editor", "labeled_xmls_poppler")
LABELED_TOC_DATA_SOURCE = join(PROJECT_PATH, "ml_pdf_web_editor", "skiff_files", "apps", "pawls", "ali_labels")
LABELED_XML_DESTINATION = join(ROOT_PATH, "pdfs")
LABELED_DATA_DESTINATION = join(ROOT_PATH, "labeled_data")
