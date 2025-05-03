from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    
    @validates('password')
    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', value):
            raise ValidationError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError('Password must contain at least one special character')

class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6))
    
    @validates('new_password')
    def validate_password(self, value):
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', value):
            raise ValidationError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError('Password must contain at least one special character')

class AccountSchema(Schema):
    account_type = fields.Str(required=True, validate=validate.OneOf(['checking', 'savings', 'investment']))
    is_active = fields.Bool(missing=True)

class TransactionSchema(Schema):
    transaction_type = fields.Str(required=True, validate=validate.OneOf(['deposit', 'withdrawal', 'transfer']))
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    description = fields.Str(validate=validate.Length(max=200))

class TransferSchema(Schema):
    from_account_id = fields.Int(required=True)
    to_account_id = fields.Int(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    description = fields.Str(validate=validate.Length(max=200)) 