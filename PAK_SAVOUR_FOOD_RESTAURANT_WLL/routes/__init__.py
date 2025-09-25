from flask import Blueprint

# Initialize blueprints here
def register_blueprints(app):
    from .auth import auth_bp
    from .pos import pos_bp
    from .expenses import expenses_bp
    from .reports import reports_bp
    from .admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
