from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Add custom Jinja filters
    @app.template_filter('slice')
    def slice_filter(iterable, start, end):
        return list(iterable)[start:end]

    @app.template_filter('nl2br')
    def nl2br_filter(text):
        if not text:
            return ""
        return text.replace('\n', '<br>')

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.routes import auth, memorial, admin, event
    app.register_blueprint(auth.bp)
    app.register_blueprint(memorial.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(event.bp)

    # Create database tables
    with app.app_context():
        from app.models.init_db import init_db
        init_db()

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    return app 