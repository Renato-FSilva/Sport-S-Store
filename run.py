from app import create_app, db, bcrypt
from app.Models.user_model import User
from flask_cors import CORS
from flask import render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token
from flask_migrate import Migrate   # 🚀 import migrate

# Importando blueprints
from routes import main        # rotas de usuário
from admin_routes import admin # rotas do admin

app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}})

# Config JWT
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
jwt = JWTManager(app)

# 🚀 Inicializar Migrate
migrate = Migrate(app, db)

# Registrar Blueprints
app.register_blueprint(main)
app.register_blueprint(admin, url_prefix="/admin")  # rotas do admin ficam em /admin/...

# ------------------------------
# Rotas de páginas (HTML)
# ------------------------------
@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# ------------------------------
# API para registro
# ------------------------------
@app.route('/api/register', methods=['POST'])
def register_api():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'message': 'Preencha todos os campos!'}), 400
    
    if User.query.filter((User.username==username)|(User.email==email)).first():
        return jsonify({'message': 'Usuário ou email já existe!'}), 409
    
    new_user = User(username=username, email=email, is_admin=False)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Cadastro realizado com sucesso!'}), 200

# ------------------------------
# API para login
# ------------------------------
@app.route('/api/login', methods=['POST'])
def login_api():
    if not request.is_json:
        return jsonify({'message': 'JSON esperado.'}), 400

    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({'message': 'Informe usuário e senha.'}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = create_access_token(identity={"id": user.id, "is_admin": bool(user.is_admin)})

        # monta resposta com username, is_admin e redirect
        resp = {
            "access_token": token,
            "username": user.username,
            "is_admin": bool(user.is_admin),
            "redirect": url_for('admin.dashboard') if user.is_admin else url_for('main.home')
        }
        return jsonify(resp), 200

    return jsonify({'message': 'Credenciais inválidas'}), 401

# ------------------------------
# Inicialização da aplicação
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
