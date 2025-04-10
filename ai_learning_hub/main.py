"""
Main application module for AI Learning Hub
"""
import click
from flask.cli import with_appcontext
from ai_learning_hub.app import app
from ai_learning_hub.init_db import init_db

# Register a CLI command to initialize the database
@app.cli.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    click.echo("Initializing the database...")
    init_db()
    click.echo("Finished initializing the database.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)