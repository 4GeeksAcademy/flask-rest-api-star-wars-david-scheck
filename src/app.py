"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Person, PersonFavorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def get_all_people():

    error = None
    serialized_people = None

    try:
        people = Person.query.all()
        serialized_people = [person.serialize() for person in people]
        # print(data)
        
    except:
        error = 'Failed to fetch people'        

    response_body = {
        "data": serialized_people,
        "error": error,
    }
    status_code = 200 if not error else 500

    return jsonify(response_body), status_code

@app.route('/favorite/people/<int:person_id>', methods=['POST'])
def create_person_favorite(person_id):
    error = None
    seriliazed_created_person_favorite = None

    try:
        user = db.session.execute(db.select(User).where(User.email == "elvis@gmail.com")).scalar_one()
        created_person_favorite = PersonFavorite(user_id=user.id, person_id=person_id)
        db.session.add(created_person_favorite)
        db.session.commit()
        seriliazed_created_person_favorite = created_person_favorite.serialize()
    except:
        error = 'Failed to create person favorite'        

    response_body = {
        "data": seriliazed_created_person_favorite,
        "error": error,
    }
    status_code = 200 if not error else 500

    return jsonify(response_body), status_code

@app.route('/favorite/people/<int:person_id>', methods=['DELETE'])
def delete_person_favorite(person_id):
    error = None
    seriliazed_deleted_person_favorite = None
    try:
        person_favorite = db.session.execute(
            db.select(PersonFavorite)
                .where(PersonFavorite.user_id == 1, PersonFavorite.person_id == person_id)
        ).scalar_one()
        db.session.delete(person_favorite)
        db.session.commit()
        seriliazed_deleted_person_favorite = person_favorite.serialize()
    except:
        error = 'Failed to delete person favorite'        

    response_body = {
        "data": seriliazed_deleted_person_favorite,
        "error": error,
    }
    status_code = 200 if not error else 500

    return jsonify(response_body), status_code

@app.route('/users/favorites', methods=['GET'])
def get_all_user_favorites():

    error = None
    user_favorites = None

    try:
        # user = User.query.get(1)
        user = db.session.execute(db.select(User).where(User.email == "elvis@gmail.com")).scalar_one()
        user_favorites = [person.serialize() for person in user.person_favorites]
    except:
        error = 'Failed to fetch people'        

    response_body = {
        "data": user_favorites,
        "error": error,
    }
    status_code = 200 if not error else 500

    return jsonify(response_body), status_code

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)