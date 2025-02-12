import json
from base64 import b64encode

def get_auth_headers(email, password):
    credentials = b64encode(f"{email}:{password}".encode()).decode('utf-8')
    return {'Authorization': f'Basic {credentials}'}

def test_get_memorial_api(client, test_memorial):
    """Test getting memorial via API"""
    response = client.get(f'/api/memorial/{test_memorial.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == test_memorial.name
    assert data['biography'] == test_memorial.biography

def test_create_memorial_api(client, test_user):
    """Test creating memorial via API"""
    headers = get_auth_headers('test@example.com', 'password123')
    data = {
        'name': 'API Test Memorial',
        'birth_date': '1960-01-01',
        'death_date': '2021-01-01',
        'biography': 'Created via API',
        'is_public': True
    }
    response = client.post('/api/memorial', 
                         json=data,
                         headers=headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'API Test Memorial'
    assert 'id' in data

def test_update_memorial_api(client, test_memorial, test_user):
    """Test updating memorial via API"""
    headers = get_auth_headers('test@example.com', 'password123')
    data = {
        'name': 'Updated via API',
        'biography': 'Updated biography'
    }
    response = client.patch(f'/api/memorial/{test_memorial.id}',
                          json=data,
                          headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Updated via API'

def test_unauthorized_api(client, test_memorial):
    """Test unauthorized API access"""
    headers = get_auth_headers('wrong@example.com', 'wrongpass')
    response = client.patch(f'/api/memorial/{test_memorial.id}',
                          json={'name': 'Hack attempt'},
                          headers=headers)
    assert response.status_code == 401 