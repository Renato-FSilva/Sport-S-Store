from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import create_access_token
from app import db
from app.Models.user_model import User

user_controller = Blueprint('user_controller', __name__)

# ------------------------------
# Registro de usuário comum
# ------------------------------
@user_controller.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'message': 'Preencha todos os campos.'}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'Usuário ou e-mail já existe.'}), 409

    # 👇 Agora só usa is_admin=False
    new_user = User(username=username, email=email, is_admin=False)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuário cadastrado com sucesso!'}), 201


# ------------------------------
# Login de usuário / admin
# ------------------------------
@user_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # agora o token leva id + is_admin
        access_token = create_access_token(identity={"id": user.id, "is_admin": user.is_admin})

        # decide o redirecionamento
        if user.is_admin:
            redirect_url = url_for('admin.dashboard')
        else:
            redirect_url = url_for('main.home')

        return jsonify({
            "access_token": access_token,
            "is_admin": user.is_admin,
            "redirect": redirect_url
        }), 200

    return jsonify({'message': 'Credenciais inválidas'}), 401
