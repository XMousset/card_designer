import json

import numpy as np

CONFIG_NAME = "config.json"


def json_vector2array(d) -> dict:
    """Convert vectors into numpy.ndarray.

    Parameters
    ----------
    d : dict
        Dictionary to check for convertions.

    Returns
    -------
    dict
        Dictionary with numpy.ndarray instead of list for vectors.
    """
    for key, value in d.items():
        if isinstance(value, list) and len(value) == 2:
            d[key] = np.array(value)
    return d


def read_json(json_name) -> dict:
    """Read json file with numpy array.

    Parameters
    ----------
    json_name : str
        Name of the json file (e.g. "axample.json")

    Returns
    -------
    dict
        A dict containing json file data.
    """
    with open(json_name, "r") as file:
        json_dict = json.load(file, object_hook= json_vector2array)
        return json_dict


CONFIG = read_json(CONFIG_NAME)