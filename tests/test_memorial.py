from app.models.memorial import Memorial
from datetime import datetime
import pytest
from app import db
from flask import url_for

def login(client, email, password):
    return client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)

def logout(client):
    return client.get('/auth/logout', follow_redirects=True)

def test_view_public_memorial(client, app, session, test_memorial):
    """Test viewing a public memorial"""
    with app.app_context():
        # Commit the transaction to make the memorial visible
        session.commit()
        
        response = client.get(f'/memorial/{test_memorial.id}')
        assert response.status_code == 200
        assert test_memorial.name.encode() in response.data
        assert test_memorial.biography.encode() in response.data

def test_view_private_memorial(client, app, session, test_memorial):
    """Test viewing a private memorial redirects to private page"""
    with app.app_context():
        test_memorial.is_public = False
        session.commit()
        
        response = client.get(f'/memorial/{test_memorial.id}')
        assert response.status_code == 200
        assert b'This memorial is private' in response.data

def test_create_memorial(client, app, session, test_user):
    """Test creating a new memorial"""
    with app.app_context():
        # Commit the test user to make it available for login
        session.commit()
        
        # Login first
        login(client, 'test@example.com', 'password123')
        
        response = client.post('/create', data={
            'name': 'New Memorial',
            'birth_date': '1960-01-01',
            'death_date': '2021-01-01',
            'biography': 'New biography',
            'is_public': True
        })
        assert response.status_code == 302  # Redirect after creation
        
        # Refresh the session to see the new memorial
        session.expire_all()
        memorial = Memorial.query.filter_by(name='New Memorial').first()
        assert memorial is not None
        assert memorial.biography == 'New biography'
        assert memorial.creator_id == test_user.id

def test_edit_memorial(client, app, test_user, test_memorial):
    """Test editing a memorial"""
    with app.app_context():
        # Login first
        login(client, 'test@example.com', 'password123')
        
        response = client.post(f'/memorial/{test_memorial.id}/edit', data={
            'name': 'Updated Memorial',
            'birth_date': '1960-01-01',
            'death_date': '2021-01-01',
            'biography': 'Updated biography',
            'is_public': True
        })
        assert response.status_code == 302  # Redirect after edit
        
        memorial = Memorial.query.get(test_memorial.id)
        assert memorial.name == 'Updated Memorial'
        assert memorial.biography == 'Updated biography'

def test_memorial_list(client):
    """Test viewing the list of public memorials"""
    response = client.get('/')
    assert response.status_code == 200

def test_unauthorized_edit(client, test_memorial):
    """Test that unauthorized users cannot edit memorials"""
    response = client.post(f'/memorial/{test_memorial.id}/edit', data={
        'name': 'Hacked Memorial',
        'birth_date': '1960-01-01',
        'death_date': '2021-01-01',
        'biography': 'Hacked biography',
        'is_public': True
    }, follow_redirects=True)
    assert b'Please log in to access this page' in response.data

def test_wrong_user_edit(client, app, test_memorial):
    """Test that wrong users cannot edit other's memorials"""
    # Create another user
    other_user = User(username='other', email='other@example.com')
    other_user.set_password('password123')
    with app.app_context():
        db.session.add(other_user)
        db.session.commit()
    
    # Login as other user
    login(client, 'other@example.com', 'password123')
    
    response = client.post(f'/memorial/{test_memorial.id}/edit', data={
        'name': 'Hacked Memorial',
    }, follow_redirects=True)
    assert b'You do not have permission to edit this memorial' in response.data

def test_custom_url(client, app, test_user):
    """Test creating memorial with custom URL"""
    login(client, 'test@example.com', 'password123')
    
    response = client.post('/create', data={
        'name': 'Custom URL Memorial',
        'birth_date': '1960-01-01',
        'death_date': '2021-01-01',
        'biography': 'Test biography',
        'is_public': True,
        'custom_url': 'test-memorial'
    })
    assert response.status_code == 302
    
    with app.app_context():
        memorial = Memorial.query.filter_by(custom_url='test-memorial').first()
        assert memorial is not None
        assert memorial.name == 'Custom URL Memorial'

def test_duplicate_custom_url(client, app, test_user):
    """Test that duplicate custom URLs are not allowed"""
    login(client, 'test@example.com', 'password123')
    
    # Create first memorial
    client.post('/create', data={
        'name': 'First Memorial',
        'birth_date': '1960-01-01',
        'death_date': '2021-01-01',
        'biography': 'Test biography',
        'is_public': True,
        'custom_url': 'test-memorial'
    })
    
    # Try to create second memorial with same custom URL
    response = client.post('/create', data={
        'name': 'Second Memorial',
        'birth_date': '1960-01-01',
        'death_date': '2021-01-01',
        'biography': 'Test biography',
        'is_public': True,
        'custom_url': 'test-memorial'
    }, follow_redirects=True)
    assert b'Custom URL already taken' in response.data

def test_validation_errors(client, app, test_user):
    """Test form validation errors"""
    with app.app_context():
        login(client, 'test@example.com', 'password123')
        
        # Test missing name
        response = client.post('/create', data={
            'name': '',
            'birth_date': '1960-01-01',
            'death_date': '2021-01-01',
            'biography': 'Test bio'
        }, follow_redirects=True)
        assert b'Name is required' in response.data
        
        # Test missing birth date
        response = client.post('/create', data={
            'name': 'Test Memorial',
            'birth_date': '',
            'death_date': '2021-01-01',
            'biography': 'Test bio'
        }, follow_redirects=True)
        assert b'Birth date is required' in response.data 