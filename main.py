"""
Entry point of the Pipeline
Execute from root dir via "python3 main.py --config configs/config.yaml"
"""

import logging

import src.utils.utils as utils

utils.setup_logging()
logger = logging.getLogger(__name__)


def main():
    # Parse CLI arguments and config file as dict
    CLI_ARGS: dict = utils.parse_args()
    CFG: dict = utils.load_config(CLI_ARGS.get("config"))

    print(CFG)


if __name__ == "__main__":
    main()
