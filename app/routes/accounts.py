from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.account import Account
from app.models.user import User
from app.models.transaction import Transaction
from app.utils.validators import error_response
from app.utils.account_utils import generate_account_number
from datetime import datetime
from sqlalchemy import or_, text, and_
import hashlib
import uuid
from marshmallow import ValidationError
from app.schemas import AccountSchema, TransactionSchema

bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')

MAX_ACCOUNTS = 2

@bp.route('/accounts', methods=['GET'])
@jwt_required()
def get_accounts():
    try:
        user_id = get_jwt_identity()
        accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
        return jsonify([account.to_dict() for account in accounts]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/accounts', methods=['POST'])
@jwt_required()
def create_account():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        schema = AccountSchema()
        schema.load(data)

        user_id = get_jwt_identity()
        account = Account(
            account_number=str(uuid.uuid4())[:20],
            user_id=user_id,
            account_type=data['account_type'],
            balance=0.0
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify(account.to_dict()), 201
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/accounts/<int:account_id>', methods=['GET'])
@jwt_required()
def get_account(account_id):
    try:
        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=account_id, user_id=user_id, is_active=True).first_or_404()
        return jsonify(account.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/accounts/<int:account_id>', methods=['PUT'])
@jwt_required()
def update_account(account_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=account_id, user_id=user_id, is_active=True).first_or_404()
        
        if 'account_type' in data:
            account.account_type = data['account_type']
        if 'is_active' in data:
            account.is_active = data['is_active']
            
        db.session.commit()
        return jsonify(account.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/accounts/<int:account_id>', methods=['DELETE'])
@jwt_required()
def delete_account(account_id):
    try:
        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=account_id, user_id=user_id, is_active=True).first_or_404()
        
        if account.balance > 0:
            return jsonify({'error': 'Cannot delete account with balance'}), 400
            
        account.is_active = False
        db.session.commit()
        return jsonify({'message': 'Account deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/accounts/<int:account_id>/transactions', methods=['GET'])
@jwt_required()
def get_account_transactions(account_id):
    try:
        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=account_id, user_id=user_id, is_active=True).first_or_404()
        transactions = Transaction.query.filter_by(account_id=account_id).order_by(Transaction.created_at.desc()).all()
        return jsonify([transaction.to_dict() for transaction in transactions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        user_id = get_jwt_identity()
        accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
        account_ids = [account.id for account in accounts]
        transactions = Transaction.query.filter(Transaction.account_id.in_(account_ids)).order_by(Transaction.created_at.desc()).all()
        return jsonify([transaction.to_dict() for transaction in transactions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transactions/accounts/<int:account_id>/transactions', methods=['GET'])
@jwt_required()
def get_account_transactions_list(account_id):
    try:
        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=account_id, user_id=user_id, is_active=True).first_or_404()
        transactions = Transaction.query.filter_by(account_id=account_id).order_by(Transaction.created_at.desc()).all()
        return jsonify([transaction.to_dict() for transaction in transactions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transactions/accounts/<int:account_id>/transactions', methods=['POST'])
@jwt_required()
def create_transaction(account_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        schema = TransactionSchema()
        schema.load(data)

        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=account_id, user_id=user_id, is_active=True).first_or_404()
        
        transaction = Transaction(
            account_id=account_id,
            transaction_type=data['transaction_type'],
            amount=data['amount'],
            description=data.get('description', ''),
            reference_number=str(uuid.uuid4())
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify(transaction.to_dict()), 201
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transactions/deposit', methods=['POST'])
@jwt_required()
def deposit():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=data['account_id'], user_id=user_id, is_active=True).first_or_404()
        
        transaction = Transaction(
            account_id=account.id,
            transaction_type='deposit',
            amount=data['amount'],
            description=data.get('description', 'Deposit'),
            reference_number=str(uuid.uuid4())
        )
        
        account.balance += data['amount']
        transaction.status = 'completed'
        transaction.completed_at = datetime.utcnow()
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify(transaction.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transactions/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        user_id = get_jwt_identity()
        account = Account.query.filter_by(id=data['account_id'], user_id=user_id, is_active=True).first_or_404()
        
        if account.balance < data['amount']:
            return jsonify({'error': 'Insufficient funds'}), 400
        
        transaction = Transaction(
            account_id=account.id,
            transaction_type='withdrawal',
            amount=data['amount'],
            description=data.get('description', 'Withdrawal'),
            reference_number=str(uuid.uuid4())
        )
        
        account.balance -= data['amount']
        transaction.status = 'completed'
        transaction.completed_at = datetime.utcnow()
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify(transaction.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transactions/transfer', methods=['POST'])
@jwt_required()
def transfer():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        user_id = get_jwt_identity()
        from_account = Account.query.filter_by(id=data['from_account_id'], user_id=user_id, is_active=True).first_or_404()
        to_account = Account.query.filter_by(id=data['to_account_id'], is_active=True).first_or_404()
        
        if from_account.balance < data['amount']:
            return jsonify({'error': 'Insufficient funds'}), 400
        
        # Create withdrawal transaction
        withdrawal = Transaction(
            account_id=from_account.id,
            transaction_type='transfer',
            amount=data['amount'],
            description=f"Transfer to account {to_account.account_number}",
            reference_number=str(uuid.uuid4())
        )
        
        # Create deposit transaction
        deposit = Transaction(
            account_id=to_account.id,
            transaction_type='transfer',
            amount=data['amount'],
            description=f"Transfer from account {from_account.account_number}",
            reference_number=withdrawal.reference_number
        )
        
        from_account.balance -= data['amount']
        to_account.balance += data['amount']
        
        withdrawal.status = 'completed'
        deposit.status = 'completed'
        withdrawal.completed_at = datetime.utcnow()
        deposit.completed_at = datetime.utcnow()
        
        db.session.add(withdrawal)
        db.session.add(deposit)
        db.session.commit()
        
        return jsonify({
            'withdrawal': withdrawal.to_dict(),
            'deposit': deposit.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transactions/transfer-advanced', methods=['POST'])
@jwt_required()
def transfer_advanced():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        user_id = get_jwt_identity()
        from_account = Account.query.filter_by(id=data['from_account_id'], user_id=user_id, is_active=True).first_or_404()
        to_account = Account.query.filter_by(id=data['to_account_id'], is_active=True).first_or_404()
        
        if from_account.balance < data['amount']:
            return jsonify({'error': 'Insufficient funds'}), 400
        
        # Create withdrawal transaction
        withdrawal = Transaction(
            account_id=from_account.id,
            transaction_type='transfer',
            amount=data['amount'],
            description=data.get('description', f"Transfer to account {to_account.account_number}"),
            reference_number=str(uuid.uuid4())
        )
        
        # Create deposit transaction
        deposit = Transaction(
            account_id=to_account.id,
            transaction_type='transfer',
            amount=data['amount'],
            description=data.get('description', f"Transfer from account {from_account.account_number}"),
            reference_number=withdrawal.reference_number
        )
        
        from_account.balance -= data['amount']
        to_account.balance += data['amount']
        
        withdrawal.status = 'completed'
        deposit.status = 'completed'
        withdrawal.completed_at = datetime.utcnow()
        deposit.completed_at = datetime.utcnow()
        
        db.session.add(withdrawal)
        db.session.add(deposit)
        db.session.commit()
        
        return jsonify({
            'withdrawal': withdrawal.to_dict(),
            'deposit': deposit.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500