"""
models/__init__.py
==================
Expõe a instância do SQLAlchemy e todos os Models
para que importações externas fiquem simples:
    from models import db, Project, Page, Component, Menu
"""

from flask_sqlalchemy import SQLAlchemy

# Instância única do SQLAlchemy (injetada na app via db.init_app)
db = SQLAlchemy()

# Importa os models para que o SQLAlchemy os conheça
from .project   import Project    # noqa: E402, F401
from .page      import Page       # noqa: E402, F401
from .component import Component  # noqa: E402, F401
from .menu      import Menu       # noqa: E402, F401

__all__ = ["db", "Project", "Page", "Component", "Menu"]
