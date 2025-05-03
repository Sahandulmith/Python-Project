import pytest
from app import create_app
from app.models import db, User, Bug
from app.config import Config
import json

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Create a test user
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    
    # Login to get token
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    token = json.loads(response.data)['access_token']
    
    return {'Authorization': f'Bearer {token}'}

def test_register(client):
    response = client.post('/auth/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass'
    })
    assert response.status_code == 201
    assert json.loads(response.data)['message'] == 'User created successfully'

def test_login(client):
    # First register
    client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass'
    })
    
    # Then login
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    assert 'access_token' in json.loads(response.data)

def test_create_bug(client, auth_headers):
    response = client.post('/api/bugs', json={
        'bug_id': 'BUG-001',
        'title': 'Test Bug',
        'description': 'This is a test bug',
        'team': 'TryCatch'
    }, headers=auth_headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['bug_id'] == 'BUG-001'
    assert data['status'] == 'open'

def test_get_bug(client, auth_headers):
    # First create a bug
    client.post('/api/bugs', json={
        'bug_id': 'BUG-001',
        'title': 'Test Bug',
        'description': 'This is a test bug',
        'team': 'TryCatch'
    }, headers=auth_headers)
    
    # Then get it
    response = client.get('/api/bugs/BUG-001', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['bug_id'] == 'BUG-001'

def test_BUG303(client, auth_headers, monkeypatch):
    # Create BUG-303
    client.post('/api/bugs', json={
        'bug_id': 'BUG-303',
        'title': 'Test Bug 303',
        'description': 'This is test bug 303',
        'team': 'TryCatch'
    }, headers=auth_headers)
    
    # Mock the backend response
    def mock_post(*args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.status_code = 200
            
            def raise_for_status(self):
                pass
        
        return MockResponse()
    
    monkeypatch.setattr('requests.post', mock_post)
    
    # Mark BUG-303 as fixed
    response = client.post('/api/bugs/BUG-303/mark_fixed', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['bug_id'] == 'BUG-303'
    assert data['status'] == 'fixed'
    assert data['team'] == 'TryCatch' 