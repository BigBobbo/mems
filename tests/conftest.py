import pytest
from app import create_app, db
from app.models.user import User
from app.models.memorial import Memorial
from config import TestConfig
from datetime import datetime

@pytest.fixture(scope='function')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def session(app):
    """Creates a new database session for a test"""
    with app.app_context():
        # Start a transaction
        db.session.begin_nested()
        
        yield db.session
        
        # Rollback the transaction
        db.session.rollback()
        db.session.remove()

@pytest.fixture(scope='function')
def test_user(app, session):
    """Create a test user that stays attached to the session"""
    with app.app_context():
        # Create and persist the user
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('password123')
        session.add(user)
        session.flush()  # Flush to get the ID without committing
        
        # Store the ID for later use
        user_id = user.id
        
        yield user
        
        # Clean up
        session.query(User).filter_by(id=user_id).delete()

@pytest.fixture(scope='function')
def test_memorial(app, session, test_user):
    """Create a test memorial that stays attached to the session"""
    with app.app_context():
        # Create and persist the memorial
        memorial = Memorial(
            name='Test Memorial',
            birth_date=datetime(1950, 1, 1),
            death_date=datetime(2020, 1, 1),
            biography='Test biography',
            is_public=True,
            creator_id=test_user.id
        )
        session.add(memorial)
        session.flush()  # Flush to get the ID without committing
        
        # Store the ID for later use
        memorial_id = memorial.id
        
        yield memorial
        
        # Clean up
        session.query(Memorial).filter_by(id=memorial_id).delete() 