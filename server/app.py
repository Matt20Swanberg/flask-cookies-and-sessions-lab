#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate

from models import db, Article, User, ArticleSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles')
def index_articles():
    articles = [ArticleSchema().dump(a) for a in Article.query.all()]
    return make_response(articles)

@app.route('/articles/<int:id>')
def show_article(id):
    """
    Retrieve an article by its ID while enforcing a session-based paywall.

    Tracks the number of articles viewed during the user's session.
    Users can view a maximum of three articles before receiving an
    HTTP 401 Unauthorized response.

    Args:
        id (int): The unique ID of the requested article.

    Returns:
        Response: A JSON response containing the serialized article
        if the user has viewed three or fewer articles.

        Response: A JSON error message with HTTP status code 401
        if the user has exceeded the page-view limit.
    """

    # Initialize the page-view counter for a new session
    # Existing sessions retain their current page-view count
    if 'page_views' not in session:
        session['page_views'] = 0

    # Increment the counter each time an article is requested
    session['page_views'] += 1

    # Allow access to the first three article views
    if session['page_views'] <= 3:

        # Retrieve the requested article by its primary key
        article = db.session.get(Article, id)

        # Serialize the SQLAlchemy object into a JSON-compatible dictionary
        article = ArticleSchema().dump(article)

        # Return the serialized article to the client
        return make_response(article)
    
    # Deny access after three article views have been recorded
    # Return an error message with HTTP 401 Unauthorized
    else:
        return make_response(
        {'message': 'Maximum pageview limit reached'}, 401
    )


if __name__ == '__main__':
    app.run(port=5555)
