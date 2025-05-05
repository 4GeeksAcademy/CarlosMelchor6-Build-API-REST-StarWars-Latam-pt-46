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
from models import db, User, People, Planets
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/users', methods=['GET'])
def get_users():
    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify([user.serialize() for user in users]), 200


@app.route('/user/<int:id>', methods=['GET'])
def get_user_by_id(id):
    user = db.session.execute(
        db.select(User).filter_by(id=id)
    ).scalar_one_or_none()

    if user is None:
        return jsonify({"message": "User not found"}), 404

    return jsonify(user.serialize()), 200


@app.route('/user', methods=["POST"])
def create_user():
    data = request.json

    required_fields = ["email", "password",
                       "user_name", "first_name", "last_name"]
    if not all(data.get(field) for field in required_fields):
        return jsonify({"message": "All fields are required: email, password, user_name, first_name, last_name"}), 400

    user_exists = db.session.execute(
        db.select(User).filter_by(email=data["email"])).scalar_one_or_none()
    if user_exists is not None:
        return jsonify({"message": "Can't create new user"}), 400

    username_exists = db.session.execute(
        db.select(User).filter_by(user_name=data["user_name"])
    ).scalar_one_or_none()

    if username_exists is not None:
        return jsonify({"message": "User with this username already exists"}), 400

    user = User(
        email=data["email"],
        password=data["password"],
        user_name=data["user_name"],
        first_name=data["first_name"],
        last_name=data["last_name"]
    )

    db.session.add(user)

    try:
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    return jsonify({
        "user": user.serialize()
    }), 201


@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user_by_id(id):
    user = db.session.execute(
        db.select(User).filter_by(id=id)
    ).scalar_one_or_none()

    if user is None:
        return jsonify({"message": "User not found"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    return jsonify({
        "message": "User delete succefully"
    }), 201


def get_user_by_id(user_id):
    return User.query.get(user_id)


@app.route('/favorite/planet/<int:user_id>/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"message": "Planet not found"}), 404

    if planet in user.favorite_planets:
        return jsonify({"message": "Planet already in favorites"}), 400

    user.favorite_planets.append(planet)
    db.session.commit()
    return jsonify({"message": "Planet added to favorites"}), 201


@app.route('/favorite/planet/<int:user_id>/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):

    user = get_user_by_id(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"message": "Planet not found"}), 404

    if planet not in user.favorite_planets:
        return jsonify({"message": "Planet is not in user's favorites"}), 400

    try:
        user.favorite_planets.remove(planet)
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    return jsonify({
        "message": "Planet delete succefully"
    }), 201


@app.route('/favorite/character/<int:user_id>/<int:character_id>', methods=['POST'])
def add_favorite_character(user_id, character_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    character = People.query.get(character_id)
    if not character:
        return jsonify({"message": "Character not found"}), 404

    if character in user.favorite_people:
        return jsonify({"message": "Character already in favorites"}), 400

    user.favorite_people.append(character)
    db.session.commit()
    return jsonify({"message": "Character added to favorites"}), 201


@app.route('/favorite/character/<int:user_id>/<int:planet_id>', methods=['DELETE'])
def delete_favorite_character(user_id, planet_id):

    user = get_user_by_id(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    character = People.query.get(planet_id)
    if not character:
        return jsonify({"message": "Character not found"}), 404

    if character not in user.favorite_people:
        return jsonify({"message": "Character is not in user's favorites"}), 400

    try:
        user.favorite_people.remove(character)
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    return jsonify({
        "message": "Character delete succefully"
    }), 201


@app.route('/favorite/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    favorite_planets = [planet.serialize() for planet in user.favorite_planets]
    favorite_people = [person.serialize() for person in user.favorite_people]

    return jsonify({
        "user_id": user.id,
        "favorite_planets": favorite_planets,
        "favorite_people": favorite_people
    }), 200


@app.route('/character', methods=["POST"])
def create_character():
    data = request.json

    required_field = ["name_of_people"]
    if not all(data.get(field) for field in required_field):
        return jsonify({"message": "field are required: name_of_people"}), 400

    people_exists = db.session.execute(
        db.select(People).filter_by(name_of_people=data["name_of_people"])).scalar_one_or_none()
    if people_exists is not None:
        return jsonify({"message": "Can't create a new character"}), 400

    people = People(
        name_of_people=data["name_of_people"],
    )

    db.session.add(people)

    try:
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    return jsonify({
        "character": people.serialize()
    }), 201


@app.route('/character/<int:id>', methods=['GET'])
def get_character_by_id(id):
    character = db.session.execute(
        db.select(People).filter_by(id=id)
    ).scalar_one_or_none()

    if character is None:
        return jsonify({"message": "character not found"}), 404

    return jsonify(character.serialize()), 200


@app.route('/people', methods=['GET'])
def get_people():
    people = db.session.execute(db.select(People)).scalars().all()
    return jsonify([character.serialize() for character in people]), 200


@app.route('/character/<int:id>', methods=['DELETE'])
def delete_character_by_id(id):
    character = db.session.execute(
        db.select(People).filter_by(id=id)
    ).scalar_one_or_none()

    if character is None:
        return jsonify({"message": "Character not found"}), 404

    try:
        db.session.delete(character)
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    return jsonify({
        "message": "Character delete succefully"
    }), 201

@app.route('/character/<int:character_id>', methods=["PUT"])
def update_character(character_id):
    data = request.json

    if not data.get("name_of_people"):
        return jsonify({"message": "Field 'name_of_people' is required"}), 400

    character = People.query.get(character_id)
    if not character:
        return jsonify({"message": "character not found"}), 404

    existing_character = db.session.execute(
        db.select(People).filter_by(name_of_people=data["name_of_people"])
    ).scalar_one_or_none()

    if existing_character and existing_character.id != character.id:
        return jsonify({"message": "Another planet with this name already exists"}), 400

    character.name_of_people = data["name_of_people"]

    try:
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500

    return jsonify({
        "charater": character.serialize(),
        "message": "character updated successfully"
    }), 200


@app.route('/planet', methods=["POST"])
def create_planet():
    data = request.json

    required_field = ["name_of_planets"]
    if not all(data.get(field) for field in required_field):
        return jsonify({"message": "field are required: name_of_planets"}), 400

    people_exists = db.session.execute(
        db.select(Planets).filter_by(name_of_planets=data["name_of_planets"])).scalar_one_or_none()
    if people_exists is not None:
        return jsonify({"message": "Can't create a new character"}), 400

    planet = Planets(
        name_of_planets=data["name_of_planets"],
    )

    db.session.add(planet)

    try:
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    return jsonify({
        "planet": planet.serialize()
    }), 201


@app.route('/planet/<int:id>', methods=['GET'])
def get_planet_by_id(id):
    planet = db.session.execute(
        db.select(Planets).filter_by(id=id)
    ).scalar_one_or_none()

    if planet is None:
        return jsonify({"message": "character not found"}), 404

    return jsonify(planet.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = db.session.execute(db.select(Planets)).scalars().all()
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route('/planet/<int:id>', methods=['DELETE'])
def delete_planet_by_id(id):
    planet = db.session.execute(
        db.select(Planets).filter_by(id=id)
    ).scalar_one_or_none()

    if planet is None:
        return jsonify({"message": "Planet not found"}), 404

    try:
        db.session.delete(planet)
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    return jsonify({
        "message": "Planet delete succefully"
    }), 201

@app.route('/planet/<int:planet_id>', methods=["PUT"])
def update_planet(planet_id):
    data = request.json

    if not data.get("name_of_planets"):
        return jsonify({"message": "Field 'name_of_planets' is required"}), 400

    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"message": "Planet not found"}), 404

    existing_planet = db.session.execute(
        db.select(Planets).filter_by(name_of_planets=data["name_of_planets"])
    ).scalar_one_or_none()

    if existing_planet and existing_planet.id != planet.id:
        return jsonify({"message": "Another planet with this name already exists"}), 400

    planet.name_of_planets = data["name_of_planets"]

    try:
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Internal server error"}), 500

    return jsonify({
        "planet": planet.serialize(),
        "message": "Planet updated successfully"
    }), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)