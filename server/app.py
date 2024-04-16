#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
import ipdb

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        json = request.get_json()
        try:
            user = User(username=json['username'], image_url=json['image_url'], bio=json['bio'])
            user.password_hash = json['password']
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return make_response(user.to_dict(), 201)
        except:
            return {}, 422

class CheckSession(Resource):
    def get(self):
        _id = session['user_id']
        if _id:
            user = User.query.filter(User.id == _id).first()
            return make_response(user.to_dict(), 200)
        else:
            return {'error': 'unauthorized'}, 401

class Login(Resource):
    def post(self):
        try:
            json = request.get_json()
            user = User.query.filter(User.username == json['username']).first()
            user.authenticate(json['password'])
            session['user_id'] = user.id
            return make_response(user.to_dict(), 200)
        except:
            return {'error': 'unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.update({'user_id': None})
            return {}, 204
        else:
            return {'error': 'unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return {'error': 'unauthorized'}, 401
        recipes = [recipe.to_dict() for recipe in Recipe.query.all() if recipe.user_id == session['user_id']]
        user = User.query.filter(User.id == session['user_id']).first()
        recipes.append(user.to_dict())
        return recipes, 200

    def post(self):
        if not session.get('user_id'):
            return {'error': 'unauthorized'}, 401
        
        json = request.get_json()
        try:
            recipe = Recipe(
                title=json['title'],
                instructions=json['instructions'],
                minutes_to_complete=json['minutes_to_complete'],
                user_id=session['user_id']
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except:
            return {}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)