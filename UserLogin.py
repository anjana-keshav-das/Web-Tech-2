from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from pymongo import MongoClient
import pymongo
import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient('mongodb://localhost:27017/')
db = client.PizzaDB

order_no = 0


def make_payment(username, amount):
    return 1


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


#Admin Login
@app.route("/api/v1/admin/<username>", methods=['GET'])
def get_admin(username):
    admin = db.admin
    q = admin.find_one({'username': username})
    if (q == None):
        print("Bad Request: Get User")
        return jsonify({}), 400
    else:
        print("User found")
        return jsonify({
            'username': q['username'],
            'password': q['password']
        }), 200


# Add Admin
@app.route("/api/v1/admin", methods=['POST'])
def add_admin():
    admin = db.admin
    q = admin.find_one({'username': request.json['username']})
    if q != None:
        print("User exisits")
        return jsonify({}), 400
    else:
        if is_sha1(request.json['password']):
            output = {
                'username': request.json['username'],
                'password': request.json['password']
            }
            q = admin.insert(output)
            print(output, ": User inserted")
            return jsonify({}), 201
        else:
            print("Bad Request: Add User")
            return jsonify({}), 400


# Get full menu or category based
@app.route("/api/v1/menu", methods=['GET'])
@app.route("/api/v1/menu?category=<category>", methods=['GET'])
def get_menu():
    category = request.args.get('category')
    menu = db.menu
    cat = db.categories
    if (category == None):
        q = menu.find({})
    else:
        q = cat.find_one({"name": category})
        if (q == None):
            print("No data")
            return jsonify([]), 204
        q = menu.find({"category": category})
    if (q == None):
        print("No data")
        return jsonify([]), 204
    output = []
    for i in q:
        temp = {
            'category': i['category'],
            'name': i['name'],
            'desc': i['desc'],
            'price': i['price'],
            'img': i['img']
        }
        output.append(temp)
    return jsonify(output), 200


# Get all categories
@app.route("/api/v1/menu/category", methods=['GET'])
def get_categories():
    category = db.categories
    q = category.find({})
    if (q == None):
        print("No data")
        return jsonify([]), 204
    else:
        output = []
        for i in q:
            temp = {'count': i['count'], 'category': i['name']}
            output.append(temp)
        return jsonify(output), 200


# Get all toppings
@app.route("/api/v1/menu/toppings", methods=['GET'])
def get_toppings():
    toppings = db.toppings
    q = toppings.find({})
    if (q == None):
        print("No data")
        return jsonify([]), 204
    else:
        output = []
        for i in q:
            # , 'img': i['img']}
            temp = {'price': i['price'], 'name': i['name']}
            output.append(temp)
        return jsonify(output), 200


# Get Cart information
@app.route("/api/v1/menu/cart/<username>", methods=['GET'])
def get_cart(username):
    cart = db.cart
    q = cart.find_one({'username': username})
    if (q == None):
        print("No data")
        return jsonify([]), 204
    else:
        output = {}
        tmp = []
        items = q['items']
        for i in items:
            if ('toppings' in i):
                temp = {
                    "name": i['name'],
                    "price": i["price"],
                    "toppings": i["toppings"],
                    "quantity": i["quantity"]
                }
            else:
                temp = {
                    "name": i['name'],
                    "price": i["price"],
                    "quantity": i["quantity"]
                }
            tmp.append(temp)
        output['items'] = tmp
        output['total'] = q['total']
        output['address'] = q['address']
        return jsonify(output), 200


# Empty cart or delete an item
@app.route("/api/v1/menu/cart/<username>", methods=['DELETE'])
@app.route("/ api/v1/menu/cart/<username>?item=<item>", methods=['DELETE'])
def delete_cart(username):
    item = request.args.get('item')
    cart = db.cart
    if (item == None):
        q = cart.remove({'username': username})
        if (q['n'] == 0):
            print("Bad Request: Empty Cart")
            return jsonify({}), 400
        else:
            print("Cart empty")
            return jsonify({}), 200
    else:
        q = cart.find_one({'username': username})
        if (q == None):
            print("Bad Request: Empty Cart")
            return jsonify({}), 400
        else:
            q = cart.update({'username': username},
                            {'$pull': {
                                'items': {
                                    "name": item
                                }
                            }})
            print("success")
            return jsonify({}), 200


# Add item in cart
# or Change quanity (if it becomes 0 delete from cart)
@app.route("/api/v1/menu/cart/<username>", methods=['POST'])
@app.route("/api/v1/menu/cart/<username>?item=<item>&qnt=<qnt>",
           methods=['POST'])
def add_item(username):
    item = request.args.get('item')
    qnt = request.args.get('qnt')
    cart = db.cart
    details = db.details
    add = details.find_one({"username": username}, {"address": 1})
    q = cart.find_one({'username': username})
    if (item == None or qnt == None):
        if (q == None):
            if ('toppings' in request.json):
                res = {
                    'username':
                    username,
                    'items': [{
                        'name': request.json['name'],
                        'price': request.json['price'],
                        'toppings': request.json['toppings'],
                        "quantity": request.json['quantity']
                    }],
                    "address":
                    add['address'],
                    'total':
                    request.json['price']
                }
            else:
                res = {
                    'username':
                    username,
                    'items': [{
                        'name': request.json['name'],
                        'price': request.json['price'],
                        "quantity": request.json['quantity']
                    }],
                    "address":
                    add['address'],
                    'total':
                    request.json['price']
                }
            q = cart.insert(res)
            print("Inserted")
            return jsonify({}), 201
        else:
            if ('toppings' in request.json):
                res = {
                    'name': request.json['name'],
                    'price': request.json['price'],
                    'toppings': request.json['toppings'],
                    'quantity': request.json['quantity']
                }
            else:
                res = {
                    'name': request.json['name'],
                    'price': request.json['price'],
                    "quantity": request.json['quantity']
                }
            q = cart.update({'username': username}, {'$push': {'items': res}})
            if (q['n'] == 0):
                print("didn't work")
                return jsonify({}), 400
            q = cart.update({'username': username},
                            {'$inc': {
                                'total': request.json['price']
                            }})
            print("success")
            return jsonify({}), 200
    else:
        if (q == None):
            print("No such user")
            return jsonify({}), 400
        else:
            if (qnt <= 0):
                q = cart.update({'username': username},
                                {'$pull': {
                                    'items': {
                                        "name": item
                                    }
                                }})
                print("success")
                return jsonify({}), 200
            q = cart.update({
                'username': username,
                'items.name': item
            }, {'$inc': {
                'items.$.quantity': int(qnt)
            }})
            if (q['n'] == 0):
                print("didn't work")
                return jsonify({}), 400
            else:
                print("success")
                return jsonify({}), 200


#Place order and add to customer sale queue
@app.route("/api/v1/menu/cart/buy/<username>", methods=['POST'])
def place_order(username):
    global order_no
    cart = db.cart
    prepare = db.prepare
    # try:
    q = cart.find_one({'username': username})
    cost = q['total']
    if (make_payment(username, cost)):
        q = prepare.insert({
            'username':
            username,
            'ordno':
            order_no,
            "received":
            0,
            "preparing":
            0,
            "delivery":
            0,
            "time":
            datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })
        order_no += 1
        if (order_no > 50):
            order_no = 0
        return jsonify({}), 200
    else:
        return jsonify({}), 402
    # except:
    #     return jsonify({}), 400


#Get All Prepared
@app.route("/api/v1/menu/prepare", methods=['GET'])
def get_orders():
    global order_no
    prepare = db.prepare
    if (prepare.count_documents({}) == 0):
        return jsonify({}), 204
    else:
        q = prepare.find({})
        output = []
        for i in q:
            temp = {
                "username": i['username'],
                'ordno': i['ordno'],
                "received": i["received"],
                "preparing": i["preparing"],
                "delivery": i["delivery"],
                "time": i["time"]
            }
            output.append(temp)
        return jsonify(output), 200


#Update Progress
@app.route("/api/v1/menu/prepare/<username>", methods=['POST'])
def update_progress(username):
    prepare = db.prepare
    try:
        q1 = prepare.update({'username': username},
                            {'$set': {
                                request.json['progress']: 1
                            }})
        q = prepare.update({'username': username}, {
            '$set': {
                'time': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        })
        return jsonify({}), 200
    except:
        return jsonify({}), 400


#get progress
@app.route("/api/v1/<username>/progress", methods=['POST'])
def get_progress(username):
    tm = request.json['time']
    prepare = db.prepare
    try:
        q = prepare.find_one({"username": username})
        if (q['time'] != tm):
            output = {
                "received": q['received'],
                "preparing": q["preparing"],
                "delivery": q["delivery"],
                "time": q['time']
            }
            return jsonify(output), 200
        else:
            return jsonify({}), 304
    except:
        return jsonify({}), 400


#Order completed
@app.route("/api/v1/menu/complete/<username>", methods=['POST'])
def order_complete(username):
    cart = db.cart
    prepare = db.prepare
    q = prepare.remove({'username': username})
    q = cart.remove({'username': username})
    return jsonify({}), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")
