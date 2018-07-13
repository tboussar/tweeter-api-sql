# models.py
from wsgi import db
from passlib.apps import custom_app_context as pwd_context
import datetime, string
from random import *
import hashlib
import uuid

class Tweet(db.Model):
    __tablename__ = "tweets"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<id {}>'.format(self.id)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password_hash = db.Column(db.String(128))
    salt = db.Column(db.String, nullable=False, default=str(uuid.uuid4().hex))
    #api_key = db.Column(db.String(128), nullable=False, default)
    tweet = db.relationship("Tweet")

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def hash_password(self, password):
        saltPassword = password + str(self.salt)
        self.password_hash = pwd_context.encrypt(saltPassword)

    def verify_password(self, password):
        saltPassword = password + str(self.salt)
        return pwd_context.verify(saltPassword, self.password_hash)
