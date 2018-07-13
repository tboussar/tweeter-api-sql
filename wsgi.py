# wsgi.py
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass # Heroku does not use .env

import datetime
from flask import Flask, request, json
from config import Config
app = Flask(__name__)
app.config.from_object(Config)


from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow # Order is important here!
db = SQLAlchemy(app)
ma = Marshmallow(app)
from models import Tweet, User
from schemas import tweets_schema, tweet_schema
from schemas import users_schema, user_schema

@app.route('/')
def hello():
    return "Hello Tweeter!"

@app.route('/api/v1/tweets')
def tweets():
    tweets = db.session.query(Tweet).all() # SQLAlchemy request => 'SELECT * FROM tweets'
    return tweets_schema.jsonify(tweets)

@app.route('/api/v1/tweets', methods=['POST'] )
def create_tweet():
    tweet = Tweet()
    user = request.json.get('username')
    userdb = db.session.query(User).filter(User.username == user).first()
    tweet.created_by = userdb.id
    tweet.text = request.json.get('text')
    db.session.add(tweet)
    db.session.commit()
    return 'Created', 201

@app.route('/api/v1/tweets/<int:id>', methods=['GET'] )
def get_tweet(id):
    tweet = db.session.query(Tweet).get(id)
    return tweet_schema.jsonify(tweet), 200

@app.route('/api/v1/tweets/<int:id>', methods=['DELETE'] )
def del_tweet(id):
    tweet = db.session.query(Tweet).filter(Tweet.id == id).delete()
    db.session.commit()
    return 'tweet Deleted', 204

@app.route('/api/v1/tweets/<int:id>', methods=['PATCH'])
def patch_tweet(id):
    data = request.get_json()
    tweet = db.session.query(Tweet).filter(Tweet.id == id).first()
    tweet.text= data['text']
    db.session.commit()
    return 'Tweet updated', 204


@app.route('/api/v1/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if db.session.query(User).filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User()
    user.username=username
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return f'Created {username}', 201
