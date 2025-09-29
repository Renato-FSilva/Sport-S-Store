from app import create_app, db
from app.Models.user_model import User

app = create_app()

with app.app_context():
    # Verifica se já existe admin
    if not User.query.filter_by(is_admin=True).first():
        admin = User(username="admin", email="admin@sportsstore.com", is_admin=True)
        admin.set_password("123456")  # senha
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado com sucesso!")
    else:
        print("Já existe um admin cadastrado.")
