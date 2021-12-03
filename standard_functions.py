import json


def load_json_config_file(file_path):
    with open(file_path, "r") as config_file:
        return json.load(config_file)
