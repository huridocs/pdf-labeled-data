from typing import NamedTuple
import json


class Configuration(NamedTuple):
    """
    General configuration for the annotation tool.

    output_directory: str, required.
        The directory where the pdfs and
        annotation output will be stored.
    labels: list[dict[str, str]], required.
        The labels in use for annotation.
    relations: list[dict[str, str]], required.
        The relations in use for annotation.
    users_file: Name str, required
        Filename where list of allowed users is specified.
    """

    output_directory: str
    labels: list[dict[str, str]]
    relations: list[dict[str, str]]
    users_file: str


def load_configuration(filepath: str) -> Configuration:
    try:
        blob = json.load(open(filepath))
        return Configuration(**blob)
    except TypeError as e:
        print(
            "Error loading configuration file %s, maybe you're missing a required field? Exception string: %s"
            % (filepath, e)
        )
        raise e
    except Exception as e:
        print("Error loading configuration file %s" % filepath)
        raise e
