from app import db
from app.models import User, Memorial, Tribute, Photo, Event

def init_db():
    db.drop_all()
    db.create_all() 