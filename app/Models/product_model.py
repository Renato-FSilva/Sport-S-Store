from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from app import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    sku = db.Column(db.String(100), nullable=True, unique=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    currency = db.Column(db.String(3), nullable=False, default="BRL")
    stock = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    image = db.Column(db.String(255), nullable=True)  # caminho da imagem

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Product id={self.id} name={self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "description": self.description,
            "price": float(self.price) if isinstance(self.price, Decimal) else self.price,
            "currency": self.currency,
            "stock": self.stock,
            "is_active": self.is_active,
            "image": self.image,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
