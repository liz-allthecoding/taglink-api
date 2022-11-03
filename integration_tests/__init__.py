import logging.config
import yaml

with open("integration_tests/logging.yaml") as log_conf:
    logging_config = yaml.safe_load(log_conf.read())
logging.config.dictConfig(logging_config)
