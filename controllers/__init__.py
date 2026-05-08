"""
controllers/__init__.py — v3.0
================================
Registra todos os Blueprints na aplicação Flask.
"""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    from .project_controller   import bp as project_bp
    from .page_controller      import bp as page_bp
    from .component_controller import bp as component_bp
    from .event_controller     import bp as event_bp
    from .rule_controller      import bp as rule_bp
    from .export_controller    import bp as export_bp
    from .menu_controller      import bp as menu_bp
    from .odata_controller     import bp as odata_bp
    from .version_controller   import bp as version_bp
    from .build_controller     import bp as build_bp
    from .nav_controller       import bp as nav_bp
    from .plugin_controller    import bp as plugin_bp
    from .addon_controller     import bp as addon_bp

    for bp in [project_bp, page_bp, component_bp, event_bp, rule_bp,
               export_bp, menu_bp, odata_bp, version_bp, build_bp,
               nav_bp, plugin_bp, addon_bp]:
        app.register_blueprint(bp)
