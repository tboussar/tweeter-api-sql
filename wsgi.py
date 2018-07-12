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
from models import Tweet
from schemas import tweets_schema, tweet_schema

@app.route('/')
def hello():
    return "Hello Tweeter!"

@app.route('/api/v1/tweets')
def tweets():
    tweets = db.session.query(Tweet).all() # SQLAlchemy request => 'SELECT * FROM tweets'
    return tweets_schema.jsonify(tweets)

@app.route('/api/v1/tweets', methods=['POST'] )
def create_tweet():
    data = request.get_json()
    tweet = Tweet()
    tweet.text = data['text']
    #tweet.created_at = datetime.datetime.now()
    db.session.add(tweet)
    db.session.commit()
    return 'Created', 201

@app.route('/api/v1/tweets/<int:id>', methods=['GET'] )
def get_tweet(id):
    tweet = db.session.query(Tweet).get(id)
    return tweet_schema.jsonify(tweet), 200

@app.route('/api/v1/tweets/<int:id>', methods=['DELETE'] )
def del_tweet(id):
    tweet = db.session.query(Tweet).filter(Tweet.id == id ).delete()
    db.session.commit()
    return 'tweet Deleted', 204

@app.route('/api/v1/tweets/<int:id>', methods=['PATCH'])
def patch_tweet(id):
    data = request.get_json()
    tweet = db.session.query(Tweet).filter(Tweet.id == id).first()
    tweet.text= data['text']
    db.session.commit()
    return 'Tweet updated', 204
