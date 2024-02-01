from typing import Any, Union

import json
import pickle
from pathlib import Path

import yaml


def read_yaml(fpath: Union[str, Path]) -> dict[Any, Any]:
    with open(fpath) as fp:
        data = yaml.safe_load(fp)
    return data


def read_json(fpath: Union[str, Path]) -> dict[Any, Any]:
    with open(fpath) as fp:
        data = json.load(fp)
    return data


def load_graph(fpath: Union[str, Path]):
    with open(fpath, 'rb') as f:
        graph_obj = pickle.load(f)
    return graph_obj
