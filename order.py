from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

app = Flask(__name__)

Base = declarative_base()
engine = create_engine('sqlite:///orders.db')
Session = sessionmaker(bind=engine)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    client_name = Column(String)
    status = Column(String)

Base.metadata.create_all(engine)

@app.route('/create_order', methods=['POST'])
def create_order():
    session = Session()
    data = request.json
    new_order = Order(client_name=data['client_name'], status='PENDING')
    session.add(new_order)
    # se der problema daqui pra trás, não vai ter commitado, por isso não precisa de compensação
    session.commit()
    #return None
    return jsonify({'order_id': new_order.id, 'status': new_order.status}), 201

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    session = Session()
    data = request.json
    order = session.query(Order).filter_by(id=data['order_id']).one()
    if order:
        order.status = 'CANCELLED'
        session.commit()
        print(f"Order with ID = {data['order_id']} got cancelled.")
        return jsonify({'status': 'cancelled'}), 200
    return jsonify({'error': 'order not found'}), 404

if __name__ == '__main__':
    app.run(port=5000)
