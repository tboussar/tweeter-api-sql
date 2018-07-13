# schemas.py
from wsgi import ma
from marshmallow import fields
from models import Tweet, User

class TweetSchema(ma.Schema):
    class Meta:
        model = Tweet

    id = fields.Int()
    text = fields.Str()
    created_at = fields.Date()
    updated_at = fields.Date()

tweet_schema = TweetSchema()
tweets_schema = TweetSchema(many=True)

class UserSchema(ma.Schema):
    class Meta:
        model = User

    id = fields.Int()
    username = fields.Str()

user_schema = UserSchema()
users_schema = UserSchema(many=True)
