from app import create_app, db, bcrypt
from app.Models.user_model import User
from flask_cors import CORS
from flask import render_template, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token

app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}})

# Config JWT
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
jwt = JWTManager(app)

# Rotas HTML
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'message': 'Preencha todos os campos!'}), 400
        
        if User.query.filter((User.username==username)|(User.email==email)).first():
            return jsonify({'message': 'Usuário ou email já existe!'}), 409
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Cadastro realizado com sucesso!'}), 200
    
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login_api():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = create_access_token(identity=user.id)
        return jsonify({'access_token': token})
    return jsonify({'message': 'Credenciais inválidas'}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
