from app.models.tribute import Tribute

def test_add_tribute(client, app, test_user, test_memorial):
    """Test adding a tribute to a memorial"""
    login(client, 'test@example.com', 'password123')
    
    response = client.post(f'/memorial/{test_memorial.id}/tribute', data={
        'content': 'Test tribute content'
    }, follow_redirects=True)
    assert b'Your tribute has been posted' in response.data
    
    with app.app_context():
        tribute = Tribute.query.filter_by(memorial_id=test_memorial.id).first()
        assert tribute is not None
        assert tribute.content == 'Test tribute content'
        assert tribute.is_approved  # Should be auto-approved for memorial creator

def test_tribute_moderation(client, app, test_memorial):
    """Test tribute moderation system"""
    # Create another user
    other_user = User(username='other', email='other@example.com')
    other_user.set_password('password123')
    with app.app_context():
        db.session.add(other_user)
        db.session.commit()
    
    # Login as other user and post tribute
    login(client, 'other@example.com', 'password123')
    client.post(f'/memorial/{test_memorial.id}/tribute', data={
        'content': 'Pending tribute'
    })
    
    # Check tribute is pending
    with app.app_context():
        tribute = Tribute.query.filter_by(content='Pending tribute').first()
        assert tribute is not None
        assert not tribute.is_approved
    
    # Login as memorial creator and approve tribute
    login(client, 'test@example.com', 'password123')
    response = client.post(f'/memorial/tribute/{tribute.id}/approve', follow_redirects=True)
    assert b'Tribute approved' in response.data
    
    with app.app_context():
        tribute = Tribute.query.get(tribute.id)
        assert tribute.is_approved 