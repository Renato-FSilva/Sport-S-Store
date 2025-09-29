from app import db
from app.Models.collection_model import Collection
from app.Models.product_model import Product

# Collections
def add_collection(name, description=None):
    c = Collection(name=name, description=description)
    db.session.add(c)
    db.session.commit()
    return c

def edit_collection(collection_id, **fields):
    Collection.query.filter_by(id=collection_id).update(fields)
    db.session.commit()

def delete_collection(collection_id):
    Collection.query.filter_by(id=collection_id).delete()
    db.session.commit()

def list_collections():
    return Collection.query.all()

# Products
def add_product(name, price, image_filename=None, description=None, collection_id=None):
    p = Product(name=name, price=price, image=image_filename, description=description, collection_id=collection_id)
    db.session.add(p)
    db.session.commit()
    return p

def edit_product(product_id, **fields):
    Product.query.filter_by(id=product_id).update(fields)
    db.session.commit()

def delete_product(product_id):
    Product.query.filter_by(id=product_id).delete()
    db.session.commit()

def list_products(collection_id=None):
    q = Product.query
    if collection_id:
        q = q.filter_by(collection_id=collection_id)
    return q.all()