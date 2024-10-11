import argparse
import logging

from typing import Dict

from src.utils.logger import setup_logger

logger = setup_logger(__name__, logging.WARNING)


def parse_args() -> Dict:
    """
    Defines and parses CLI arguments as a dictionary.

    :return: args_dict: dict
    """
    logger.info("Parsing CLI arguments as dict ...")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        help="Path to the config file",
        type=str,
        default="configs/config.yaml",
    )
    args = parser.parse_args()
    args_dict = vars(args)

    logger.info(f"Successfully parsed {len(args_dict.keys())} CLI argument(s).")

    return args_dict
