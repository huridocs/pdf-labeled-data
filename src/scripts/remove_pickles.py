import os
from os.path import join, exists

from config import PDF_FEATURES_PICKLE_NAME, FEATURES_PICKLE_NAME, LABELED_DATA_DESTINATION


def loop_xmls():
    for dataset_type_name in os.listdir(join(LABELED_DATA_DESTINATION, "token_type")):
        dataset_path = join(LABELED_DATA_DESTINATION, "token_type", dataset_type_name)
        if not os.path.isdir(dataset_path):
            continue
        for xml_name in sorted(os.listdir(dataset_path)):
            yield dataset_type_name, join(dataset_path, xml_name), xml_name


def remove_pickles():
    to_remove = [PDF_FEATURES_PICKLE_NAME, FEATURES_PICKLE_NAME]
    for dataset_type_name, xml_folder_path, xml_name in loop_xmls():
        pickle_paths = [join(xml_folder_path, x) for x in to_remove]
        for pickle_path in pickle_paths:
            if exists(pickle_path):
                os.remove(pickle_path)


if __name__ == "__main__":
    remove_pickles()
