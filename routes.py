from flask import Blueprint, render_template, abort, request, jsonify
from app import db
from app.Models.collection_model import Collection
from app.Models.product_model import Product

main = Blueprint('main', __name__)

# ----------------------------
# Páginas públicas (HTML)
# ----------------------------

# Página de registro
@main.route('/register')
def register_page():
    return render_template('register.html')

# Página de login
@main.route('/login')
def login_page():
    return render_template('login.html')

# Home do usuário logado comum
@main.route('/home')
def home():
    return render_template('home.html')

# Página de uma coleção (lista produtos daquela coleção)
@main.route('/colecao/<int:col_id>')
def collection_page(col_id):
    # A página em si é sempre renderizada.
    # Os dados (nome da coleção, produtos etc.) são buscados via fetch no JS.
    return render_template('colecao.html')

# Página de detalhes de um produto específico
@main.route('/produto/<int:prod_id>')
def product_detail(prod_id):
    product = Product.query.get(prod_id)
    if not product or not product.is_active:
        return abort(404)

    # Renderiza a página visual do produto
    # O JS dentro de product.html também pode chamar a API pública pra buscar dados atualizados
    return render_template('product.html', product_id=prod_id)

# Página de checkout (o "carrinho" / confirmação da compra)
@main.route('/checkout/<int:prod_id>')
def checkout_page(prod_id):
    product = Product.query.get(prod_id)
    if not product or not product.is_active:
        return abort(404)

    # Essa página vai mostrar quantidade, preço total, botão "finalizar"
    # Você precisa ter um checkout.html que consome /api/public/products/<id>
    return render_template('checkout.html', product_id=prod_id)


# ----------------------------
# APIs públicas (dados lidos pelo front do cliente)
# Essas rotas NÃO exigem admin e podem ser usadas no fetch() do front
# ----------------------------

# Retorna todos os dados de um produto (para product.html e checkout.html)
@main.route('/api/public/products/<int:prod_id>', methods=['GET'])
def public_get_product(prod_id):
    product = Product.query.get(prod_id)
    if not product or not product.is_active:
        return jsonify({"message": "Produto não encontrado"}), 404

    return jsonify(product.to_dict()), 200


# Retorna dados da coleção específica
@main.route('/api/public/collections/<int:col_id>', methods=['GET'])
def public_get_collection(col_id):
    col = Collection.query.get(col_id)
    if not col:
        return jsonify({"message": "Coleção não encontrada"}), 404

    # Aqui usamos o to_dict() da Collection
    return jsonify(col.to_dict()), 200


# Retorna os produtos dessa coleção
@main.route('/api/public/collections/<int:col_id>/products', methods=['GET'])
def public_collection_products(col_id):
    # só produtos ativos dessa coleção
    products = Product.query.filter_by(collection_id=col_id, is_active=True).all()
    return jsonify([p.to_dict() for p in products]), 200


# ----------------------------
# API de checkout (POST)
# Debita estoque e retorna confirmação
# ----------------------------
@main.route('/api/checkout', methods=['POST'])
def process_checkout():
    """
    Espera JSON assim:
    {
        "product_id": 5,
        "quantity": 2
    }
    """
    data = request.get_json() or {}
    prod_id = data.get('product_id')
    qty = data.get('quantity')

    # validação básica
    if not prod_id or not qty:
        return jsonify({"message": "Dados incompletos. Informe product_id e quantity."}), 400

    # busca produto
    product = Product.query.get(prod_id)
    if not product or not product.is_active:
        return jsonify({"message": "Produto não encontrado"}), 404

    # garante que qty é número inteiro positivo
    try:
        qty = int(qty)
        if qty <= 0:
            return jsonify({"message": "Quantidade inválida"}), 400
    except ValueError:
        return jsonify({"message": "Quantidade inválida"}), 400

    # verifica estoque
    if product.stock < qty:
        return jsonify({"message": "Estoque insuficiente"}), 400

    # debita do estoque e salva
    product.stock -= qty
    db.session.commit()

    return jsonify({
        "message": f"Compra concluída! {qty} unidade(s) de {product.name} compradas.",
        "product_id": product.id,
        "remaining_stock": product.stock,
        "unit_price": float(product.price),
        "total_price": float(product.price) * qty,
    }), 200

@main.route('/carrinho')
def cart_page():
    return render_template('carrinho.html')
