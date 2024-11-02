# src/utils.py

import logging
import yaml


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def load_config(config_path='config/config.yaml'):
    with open(config_path) as f:
        return yaml.safe_load(f)
