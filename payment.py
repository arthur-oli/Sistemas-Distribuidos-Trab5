from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker, declarative_base

app = Flask(__name__)

Base = declarative_base()
engine = create_engine('sqlite:///payments.db')
Session = sessionmaker(bind=engine)

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    amount = Column(Float)
    refunded = Column(String)

Base.metadata.create_all(engine)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    session = Session()
    data = request.json
    new_payment = Payment(order_id=data['order_id'], amount=data['amount'])
    session.add(new_payment)
    session.commit()
    #return None
    return jsonify({'status': 'paid'}), 200

@app.route('/compensate_payment', methods=['POST'])
def compensate_payment():
    session = Session()
    data = request.json
    payment = session.query(Payment).filter_by(order_id=data['order_id']).one()
    if payment:
        payment.refunded = "To be refunded"
        session.commit()
        print(f"Payment was compensated after an error occurred. ${payment.amount} will be refunded on the product with ID = {payment.order_id}.")

    return jsonify({'status': 'compensated'}), 200

if __name__ == '__main__':
    app.run(port=5002)
