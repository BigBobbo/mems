from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Create upload directory
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Use tmp directory for Render's ephemeral filesystem
    if os.environ.get('RENDER'):
        app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
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

    from app.cli import register_commands
    register_commands(app)

    return app 