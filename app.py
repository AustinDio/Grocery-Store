from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
db = SQLAlchemy(app)

class GroceryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer)
    category_name = db.Column(db.String(100))
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    image_url = db.Column(db.String(200))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(10), default='N/A') 

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), default='N/A')
    image_url = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), nullable=True)
    category = db.relationship('Category', backref='products')



class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product', backref='cart_items')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)


@app.route('/')
def mainpg():
    return render_template('intro.html')

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/adminpage')
def index():
    return redirect(url_for('show_categories'))

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
           
            unit = 'N/A'  
            category = Category(name=name, unit=unit)
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('show_categories'))
    return render_template('add_category.html')



@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        image_url = request.form['image_url']
        category_id = int(request.form['category'])
        unit = request.form['unit']  
        product = Product(name=name, quantity=quantity, price=price, image_url=image_url, category_id=category_id, unit=unit)  # Include unit value in the Product creation
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('show_categories'))
    return render_template('add_product.html', categories=categories)

@app.route('/categories', methods=['GET'])
def show_categories():
    search = request.args.get('search')
    categories = Category.query.all()

    return render_template('categories.html', categories=categories, search=search)

@app.route('/update_category/<int:category_id>', methods=['GET', 'POST'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        new_name = request.form['name']
        category.name = new_name
        db.session.commit()
        return redirect(url_for('show_categories'))
    return render_template('update_category.html', category=category)

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.quantity = int(request.form['quantity'])
        product.price = float(request.form['price'])
        product.image_url = request.form['image_url']
        db.session.commit()
        return redirect(url_for('show_categories'))

    return render_template('update_product.html', product=product)


@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('show_categories'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('show_categories'))

@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/user_page', methods=['GET', 'POST'])
def user_page():
    search_product = request.args.get('search_product')
    search_category = request.args.get('search_category')

    products = Product.query.all()
    categories = Category.query.all()

    if search_product:
        products = Product.query.filter(Product.name.ilike(f'%{search_product}%')).all()

    if search_category:
        categories = Category.query.filter(Category.name.ilike(f'%{search_category}%')).all()

    return render_template('user.html', products=products, categories=categories,
                           search_product=search_product, search_category=search_category)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form['quantity'])
    if quantity > product.quantity:
        return "Error: Quantity selected exceeds available quantity."

    user_id = 1  
    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product.id).first()

    if cart_item:
       
        cart_item.quantity = quantity
    else:
       
        cart_item = CartItem(user_id=user_id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return redirect(url_for('user_page'))

@app.route('/cart')
def view_cart():
    user_id = 1  
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:cart_item_id>', methods=['POST'])
def remove_from_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    product = Product.query.get_or_404(cart_item.product_id)
    product.quantity += cart_item.quantity 
    db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user_id = 1 
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    for cart_item in cart_items:
        product = Product.query.get_or_404(cart_item.product_id)
        product.quantity -= cart_item.quantity

        if product.quantity <= 0:
            product.quantity = 0
            product.available = False

        db.session.delete(cart_item)

    db.session.commit()
    return render_template('payment.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)