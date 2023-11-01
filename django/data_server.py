import os

from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/metadata"
mongo = PyMongo(app)

db = mongo.db.user_data


@app.route('/user/data_put', methods=['PUT'])
def put_data():
    id = request.json['id']
    data = request.json['data']

    if id and data:
        new_entry = {"id": id, "data": data}
        db.insert_one(new_entry)
        return {"message": "Entry saved successfully."}, 201
    else:
        return {"error": "Invalid data provided."}, 400


auth = HTTPBasicAuth()

users = {
    os.getenv("mongo_db_user"): generate_password_hash(os.getenv("mongo_db_password"))
}


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username


@app.route('/api/data_get', methods=['GET'])
@auth.login_required
def get_data():
    id = request.args.get('id')

    if id:
        result = db.find_one({"id": id})

        if result:
            return jsonify(result['data']), 200
        else:
            return {"error": "Data not found."}, 404
    else:
        return {"error": "Invalid id provided."}, 400


if __name__ == '__main__':
    app.run(debug=True)
