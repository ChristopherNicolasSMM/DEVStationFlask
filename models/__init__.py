"""
models/__init__.py — v3.0
===========================
Expõe a instância do SQLAlchemy e todos os Models.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .addon import Addon  # noqa
from .addon_log import AddonLog  # noqa
from .build_log import BuildLog  # noqa
from .component import Component  # noqa
from .menu import Menu  # noqa
from .odata_connection import ODataConnection  # noqa
from .page import Page  # noqa
from .page_version import PageVersion  # noqa
from .plugin import Plugin  # noqa
from .project import Project  # noqa
from .transaction import Transaction  # noqa
from .version_backup import VersionBackup  # noqa

__all__ = [
    "db",
    "Project",
    "Page",
    "Component",
    "Menu",
    "ODataConnection",
    "PageVersion",
    "VersionBackup",
    "Transaction",
    "Plugin",
    "Addon",
    "AddonLog",
    "BuildLog",
]
