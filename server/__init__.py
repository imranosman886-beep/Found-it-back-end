
from flask import Flask
from flask_cors import CORS

from server.config import Config
from server.extensions import db, migrate, bcrypt
from server import models

from server.routes.auth import auth_bp
from server.routes.categories import categories_bp
from server.routes.lost_items import lost_items_bp
from server.routes.found_items import found_items_bp
from server.routes.claims import claims_bp
from server.routes.notifications import notifications_bp
from server.routes.admin import admin_bp


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object(Config)

    # Apply test settings before initializing the database.
    if test_config:
        app.config.update(test_config)

    # Allow the React frontend to use session cookies.
    CORS(app, supports_credentials=True)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Register all route blueprints.
    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(lost_items_bp)
    app.register_blueprint(found_items_bp)
    app.register_blueprint(claims_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(admin_bp)

    return app
