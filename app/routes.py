from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, Bug, db
from app.config import Config
import requests
from datetime import datetime
from marshmallow import Schema, fields, ValidationError

# Input validation schemas
class UserSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, min_length=6)

class BugSchema(Schema):
    bug_id = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    team = fields.Str(required=True)

auth_bp = Blueprint('auth', __name__)
api_bp = Blueprint('api', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Validate input
        schema = UserSchema()
        schema.load(data)

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/bugs', methods=['GET'])
@jwt_required()
def get_bugs():
    try:
        bugs = Bug.query.all()
        return jsonify([bug.to_dict() for bug in bugs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/bugs/<bug_id>', methods=['GET'])
@jwt_required()
def get_bug(bug_id):
    try:
        bug = Bug.query.filter_by(bug_id=bug_id).first_or_404()
        return jsonify(bug.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/bugs', methods=['POST'])
@jwt_required()
def create_bug():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Validate input
        schema = BugSchema()
        schema.load(data)

        if Bug.query.filter_by(bug_id=data['bug_id']).first():
            return jsonify({'error': 'Bug ID already exists'}), 409
        
        bug = Bug(
            bug_id=data['bug_id'],
            title=data['title'],
            description=data['description'],
            team=data['team']
        )
        
        db.session.add(bug)
        db.session.commit()
        
        return jsonify(bug.to_dict()), 201
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/bugs/<bug_id>/mark_fixed', methods=['POST'])
@jwt_required()
def mark_bug_fixed(bug_id):
    try:
        bug = Bug.query.filter_by(bug_id=bug_id).first_or_404()
        
        if bug.status == 'fixed':
            return jsonify({'error': 'Bug is already marked as fixed'}), 400
        
        # Update bug status
        bug.status = 'fixed'
        bug.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Notify backend
        try:
            response = requests.post(
                f"{Config.BACKEND_URL}/api/mark_fixed",
                json={
                    'bug_id': bug_id,
                    'team': bug.team
                },
                headers={
                    'Authorization': f'Bearer {Config.AUTH_KEY}'
                }
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Failed to notify backend: {str(e)}'}), 500
        
        return jsonify(bug.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 