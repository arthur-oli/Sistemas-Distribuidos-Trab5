from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

app = Flask(__name__)

Base = declarative_base()
engine = create_engine('sqlite:///stock.db')
Session = sessionmaker(bind=engine)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    stock = Column(Integer)
    cost = Column(Integer)

# criando um estoque básico para iniciar
session = Session()
Base.metadata.create_all(engine)
if (not session.query(Product).filter_by(id = 1).first()):
    new_stock = Product(id = 1, name = "Notebook", stock = 2500, cost = 1000)
    session.add(new_stock)
    session.commit()

@app.route('/reserve_stock', methods=['POST'])
def reserve_stock():
    session = Session()
    data = request.json
    product = session.query(Product).filter_by(id=data['product_id']).first()
    if product and product.stock >= data['quantity']:
        product.stock -= data['quantity']
        session.commit()
        #return None
        return jsonify({'status': 'reserved', 'cost': product.cost}), 200
    return jsonify({'error': 'insufficient stock'}), 400

@app.route('/compensate_stock', methods=['POST'])
def compensate_stock():
    session = Session()
    data = request.json
    product = session.query(Product).filter_by(id=data['product_id']).one()
    if product:
        product.stock += data['quantity']
        session.commit()
        print(f"Stock was compensated after an error occurred. {data['quantity']} units of the product with ID = {data['product_id']} were readded.")

    return jsonify({'status': 'compensated'}), 200

if __name__ == '__main__':
    app.run(port=5001)
