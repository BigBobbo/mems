import pytest
from app import create_app, db
from app.models.user import User
from app.models.memorial import Memorial
from config import TestConfig
from datetime import datetime

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('password123')
    with app.app_context():
        db.session.add(user)
        db.session.commit()
    return user

@pytest.fixture
def test_memorial(app, test_user):
    memorial = Memorial(
        name='Test Memorial',
        birth_date=datetime(1950, 1, 1),
        death_date=datetime(2020, 1, 1),
        biography='Test biography',
        is_public=True,
        creator_id=test_user.id
    )
    with app.app_context():
        db.session.add(memorial)
        db.session.commit()
    return memorial 