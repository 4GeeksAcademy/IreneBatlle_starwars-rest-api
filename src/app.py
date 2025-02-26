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
from models import db, User, Planet, People, People_Favorite, Planet_Favorite
#importar todos los models 
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


#conseguir todos los usuarios
@app.route('/user', methods=['GET'])
def handle_hello():
    users = User.query.all()
    all_users = [user.serialize()for user in users]
    return jsonify(all_users), 200


#[GET] /people Listar todos los registros de people en la base de datos.
@app.route('/people', methods=['GET'])
def get_all_people():
    characters = People.query.all()
    all_people = [people.serialize()for people in characters]
    return jsonify(all_people), 200

#[GET] /people/<int:people_id> Muestra la información de un solo personaje según su id.
@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_by_id(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"error": "No se ha encontrado el personaje"}), 404
    return jsonify(person.serialize()), 200


#[GET] /planets Listar todos los registros de planets en la base de datos.

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    all_planets = [planet.serialize()for planet in planets]
    return jsonify(all_planets), 200

#[GET] /planets/<int:planet_id> Muestra la información de un solo planeta según su id.
@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "No se ha encontrado el planeta"}), 404
    return jsonify(planet.serialize()), 200


#conseguir los personajes favoritos de un usuario
@app.route('/user/<int:user_id_in_url>/favorite/people', methods=['GET'])
def favorite_people(user_id_in_url):
    favorites=People_Favorite.query.filter_by(user_id=user_id_in_url).all()
    return jsonify([fav.serialize() for fav in favorites]), 200


#agregar personaje
@app.route('/user/<int:user_id_in_url>/favorite/people/<int: people_id_in_url>', methods=['POST'])
def add_favorite_people(user_id_in_url, people_id_in_url):
    exist=People_Favorite.query.filter_by(user_id=user_id_in_url, people_id = people_id_in_url).first()
    if exist:
        return jsonify({"msg":"Este personaje ya está en favoritos"}), 400
    new_people_favorite = People_Favorite(user_id=user_id_in_url, people_id = people_id_in_url)

    db.session.add(new_people_favorite)
    db.session.commit()
    return jsonify({"msg":"Personaje añadido a favoritos"}), 200


#eliminar personaje
@app.route('/user/<int:user_id_in_url>/favorite/people/<int: people_id_in_url>', methods=['DELETE'])
def delete_favorite_people(user_id_in_url, people_id_in_url):
    exist=People_Favorite.query.filter_by(user_id=user_id_in_url, people_id = people_id_in_url).first()
    if not exist:
        return jsonify({"msg":"Favorito no encontrado"}), 400

    db.session.delete(exist)
    db.session.commit()
    return jsonify({"msg":"Personaje eliminado de favoritos"}), 200


#conseguir los planetas favoritos de un usuario
@app.route('/user/<int:user_id_in_url>/favorite/planet', methods=['GET'])
def favorite_planet(user_id_in_url):
    favorites=Planet_Favorite.query.filter_by(user_id=user_id_in_url).all()
    return jsonify([fav.serialize() for fav in favorites]), 200



#agregar planeta
@app.route('/user/<int:user_id_in_url>/favorite/planet/<int: planet_id_in_url>', methods=['POST'])
def add_favorite_planet(user_id_in_url, planet_id_in_url):
    exist=Planet_Favorite.query.filter_by(user_id=user_id_in_url, planet_id = planet_id_in_url).first()
    if exist:
        return jsonify({"msg":"Este planeta ya está en favoritos"}), 400
    new_planet_favorite = Planet_Favoritelanet_Favorite(user_id=user_id_in_url, planet_id = planet_id_in_url)

    db.session.add(new_planet_favorite)
    db.session.commit()
    return jsonify({"msg":"Planeta añadido a favoritos"}), 200


#eliminar planeta
@app.route('/user/<int:user_id_in_url>/favorite/planet/<int: planet_id_in_url>', methods=['DELETE'])
def delete_favorite_planet(user_id_in_url, planet_id_in_url):
    exist=Planet_Favorite.query.filter_by(user_id=user_id_in_url, planet_id = planet_id_in_url).first()
    if not exist:
        return jsonify({"msg":"Favorito no encontrado"}), 400

    db.session.delete(exist)
    db.session.commit()
    return jsonify({"msg":"Planeta eliminado de favoritos"}), 200




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
