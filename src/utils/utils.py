import argparse
import logging

from typing import Dict

logger = logging.getLogger(__name__)


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


def setup_logging(loglevel=logging.INFO) -> None:
    """Handles the logger setup / configuration

    :param loglevel: Level of logging, e.g. {logging.DEBUG, logging.INFO}
    :return: None
    """
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s [%(name)s:%(lineno)s] [%(levelname)s] >>> %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
