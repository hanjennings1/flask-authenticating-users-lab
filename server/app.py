#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User, ArticlesSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [ArticlesSchema().dump(article) for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = ArticlesSchema.dump(article)

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

# == NEW CLASSES ==
class Login(Resource):
    def post(self):
        username = request.get_json().get('username')
        user = User.query.filter(User.username == username).first()

        #set session['user_id'] to the found user's id
        session['user_id'] = user.id
        #return user as JSON with a 200 status code
        return UserSchema().dump(user), 200


class Logout(Resource):
    def delete(self):
        #remove the value for session['user_id']
        session['user_id'] = None
        #returns no data and a 204 (No Content) status code
        return {}, 204


class CheckSession(Resource):
    def get(self):
        #get current value of session['user_id'] (it may not exist)
        user_id = session.get('user_id')
        #If the session has a user_id, get() returns the user as JSON with a 200 status code.
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return UserSchema().dump(user), 200
        #If the session does not have a user_id, get() returns no data and a 401 (Unauthorized) status code.
        return {}, 401


api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')           # log in
api.add_resource(Logout, '/logout')         # log out
api.add_resource(CheckSession, '/check_session')    # check user status

if __name__ == '__main__':
    app.run(port=5555, debug=True)
