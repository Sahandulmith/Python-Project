from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6))

class AccountSchema(Schema):
    account_type = fields.Str(required=True, validate=validate.OneOf(['checking', 'savings', 'investment']))
    is_active = fields.Bool(missing=True)

class TransactionSchema(Schema):
    transaction_type = fields.Str(required=True, validate=validate.OneOf(['deposit', 'withdrawal', 'transfer']))
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    description = fields.Str(validate=validate.Length(max=200)) 