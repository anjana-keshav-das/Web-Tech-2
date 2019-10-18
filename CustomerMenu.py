from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from pymongo import MongoClient
import pymongo

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client.PizzaDB

# Get full menu or category based
@app.route("/api/v1/menu", methods=['GET'])
@app.route("/api/v1/menu?category=<category>", methods=['GET'])
def get_menu():
    category = request.args.get('details')
    menu = db.menu
    if(category == None):
        q = menu.find({})
    else:
        q = menu.find({"category": category})
    if(q == None):
        print("No data")
        return jsonify([]), 204
    output = []
    for i in q:
        temp = {'itemID': i['itemID'], 'category': i['category'], 'name': i['name'],
                'desc': i['desc'], 'price': i['price'], 'img': i['img']}
        output.append(temp)
    return jsonify(output), 200

# Get all categories
@app.route("/api/v1/menu/category", methods=['GET'])
def get_categories():
    category = db.category
    q = category.find({})
    if(q == None):
        print("No data")
        return jsonify([]), 204
    else:
        output = []
        for i in q:
            temp = {'count': i['count'], 'category': i['category']}
            output.append(temp)
        return jsonify(output), 200

# Get all toppings
@app.route("/api/v1/menu/toppings", methods=['GET'])
def get_toppings():
    toppings = db.toppings
    q = toppings.find({})
    if(q == None):
        print("No data")
        return jsonify([]), 204
    else:
        output = []
        for i in q:
            temp = {'price': i['price'], 'name': i['name'], 'img': i['img']}
            output.append(temp)
        return jsonify(output), 200

# Get Cart information
@app.route("/api/v1/menu/cart/<username>", methods=['GET'])
def get_cart(username):
    cart = db.cart
    q = cart.find_one({'username': username})
    if(q == None):
        print("No data")
        return jsonify([]), 204
    else:
        output = []
        items = q['items']
        for i in items:
            temp = {"name": i['name'], "price": i["price"],
                    "topping": i["topping"], "quan": i["quan"]}
            output.append(temp)
        output.append({"total": q["total"]})
        return jsonify(output), 200

# Empty cart
@app.route("/api/v1/menu/cart/<username>", methods=['DELETE'])
def delete_cart(username):
    cart = db.cart
    q = cart.remove({'username': username})
    if(q['n'] == 0):
        print("Bad Request: Empty Cart")
        return jsonify({}), 400
    else:
        print("Cart empty")
        return jsonify({}), 200

# Add item in cart
# or Change quanity (if it becomes 0 delete from cart)
@app.route("/api/v1/menu/cart/<username>", methods=['POST'])
@app.route("/api/v1/menu/cart/<username>?item=<item>&qnt=<qnt>")
def add_item(username):
    item = request.args.get('item')
    qnt = request.args.get('qnt')
    cart = db.cart
    q = cart.find_one({'username': username})
    if(item == None or qnt == None):
        if(q == None):
            if(request.json['toppings'] != None):
                res = {'username': username, 'items': [{'name': request.json['name'], 'price':request.json['price'],
                                                        'toppings':request.json['toppings'], "quantity":request.json['quantity']}], 'total': request.json['price']}
            else:
                res = {'username': username, 'items': [
                    {'name': request.json['name'], 'price':request.json['price', "quantity":request.json['quantity']]}], 'total': request.json['price']}
            q = cart.insert(res)
            print("Inserted")
            return jsonify({}), 201
        else:
            if(request.json['toppings'] != None):
                res = {'name': request.json['name'], 'price': request.json['price'],
                       'toppings': request.json['toppings'], 'quantity': request.json['quantity']}
            else:
                res = {'name': request.json['name'], 'price': request.json['price'],
                       "quantity": request.json['quantity']}
            q = cart.update({'username': username}, {'$push': {'items': res}})
            if(q['n'] == 0):
                print("didn't work")
                return jsonify({}), 400
            q = cart.update({'username': username}, {
                '$inc': {'total': request.json['price']}})
            print("success")
            return jsonify({}), 200
    else:
        pass


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="5000")
