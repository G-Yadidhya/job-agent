import pytest

from src.config import load_config
from src.logger import get_logger


def test_config_loads():
    config = load_config()
    assert "platforms" in config
    assert config["platforms"] == ["naukri", "remoteok", "wellfound"]


def test_logger_returns_instance():
    logger = get_logger("test_logger")
    assert logger.name == "test_logger"
