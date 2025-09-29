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
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # cria a pasta se não existir


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
        {"id": u.id, "username": u.username, "email": u.email, "is_admin": u.is_admin}
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
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "image": c.image
    } for c in collections])

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
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": getattr(p, "description", ""),   # agora retorna descrição
        "price": float(p.price),
        "quantity": getattr(p, "quantity", 0),
        "image": getattr(p, "image", None),
        "collection_id": getattr(p, "collection_id", None)
    } for p in products])

@admin.route('/products', methods=['POST'])
def create_product():
    name = request.form.get("name")
    description = request.form.get("description", "")
    price = request.form.get("price")
    quantity = request.form.get("quantity", 0)
    file = request.files.get("image")

    # Converte valores
    try:
        price = float(price) if price else 0.0
    except ValueError:
        price = 0.0

    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 0

    filename = None
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    new_product = Product(
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        image=filename
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
