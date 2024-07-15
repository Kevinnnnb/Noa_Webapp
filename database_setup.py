from app import create_app, db
from app.models import Stats

app = create_app()

@app.cli.command('initdb'
def initdb_command():
    """Initializes the database."""
    db.create_all()
    initial_stats = Stats(message_count=0, image_count=0)
    db.session.add(initial_stats)
    db.session.commit()
    print('Initialized the database.')
