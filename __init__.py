"""Top-level package for my_nodes."""

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]

__author__ = """tagbliton"""
__email__ = "1229532590@qq.com"
__version__ = "0.0.1"

from .nodes import NODE_CLASS_MAPPINGS
from .nodes import NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"