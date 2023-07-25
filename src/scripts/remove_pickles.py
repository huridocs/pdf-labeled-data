import os
from os.path import join, exists

from config import PDF_FEATURES_PICKLE_NAME, FEATURES_PICKLE_NAME
from src.scripts.import_token_type import loop_xmls


def remove_pickles():
    to_remove = [PDF_FEATURES_PICKLE_NAME, FEATURES_PICKLE_NAME]
    for dataset_type_name, xml_folder_path, xml_name in loop_xmls():
        pickle_paths = [join(xml_folder_path, x) for x in to_remove]
        for pickle_path in pickle_paths:
            if exists(pickle_path):
                os.remove(pickle_path)


if __name__ == '__main__':
    remove_pickles()
