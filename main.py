"""
Entry point of the Pipeline
Execute from root dir via "python3 main.py --config configs/config.yaml"
"""

import logging

import src.utils.utils as utils

from src.utils.config_manager import ConfigManager

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    # Parse CLI arguments and config file as dict
    CLI_ARGS: dict = utils.parse_args()
    CFG_MNGR: ConfigManager = ConfigManager(CLI_ARGS.get("config"))
    CFG: dict = CFG_MNGR.config

    print(CFG)


if __name__ == "__main__":
    main()
