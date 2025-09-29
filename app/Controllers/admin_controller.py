from flask import Blueprint, render_template, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.Models.product_model import Product
from app.Models.collection_model import Collection
from app.Models.user_model import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Dashboard de gerenciamento (apenas admin)
@admin_bp.route('/dashboard')
@jwt_required()
def dashboard():
    current_user = get_jwt_identity()

    # bloqueia se não for admin
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado: apenas administradores"}), 403

    products = Product.query.all()
    collections = Collection.query.all()
    users = User.query.all()
    return render_template('admin/dashboard.html', products=products, collections=collections, users=users)

# Adicionar produto
@admin_bp.route('/products/add', methods=['POST'])
@jwt_required()
def add_product():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    name = request.form['name']
    price = request.form['price']
    collection_id = request.form['collection_id']

    new_product = Product(name=name, price=price, collection_id=collection_id)
    from app import db
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Produto adicionado com sucesso!"}), 201

# Adicionar coleção
@admin_bp.route('/collections/add', methods=['POST'])
@jwt_required()
def add_collection():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    name = request.form['name']
    new_collection = Collection(name=name)
    from app import db
    db.session.add(new_collection)
    db.session.commit()
    return jsonify({"message": "Coleção adicionada com sucesso!"}), 201
