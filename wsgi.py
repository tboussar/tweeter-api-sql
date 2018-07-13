# wsgi.py
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass # Heroku does not use .env

import datetime
from flask import Flask, request, json, redirect, session, url_for
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
#from flask_oauth import OAuth
from flask_oauthlib.client import OAuth
from  requests_oauthlib import OAuth2Session
from functools import wraps


app.secret_key = 'development'
oauth = OAuth(app)

github = oauth.remote_app(
    'github',
    consumer_key='9c4890554ad8338bc715',
    consumer_secret='44553bf57cdb48f9d3dff2bf43eb52c4be2e0134',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'github_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/oauth')
def index():
    if 'github_token' in session:
        me = github.get('user')
        return jsonify(me.data)
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['github_token'] = (resp['access_token'], '')
    me = github.get('user')
    return jsonify(me.data)

# client_id='9c4890554ad8338bc715'
# secret_key='44553bf57cdb48f9d3dff2bf43eb52c4be2e0134'
# authorization_base_url = 'https://github.com/login/oauth/authorize'
# token_url = 'https://github.com/login/oauth/access_token'



# @app.route('/oauth')
# def oauth():
#     github = OAuth2Session(client_id)
#     authorization_url, state = github.authorization_url(authorization_base_url)
#     session['oauth_state'] = state
#     return redirect(authorization_url)

# @app.route("/callback", methods=["GET"])
# def callback():
#     github = OAuth2Session(client_id, state=session['oauth_state'])
#     token = github.fetch_token(token_url, client_secret=secret_key,
#                                authorization_response=request.url)
#     session['oauth_token'] = token
#     return redirect(url_for('.profile'))


# @app.route("/profile", methods=["GET"])
# def profile():
#     """Fetching a protected resource using an OAuth 2 token.
#     """
#     github = OAuth2Session(client_id, token=session['oauth_token'])
#     return jsonify(github.get('https://api.github.com/user').json())





@app.route('/')
@login_required
def hello():
    return "Hello Tweeter!"


@app.route('/api/v1/tweets')
def tweets():
    # if 'github_token' in session:
    #     tweets = db.session.query(Tweet).all() # SQLAlchemy request => 'SELECT * FROM tweets'
    #     return tweets_schema.jsonify(tweets)
    # return redirect(url_for('login'))
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
