from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    cart = db.relationship('CartItem', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])  # Agrega methods=['POST'] aquí
@login_required
def add_to_cart(product_id):
    if request.method == 'POST':
        # Lógica para agregar el producto al carrito
        flash('Producto agregado al carrito', 'success')
        return redirect(url_for('index'))
    else:
        # Manejar el caso en que no se realice una solicitud POST
        return redirect(url_for('index'))  # Redirige a la página de inicio



@app.route('/cart')
@login_required
def view_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', items=items)

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Product removed from cart!', 'success')
    return redirect(url_for('view_cart'))

@app.route('/checkout')
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template('checkout.html', items=items, total=total)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user is None:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('An account with this email already exists.', 'danger')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
         
    app.run(host='localhost', port=5000, debug=True)




