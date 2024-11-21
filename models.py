from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Product(db.Model):
    __tablename__ = 'product'
    productID = db.Column(db.Integer, primary_key=True) 
    productName = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    categoryID = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Product {self.productName}>"

class Customer(db.Model):
    __tablename__ = 'customer'
    customerID = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    pwd = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    address = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f"<Customer {self.firstName} {self.lastName}>"
    
class Order(db.Model):
    __tablename__ = 'order'
    orderID = db.Column(db.Integer, primary_key=True)
    customerID = db.Column(db.Integer, db.ForeignKey('customer.customerID'), nullable=False)
    orderDate = db.Column(db.Date, nullable=False)
    totalAmount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(15), nullable=False)
    shippingAddress = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    updatedAt = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    customer = db.relationship('Customer', backref='orders', lazy=True)

    def __repr__(self):
        return f"<Order {self.orderID} for Customer {self.customerID}>"

class OrderItem(db.Model):
    __tablename__ = 'orderItem'
    orderItemID = db.Column(db.Integer, primary_key=True)
    orderID = db.Column(db.Integer, db.ForeignKey('order.orderID'), nullable=False)
    productID = db.Column(db.Integer, db.ForeignKey('product.productID'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', backref='order_items', lazy=True)
    product = db.relationship('Product', backref='order_items', lazy=True)

    def __repr__(self):
        return f"<OrderItem {self.orderItemID} for Order {self.orderID} and Product {self.productID}>"

class Payment(db.Model):
    __tablename__ = 'payment'
    paymentID = db.Column(db.Integer, primary_key=True)
    orderID = db.Column(db.Integer, db.ForeignKey('order.orderID'), nullable=False)
    paymentDate = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paymentMethod = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(15), nullable=False)

    order = db.relationship('Order', backref='payments', lazy=True)

    def __repr__(self):
        return f"<Payment {self.paymentID} for Order {self.orderID}>"

class Review(db.Model):
    __tablename__ = 'review'
    reviewID = db.Column(db.Integer, primary_key=True)
    productID = db.Column(db.Integer, db.ForeignKey('product.productID'), nullable=False)
    customerID = db.Column(db.Integer, db.ForeignKey('customer.customerID'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())

    product = db.relationship('Product', backref='reviews', lazy=True) 
    customer = db.relationship('Customer', backref='reviews', lazy=True)

    def __repr__(self):
        return f"<Review {self.reviewID} for Product {self.productID} by Customer {self.customerID}>"

 