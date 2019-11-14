from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from pymongo import MongoClient
import pymongo

app = Flask(__name__)
CORS(app)

client = MongoClient('mongodb://localhost:27017/')
db = client.PizzaDB


def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True


# Add User
@app.route("/api/v1/users", methods=['POST'])
def add_user():
    login = db.login
    q = login.find_one({'username': request.json['username']})
    if q != None:
        print("User exisits")
        return jsonify({}), 400
    else:
        if is_sha1(request.json['password']):
            output = {
                'username': request.json['username'],
                'password': request.json['password']
            }
            q = login.insert(output)
            print(output, ": User inserted")
            return jsonify({}), 201
        else:
            print("Bad Request: Add User")
            return jsonify({}), 400


# Remove User
@app.route("/api/v1/users/<username>", methods=['DELETE'])
def remove_user(username):
    login = db.login
    details = db.details
    q = login.remove({'username': username})
    if (q['n'] == 0):
        print("Bad Request: Remove User")
        return jsonify({}), 400
    else:
        print("User:", username, "deleted")
        q = details.remove({'username': username})
        return jsonify({}), 200


# Get User for login or get details
@app.route("/api/v1/users/<username>", methods=['GET'])
@app.route("/api/v1/users/<username>?details=<val>", methods=['GET'])
def get_user(username):
    val = request.args.get('details')
    if (val == None):
        login = db.login
        q = login.find_one({'username': username})
        if (q == None):
            print("Bad Request: Get User")
            return jsonify({}), 400
        else:
            print("User found")
            return jsonify({
                'username': q['username'],
                'password': q['password']
            }), 200
    else:
        details = db.details
        q = details.find_one({'username': username})
        if (q == None):
            print("No details found")
            return jsonify({}), 204
        else:
            output = {
                'username': q['username'],
                'name': q['name'],
                'contact': q['contact'],
                'address': q['address'],
                'email': q['email']
            }
            return jsonify(output), 200


# Add or update user details or password
@app.route("/api/v1/users/<username>", methods=['POST'])
@app.route("/api/v1/users/<username>?pass=<val>", methods=['POST'])
def add_user_details(username):
    val = request.args.get('pass')
    login = db.login
    details = db.details
    q = login.find_one({'username': username})
    if (q == None):
        print("No such user")
        return jsonify({}), 400
    if (val == None):
        q = details.find_one({'username': username})
        if (q == None):  #add details
            res = {
                'username': username,
                'name': request.json['name'],
                'contact': request.json['contact'],
                'address': request.json['address'],
                'email': request.json['email']
            }
            q = details.insert(res)
            print(res, ": details inserted")
            return jsonify({}), 201
        else:
            q = details.update(
                {'username': username},
                {'$set': {
                    request.json['field']: request.json['value']
                }})
            if (q['n'] == 0):
                print("Update failed")
                return jsonify({}), 400
            print("Update successful")
            return jsonify({}), 200
    else:
        if is_sha1(request.json['password']):
            q = login.update({'username': username},
                             {'$set': {
                                 'password': request.json['password']
                             }})
            if (q['n'] == 0):
                print("Update failed")
                return jsonify({}), 400
            print("Update successful")
            return jsonify({}), 200
        else:
            print("Update failed")
            return jsonify({}), 400


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")
