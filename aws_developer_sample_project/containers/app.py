from flask import Flask,request,render_template
import products_db

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/products",methods=['GET'])
def query_products():
    category = request.args.get('category')
    if category:
        return products_db.get_products_by_category(category)
    return products_db.get_all_products()

@app.route("/products/<id>",methods=['GET'])
def get_product(id):
    product=products_db.get_product(id)
    if not product:
        return "Product not found", 404
    return product

@app.route("/products/<id>",methods=['DELETE'])
def delete_product(id):
    product=products_db.delete_product(id)
    return product


@app.route("/products", methods=['POST'])
def insert_product():
    item = request.get_json()
    inserted=products_db.insert_product(item)
    return inserted, 201

from utils import create_options_response   
@app.route("/products", methods=['OPTIONS'])
@app.route("/products/<id>", methods=['OPTIONS'])
def options():
    return create_options_response()