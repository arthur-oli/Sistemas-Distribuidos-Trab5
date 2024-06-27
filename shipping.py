from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

app = Flask(__name__)

Base = declarative_base()
engine = create_engine('sqlite:///shipping.db')
Session = sessionmaker(bind=engine)

class Shipment(Base):
    __tablename__ = 'shipments'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    address = Column(String)

Base.metadata.create_all(engine)

@app.route('/ship_order', methods=['POST'])
def ship_order():
    session = Session()
    data = request.json
    new_shipment = Shipment(order_id=data['order_id'], address=data['address'])
    session.add(new_shipment)
    session.commit()
    #return None
    return jsonify({'status': 'shipped'}), 200

@app.route('/compensate_shipping', methods=['POST'])
def compensate_shipping():
    session = Session()
    data = request.json
    shipment = session.query(Shipment).filter_by(order_id=data['order_id']).one()
    if shipment:
        session.delete(shipment)
        session.commit()
    return jsonify({'status': 'compensated'}), 200

if __name__ == '__main__':
    app.run(port=5003)
