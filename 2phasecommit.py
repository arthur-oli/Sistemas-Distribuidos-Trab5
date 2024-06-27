from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class OrderStatus(PyEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    stock = Column(Integer)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    status = Column(Enum(OrderStatus))
    product = relationship("Product")

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    amount = Column(Float)
    order = relationship("Order")

class Shipping(Base):
    __tablename__ = 'shipping'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    address = Column(String)
    status = Column(String)
    order = relationship("Order")

# setup do banco
engine = create_engine('sqlite:///ecommerce.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def two_phase_commit(order_id, payment_amount):
    session = Session()
    
    try:
        # Fase 1: preparacao
        order = session.query(Order).filter_by(id=order_id).with_for_update().one()
        product = session.query(Product).filter_by(id=order.product_id).with_for_update().one()
        
        if product.stock < order.quantity:
            raise ValueError("Insufficient stock")

        payment = Payment(order_id=order_id, amount=payment_amount)
        session.add(payment)
        
        # Fase 2: commit
        order.status = OrderStatus.PAID
        product.stock -= order.quantity
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def process_shipping(order_id, address):
    session = Session()
    try:
        order = session.query(Order).filter_by(id=order_id).one()
        if order.status != OrderStatus.PAID:
            raise ValueError("Order not paid")

        shipping = Shipping(order_id=order_id, address=address, status="SHIPPED")
        session.add(shipping)
        
        order.status = OrderStatus.SHIPPED
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def list_products():
    session = Session()
    products = session.query(Product).all()
    for product in products:
        print(f"ID: {product.id}, Name: {product.name}, Price: {product.price}, Stock: {product.stock}")
    session.close()

def list_orders():
    session = Session()
    orders = session.query(Order).all()
    for order in orders:
        print(f"Order ID: {order.id}, Product ID: {order.product_id}, Quantity: {order.quantity}, Status: {order.status}")
    session.close()

def list_payments():
    session = Session()
    payments = session.query(Payment).all()
    for payment in payments:
        print(f"Payment ID: {payment.id}, Order ID: {payment.order_id}, Amount: {payment.amount}")
    session.close()

def list_shipping():
    session = Session()
    shippings = session.query(Shipping).all()
    for shipping in shippings:
        print(f"Shipping ID: {shipping.id}, Order ID: {shipping.order_id}, Address: {shipping.address}, Status: {shipping.status}")
    session.close()

if __name__ == '__main__':
    session = Session()

    # novo produto
    new_product = Product(name = 'Notebook', price=1000.0, stock=10)
    session.add(new_product)
    session.commit()

    # novo pedido
    new_order = Order(product=new_product, quantity=1, status=OrderStatus.PENDING)
    session.add(new_order)
    session.commit()

    # processamento de pagamento e envio
    try:
        two_phase_commit(order_id=new_order.id, payment_amount=new_product.price)
        print("Order paid successfully")
        process_shipping(order_id = new_order.id, address = 'Rua Exemplo 100, Curitiba, PR')
        print("Order shipped successfully")
    except Exception as e:
        print(f"Failed to process order: {e}")

    print("Products:")
    list_products()
    print("\nOrders:")
    list_orders()
    print("\nPayments:")
    list_payments()
    print("\nShipping:")
    list_shipping()
