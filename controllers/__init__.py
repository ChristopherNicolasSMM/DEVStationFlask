"""
controllers/__init__.py
========================
Registra todos os Blueprints na aplicação Flask.
Cada controller é um Blueprint independente, promovendo
separação de responsabilidades e escalabilidade.
"""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    """
    Importa e registra cada Blueprint.
    Adicionar um novo controller: basta criar o módulo e incluir aqui.
    """
    from .project_controller   import bp as project_bp
    from .page_controller      import bp as page_bp
    from .component_controller import bp as component_bp
    from .event_controller     import bp as event_bp
    from .rule_controller      import bp as rule_bp
    from .export_controller    import bp as export_bp
    from .menu_controller      import bp as menu_bp

    app.register_blueprint(project_bp)
    app.register_blueprint(page_bp)
    app.register_blueprint(component_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(rule_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(menu_bp)
