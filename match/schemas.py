from marshmallow import Schema, fields


class MatchSchema(Schema):
	username1 = fields.String(required=True)
	username2 = fields.String(required=True)
	scorePlayer1 = fields.Integer(required=True)
	scorePlayer2 = fields.Integer(required=True)
