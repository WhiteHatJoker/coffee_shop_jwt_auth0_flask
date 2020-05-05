import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
db = setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
Public endpoint for getting short verion of drinks
'''
@app.route('/drinks')
def get_drinks():
    all_drinks = Drink.query.all()
    if all_drinks:
        formatted_drinks = [drink.short() for drink in all_drinks]
        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })
    else:
        abort(404)

'''
Private endpoint for getting long verion of drinks
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    all_drink_details = Drink.query.all()
    if all_drink_details:
        formatted_drink_details = [drink_detail.long() for drink_detail in all_drink_details]
        return jsonify({
            'success': True,
            'drinks': formatted_drink_details
        })
    else:
        abort(404)

'''
Private endpoint for creating new drinks
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    try:
        data = request.get_json()
        if not('title' in data and 'recipe' in data):
            abort(422)

        drink = Drink(
            title=data.get('title', None),
            recipe=json.dumps(data.get('recipe', None))
        )
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(422)


'''
Private endpoint for editing a specific drink
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if drink:
        try:
            data = request.get_json()
            updated_drink_title = data.get('title', None)
            updated_drink_recipe = data.get('recipe', None)
            if updated_drink_title:
                drink.title = updated_drink_title
            if updated_drink_recipe:
                drink.recipe = updated_drink_recipe
            drink.update()
            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
        except:
            abort(422)
    else:
        abort(404)

'''
Private endpoint for deleting a drink
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    try:
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except:
        abort(422)


## Error Handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource you are trying to modify is not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable data, please check your data"
    }), 422

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), 401

