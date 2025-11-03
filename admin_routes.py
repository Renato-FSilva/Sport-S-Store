import os
from flask import Blueprint, jsonify, request, render_template
from werkzeug.utils import secure_filename
from app import db
from app.Models.user_model import User
from app.Models.product_model import Product
from app.Models.collection_model import Collection

admin = Blueprint('admin', __name__)

# -------------------------
# Configuração de uploads
# -------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(os.path.dirname(BASE_DIR), "static", "images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # garante que a pasta existe


# -------------------------
# Dashboard (HTML)
# -------------------------
@admin.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template("dashboard.html")


# -------------------------
# Usuários
# -------------------------
@admin.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_admin": u.is_admin
        }
        for u in users
    ])

@admin.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"message": "Usuário não encontrado"}, 404

    db.session.delete(user)
    db.session.commit()
    return {"message": "Usuário excluído com sucesso"}


# -------------------------
# Coleções
# -------------------------
@admin.route('/collections', methods=['GET'])
def list_collections():
    collections = Collection.query.all()
    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "image": c.image
        }
        for c in collections
    ])

@admin.route('/collections', methods=['POST'])
def create_collection():
    name = request.form.get("name")
    description = request.form.get("description")
    file = request.files.get("image")

    filename = None
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    new_col = Collection(
        name=name,
        description=description,
        image=filename
    )
    db.session.add(new_col)
    db.session.commit()
    return {"message": "Coleção criada com sucesso"}

@admin.route('/collections/<int:col_id>', methods=['DELETE'])
def delete_collection(col_id):
    col = Collection.query.get(col_id)
    if not col:
        return {"message": "Coleção não encontrada"}, 404

    db.session.delete(col)
    db.session.commit()
    return {"message": "Coleção excluída com sucesso"}


# -------------------------
# Produtos
# -------------------------
@admin.route('/products', methods=['GET'])
def list_products():
    products = Product.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "description": getattr(p, "description", ""),
            "price": float(p.price),
            "stock": getattr(p, "stock", 0),  # <-- estoque certo
            "image": getattr(p, "image", None),
            "collection_id": getattr(p, "collection_id", None)
        }
        for p in products
    ])

@admin.route('/products', methods=['POST'])
def create_product():
    name = request.form.get("name")
    description = request.form.get("description", "")
    price_raw = request.form.get("price")
    quantity_raw = request.form.get("quantity", 0)
    collection_id = request.form.get("collection_id")
    file = request.files.get("image")

    # trata preço
    try:
        price_value = float(price_raw) if price_raw else 0.0
    except ValueError:
        price_value = 0.0

    # trata estoque informado
    try:
        stock_value = int(quantity_raw) if quantity_raw else 0
    except ValueError:
        stock_value = 0

    # salva imagem (se enviada)
    filename = None
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    # cria produto usando o campo correto "stock"
    new_product = Product(
        name=name,
        description=description,
        price=price_value,
        stock=stock_value,           # <-- importante
        image=filename,
        collection_id=collection_id,
        is_active=True
    )

    db.session.add(new_product)
    db.session.commit()
    return {"message": "Produto criado com sucesso"}

@admin.route('/products/<int:prod_id>', methods=['DELETE'])
def delete_product(prod_id):
    prod = Product.query.get(prod_id)
    if not prod:
        return {"message": "Produto não encontrado"}, 404

    db.session.delete(prod)
    db.session.commit()
    return {"message": "Produto excluído com sucesso"}

@admin.route('/products/<int:prod_id>', methods=['PUT'])
def update_product(prod_id):
    prod = Product.query.get(prod_id)
    if not prod:
        return jsonify({"message": "Produto não encontrado"}), 404

    data = request.get_json() or {}

    # Campos que o admin pode alterar
    new_name = data.get("name")
    new_description = data.get("description")
    new_price = data.get("price")
    new_stock = data.get("stock")
    new_collection_id = data.get("collection_id")  # opcional

    if new_name is not None:
        prod.name = new_name

    if new_description is not None:
        prod.description = new_description

    if new_price is not None:
        try:
            prod.price = float(new_price)
        except ValueError:
            return jsonify({"message": "Preço inválido"}), 400

    if new_stock is not None:
        try:
            prod.stock = int(new_stock)
        except ValueError:
            return jsonify({"message": "Estoque inválido"}), 400

    if new_collection_id is not None and new_collection_id != "":
        prod.collection_id = new_collection_id

    db.session.commit()

    return jsonify({"message": "Produto atualizado com sucesso"}), 200