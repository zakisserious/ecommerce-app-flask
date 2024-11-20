from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

    
@app.route('/admin/dashboard')
def dashboard():
    product_count = Product.query.count()
    products = Product.query.all()
    return render_template("/admin/dashboard.html",product_count=product_count, product=products)

@app.route('/admin/product')
def product():
    search_query = request.args.get('searchProduct', '')  
    if search_query:
        products = Product.query.filter(
            Product.productName.ilike(f'%{search_query}%') | 
            Product.productID.ilike(f'%{search_query}%')
        ).all()  
    else:
        products = Product.query.all()

    return render_template("/admin/product.html", product=products)

@app.route('/add', methods=["GET", "POST"])
def add_product():
    new_product = Product(
        productName= request.form['p_name'],
        description= request.form['p_desc'],
        price= float(request.form['p_price']),
        stock= int(request.form['p_stock']),
        categoryID= int(request.form['p_category'])
    )

    try:
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('product'))
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {e}"

@app.route('/update', methods=["POST"])
def update_product():
    p_ID = request.form.get('p_ID')
    
    if p_ID:
        product = Product.query.get_or_404(p_ID)

        if 'btndelete' in request.form:
            try:
                db.session.delete(product)
                db.session.commit()
                return redirect(url_for('product'))
            except Exception as e:
                db.session.rollback()
                return f"An error occurred while deleting the product: {e}", 500

        elif 'btnedit' in request.form:
            try:
                product.productName = request.form['p_name']
                product.description = request.form['p_desc']
                product.price = float(request.form['p_price'])
                product.stock = int(request.form['p_stock'])
                db.session.commit()
                return redirect(url_for('product'))
            except Exception as e:
                db.session.rollback()
                return f"An error occurred while updating the product: {e}", 500
    else:
        return "Product ID not provided", 400
    
@app.route('/admin/review')
def review():
    search_query = request.args.get('rating', '')  
    if search_query:
        review = Review.query.filter(
            Review.rating.ilike(f'%{search_query}%')
        ).all()  
    else:
        review = Review.query.all()
    return render_template("/admin/review.html", review=review)

@app.route('/admin/customer')
def customer():
    search_query = request.args.get('searchCust', '')  
    if search_query:
        customer = Customer.query.filter(
            Customer.customerID.ilike(f'%{search_query}%') | 
            Customer.firstName.ilike(f'%{search_query}%') |
            Customer.lastName.ilike(f'%{search_query}%')
        ).all()  
    else:
        customer = Customer.query.all()
    return render_template("/admin/customer.html", customer=customer)

@app.route('/admin/order')
def order():
    search_query = request.args.get('searchOrder', '')  
    if search_query:
        orders = Order.query.filter(
            Order.orderID.ilike(f'%{search_query}%')
        ).all()  
        orderItems = OrderItem.query.filter(OrderItem.orderID.in_([order.orderID for order in orders])).all()
    else:
        orders = Order.query.all()
        orderItems = OrderItem.query.all()
    
    return render_template("/admin/order.html", order=orders, orderItem=orderItems)

@app.route('/admin/transaction')
def transaction():
    search_query = request.args.get('searchPayment', '')  
    if search_query:
        payment = Payment.query.filter(
            Payment.paymentID.ilike(f'%{search_query}%')
        ).all()  
    else:
        payment = Payment.query.all()
    return render_template("/admin/transaction.html", payment=payment)

if __name__ == '__main__':
    app.run(debug=True)