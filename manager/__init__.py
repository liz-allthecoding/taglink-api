import yaml

with open("config.yaml") as file_handle:
    CONFIG = yaml.safe_load(file_handle)
