import click
from flask.cli import with_appcontext
from app.models.seed_data import seed_data

def register_commands(app):
    @app.cli.command()
    @with_appcontext
    def seed():
        """Seed the database with example data."""
        seed_data() 