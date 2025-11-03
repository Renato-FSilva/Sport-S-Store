import os
from flask import Blueprint, render_template, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.Models.product_model import Product
from app.Models.collection_model import Collection
from app.Models.user_model import User

# Blueprint oficial do admin
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Caminho onde as imagens vão ficar
# Exemplo: app/static/images/
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # app/Controllers
UPLOAD_FOLDER = os.path.join(os.path.dirname(BASE_DIR), "static", "images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ------------------ DASHBOARD PAGE (HTML) ------------------
@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado: apenas administradores"}), 403

    # O HTML faz fetch pros /admin/users, /admin/products etc.
    # então não precisamos mandar dados aqui
    return render_template('admin/dashboard.html')


# ------------------ USERS ------------------
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_admin": bool(u.is_admin),
        }
        for u in users
    ]), 200


@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user_admin():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Campos obrigatórios ausentes"}), 400

    # Cria usuário comum (is_admin=False fixo aqui)
    new_user = User(username=username, email=email, is_admin=False)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuário criado com sucesso!"}), 201


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Usuário não encontrado"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Usuário removido"}), 200


# ------------------ COLLECTIONS ------------------
@admin_bp.route('/collections', methods=['GET'])
@jwt_required()
def list_collections():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    collections = Collection.query.all()
    return jsonify([c.to_dict() for c in collections]), 200


@admin_bp.route('/collections', methods=['POST'])
@jwt_required()
def create_collection():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    name = request.form.get("name")
    description = request.form.get("description")
    image_file = request.files.get("image")

    if not name:
        return jsonify({"message": "Nome da coleção é obrigatório"}), 400

    image_filename = None
    if image_file:
        # sanitiza o nome do arquivo e salva
        safe_name = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, safe_name)
        image_file.save(image_path)
        image_filename = safe_name

    new_collection = Collection(
        name=name,
        description=description,
        image=image_filename
    )

    db.session.add(new_collection)
    db.session.commit()

    return jsonify({"message": "Coleção criada com sucesso!"}), 201


@admin_bp.route('/collections/<int:collection_id>', methods=['DELETE'])
@jwt_required()
def delete_collection(collection_id):
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    col = Collection.query.get(collection_id)
    if not col:
        return jsonify({"message": "Coleção não encontrada"}), 404

    db.session.delete(col)
    db.session.commit()

    return jsonify({"message": "Coleção removida"}), 200


# ------------------ PRODUCTS ------------------
@admin_bp.route('/products', methods=['GET'])
@jwt_required()
def list_products():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200


@admin_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    # Campos vindos do FormData() do frontend
    name = request.form.get("name")
    description = request.form.get("description", "")
    price_raw = request.form.get("price")
    quantity_raw = request.form.get("quantity")
    collection_id = request.form.get("collection_id")
    image_file = request.files.get("image")

    # valida obrigatórios básicos
    if not name:
        return jsonify({"message": "Nome do produto é obrigatório"}), 400
    if price_raw is None:
        return jsonify({"message": "Preço é obrigatório"}), 400

    # salvar imagem (opcional)
    image_filename = None
    if image_file:
        safe_name = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, safe_name)
        image_file.save(image_path)
        image_filename = safe_name

    # converter preço
    try:
        price_value = float(price_raw) if price_raw else 0.0
    except ValueError:
        return jsonify({"message": "Preço inválido"}), 400

    # converter quantidade -> vira stock
    try:
        stock_value = int(quantity_raw) if quantity_raw else 0
    except ValueError:
        return jsonify({"message": "Quantidade inválida"}), 400

    # montar produto com os campos certos do model
    new_product = Product(
        name=name,
        description=description,
        price=price_value,          # Numeric(10,2)
        stock=stock_value,          # Integer
        image=image_filename,
        collection_id=collection_id,
        is_active=True
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": "Produto criado com sucesso!"}), 201


@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    current_user = get_jwt_identity()
    if not current_user.get("is_admin", False):
        return jsonify({"message": "Acesso negado"}), 403

    prod = Product.query.get(product_id)
    if not prod:
        return jsonify({"message": "Produto não encontrado"}), 404

    db.session.delete(prod)
    db.session.commit()

    return jsonify({"message": "Produto removido"}), 200
