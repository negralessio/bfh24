import yaml
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


def load_config(config_path: str = "configs/config.yaml") -> Dict:
    """
    Loads a YAML configuration file as a dict given the path.

    :param config_path: str -- Path to the configuration file (default: "configs/config.yaml")
    :return: dict -- Configuration dictionary
    """
    try:
        with open(config_path, "r") as yamlfile:
            logger.info(f"Loading yaml file at '{config_path}' ...")
            return yaml.load(yamlfile, yaml.FullLoader)
    except FileNotFoundError:
        raise FileNotFoundError(f"File {config_path} not found!")
    except PermissionError:
        raise PermissionError(f"Insufficient permission to read {config_path}!")
    except IsADirectoryError:
        raise IsADirectoryError(f"{config_path} is a directory!")


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
