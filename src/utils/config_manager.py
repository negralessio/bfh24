import yaml
import logging

from src.utils.utils import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


class ConfigManager:

    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        :param config_path: str -- Path to configuration (yaml) file
        """
        self._config_path = config_path

        self._config: dict = self.load_config()

    @property
    def config_path(self) -> str:
        return self._config_path

    @property
    def config(self) -> dict:
        return self._config

    def load_config(self) -> dict:
        """Loads YAML configuration file as a dict."""
        try:
            with open(self._config_path, "r") as yamlfile:
                logger.info(f"Loading yaml file at '{self._config_path}' ...")
                return yaml.load(yamlfile, yaml.FullLoader)
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self._config_path} not found!")
        except PermissionError:
            raise PermissionError(f"Insufficient permission to read {self._config_path}!")
        except IsADirectoryError:
            raise IsADirectoryError(f"{self._config_path} is a directory!")
