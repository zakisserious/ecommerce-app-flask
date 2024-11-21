from flask import  render_template, request, redirect, url_for

from models import Product , Customer,Order,OrderItem,Payment,Review,db
from flask import Flask

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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