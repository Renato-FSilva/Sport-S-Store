from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from app import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    # Dados principais
    name = db.Column(db.String(255), nullable=False, index=True)
    sku = db.Column(db.String(100), nullable=True, unique=True)
    description = db.Column(db.Text, nullable=True)

    # Preço
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    currency = db.Column(db.String(3), nullable=False, default="BRL")

    # Estoque
    stock = db.Column(db.Integer, nullable=False, default=0)

    # Status
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Imagem
    image = db.Column(db.String(255), nullable=True)

    # Relacionamento com coleção
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    collection = db.relationship(
        'Collection',
        backref=db.backref('products', lazy=True)
    )

    # Auditoria
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Product id={self.id} name={self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        # garante que price vai como float simples pro JSON
        if self.price is None:
            price_value = 0.0
        elif isinstance(self.price, Decimal):
            price_value = float(self.price)
        else:
            price_value = float(self.price)

        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "description": self.description,

            # preço formatado pro front
            "price": price_value,
            "currency": self.currency,

            # ESTOQUE REAL que o dashboard precisa
            "stock": int(self.stock) if self.stock is not None else 0,

            "is_active": self.is_active,
            "image": self.image,

            "collection_id": self.collection_id,
            "collection_name": self.collection.name if self.collection else None,

            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
