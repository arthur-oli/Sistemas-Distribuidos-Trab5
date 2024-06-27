from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.json
    order_id = create_order_service(data['client_name'])
    if order_id is None:
        return jsonify({'error': 'Order creation failed'}), 400

    stock_reserved = reserve_stock_service(order_id, data['product_id'], data['quantity'])

    if 'error' in stock_reserved.json:
        cancel_order_service(order_id)
        return jsonify({'error': 'Stock insufficient.'}), 400

    if not stock_reserved:
        compensate_stock_service(data['product_id'], data['quantity'])
        cancel_order_service(order_id)
        return jsonify({'error': 'Stock reservation failed'}), 400

    payment_processed = process_payment_service(order_id, data['amount'], stock_reserved['cost'])

    if 'error' in payment_processed.json:
        compensate_stock_service(data['product_id'], data['quantity'])
        cancel_order_service(order_id)
        return jsonify({'error': 'Stock insufficient.'}), 400

    if not payment_processed:
        compensate_payment_service(order_id)
        compensate_stock_service(data['product_id'], data['quantity'])
        cancel_order_service(order_id)
        return jsonify({'error': 'Payment processing failed'}), 400

    shipping_done = ship_order_service(order_id, data['address'])
    if not shipping_done:
        compensate_shipping_service(order_id)
        compensate_payment_service(order_id)
        compensate_stock_service(data['product_id'], data['quantity'])
        cancel_order_service(order_id)
        return jsonify({'error': 'Shipping failed'}), 400

    return jsonify({'order_id': order_id, 'status': 'COMPLETED'}), 200

def create_order_service(client_name):
    response = requests.post('http://localhost:5000/create_order', json={'client_name': client_name})
    if response.status_code == 201:
        return response.json()['order_id']
    return None

def reserve_stock_service(order_id, product_id, quantity):
    response = requests.post('http://localhost:5001/reserve_stock', json={'order_id': order_id, 'product_id': product_id, 'quantity': quantity})
    return response.status_code == 200

def process_payment_service(order_id, amount):
    response = requests.post('http://localhost:5002/process_payment', json={'order_id': order_id, 'amount': amount})
    return response.status_code == 200

def ship_order_service(order_id, address):
    response = requests.post('http://localhost:5003/ship_order', json={'order_id': order_id, 'address': address})
    return response.status_code == 200

def cancel_order_service(order_id):
    requests.post('http://localhost:5000/cancel_order', json={'order_id': order_id})

def compensate_stock_service(product_id, quantity):
    requests.post('http://localhost:5001/compensate_stock', json={'product_id': product_id, 'quantity': quantity})

def compensate_payment_service(order_id):
    requests.post('http://localhost:5002/compensate_payment', json={'order_id': order_id})

def compensate_shipping_service(order_id):
    requests.post('http://localhost:5003/compensate_shipping', json={'order_id': order_id})

if __name__ == '__main__':
    app.run(port=6000)
