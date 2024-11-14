from flask import Flask, render_template, request, redirect, flash, jsonify, url_for, session
from flask_login import LoginManager, login_user, UserMixin
from http import HTTPStatus
import pymysql, hashlib
from auth import login_required, admin_required
from dbconfig import get_db_connection
from dbinfo import secretKey

app = Flask(__name__)

class User(UserMixin):
    def __init__(self, user_id, name, is_owner):
        self.id = user_id
        self.name = name
        self.is_owner = is_owner

    def get_id(self):
        return str(self.id)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT user_id, name, is_owner FROM User WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if user:
            return User(user['user_id'], user['name'], user['is_owner'])
        return None
    
    finally:
        cursor.close()
        connection.close()

app.secret_key = secretKey

def getUsers():
    connection = get_db_connection()
    if (connection is None):
        return render_template("error.html")
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT * FROM User")
        usersFromDb = cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        usersFromDb = []
    finally:
        cursor.close()
        connection.close()
    
    return usersFromDb

def getProducts():
    connection = get_db_connection()
    if (connection is None):
        return render_template("error.html")
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute('''SELECT p.name, pt.name as product_type, p.description, p.barcode, p.unit_price, s.available, s.minimum
                        FROM Product p
                        INNER JOIN Product_Type pt ON pt.type_id = p.type_id
                        INNER JOIN Stock s ON s.stock_id = p.stock_id;''')
        productsFromDb = cursor.fetchall()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        productsFromDb = []
    finally:
        cursor.close()
        connection.close()

    return productsFromDb

def checkCredentials(request: any):
    user = request.form['username']
    password = request.form['password']

    hashed_pass = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'', 100000).hex()

    connection = get_db_connection()
    if (connection is None):
        return render_template("error.html")
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT name FROM User WHERE name = %s AND password = %s", (user, hashed_pass))
        userDb = cursor.fetchone()

        if (userDb):
            flash('Se inició sesión correctamente')
            return True
        flash(f'Usuario o contraseña incorrecto.')
        return False
    except pymysql.MySQLError as e:
        print(f'Error: {e}')
        flash(f'Error al iniciar sesión: {e}')
    finally:
        cursor.close()
        connection.close()

def trySignUp(request: any) -> bool:
    user = request.form['username']
    password = request.form['password']
    is_owner = int(request.form['isOwner'])

    hashed_pass = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'', 100000).hex()

    connection = get_db_connection()
    if (connection is None):
        return render_template("error.html")
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("INSERT INTO User (name, password, is_owner) VALUES (%s, %s, %s)", (user, hashed_pass, is_owner))
        connection.commit()
        flash(f'Usuario creado correctamente')
    except pymysql.MySQLError as e:
        print(f'Error: {e}')
        flash(f'Error al crear el usuario: {e}')
    finally:
        cursor.close()
        connection.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    if (request.method == 'GET'):
        return render_template('login.html')
    
    elif (request.method == 'POST'):
        if not all(k in request.form for k in ['username', 'password']):
            flash('Por favor complete todos los campos')
            return redirect(url_for('login'))

        try:
            if checkCredentials(request):
                connection = get_db_connection()
                if connection is None:
                    return render_template("error.html")
                
                cursor = connection.cursor(pymysql.cursors.DictCursor)
                
                try:
                    cursor.execute("""
                        SELECT user_id, name, is_owner 
                        FROM User 
                        WHERE name = %s
                    """, (request.form['username'],))
                    
                    user_data = cursor.fetchone()
                    
                    if user_data:
                        session['user_id'] = user_data['user_id']
                        session['username'] = user_data['name']
                        session['is_owner'] = bool(user_data['is_owner'])
                        
                        return redirect(url_for('home'))
                
                finally:
                    cursor.close()
                    connection.close()
            
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            flash('Ocurrió un error durante el inicio de sesión')
            return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if (request.method == 'GET'):
        return render_template('signup.html')
    elif (request.method == 'POST'):
        trySignUp(request)
        return redirect('/')

@app.route('/home/', methods=['GET'])
@login_required
def home():
    return render_template('home.html', products=getProducts())

@app.route('/home/add_product', methods=['GET', 'POST'])
def new_product():
    if request.method == 'GET':
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT type_id, name FROM Product_Type")
            product_types = cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"Error al obtener tipos de producto: {e}")
            product_types = []
        finally:
            cursor.close()
            connection.close()

        return render_template('addProduct.html', product_types=product_types)
    
    elif request.method == 'POST':
        name = request.form['name']
        type_id = request.form['type_id']
        description = request.form['description']
        barcode = request.form['barcode']
        unit_price = request.form['unit_price']
        stock = request.form['stock']

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("INSERT INTO Stock (available) VALUES (%s)", (stock,))
            stock_id = cursor.lastrowid

            cursor.execute('''INSERT INTO Product (name, type_id, description, barcode, unit_price, stock_id)
                              VALUES (%s, %s, %s, %s, %s, %s)''', (name, type_id, description, barcode, unit_price, stock_id))

            connection.commit()
            flash('Producto agregado exitosamente.')
            return redirect('/home/')
        except pymysql.MySQLError as e:
            print(f"Error al agregar producto: {e}")
            flash(f"Error al agregar el producto: {e}")
            return redirect('/home/add_product')
        finally:
            cursor.close()
            connection.close()

@app.route('/home/modify_product', methods=['GET', 'POST'])
@login_required
def modify_product():
    if request.method == 'GET':
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute('''SELECT p.product_id, p.name, p.type_id, p.description, p.barcode, p.unit_price, s.available, s.minimum, p.creation_date, p.modification_date, s.stock_id
                            FROM Product p
                            INNER JOIN Stock s ON s.stock_id = p.stock_id;''')
            products = cursor.fetchall()
            print(products)
            return render_template('modifyProduct.html', products=products)
        except pymysql.MySQLError as e:
            print(f"Error al obtener los productos: {e}")
            flash("Error al cargar los productos")
            return redirect('/home/')
        finally:
            cursor.close()
            connection.close()

    elif request.method == 'POST':
        product_id = request.form['product_id']
        name = request.form['name']
        type_id = request.form['type_id']
        description = request.form['description']
        barcode = request.form['barcode']
        unit_price = request.form['unit_price']
        s_available = request.form['stock_available']
        s_minimum = request.form['stock_minimum']
        s_id = request.form['stock_id']

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("UPDATE Stock SET available=%s, minimum=%s WHERE stock_id=%s", (s_available, s_minimum, s_id))
            cursor.execute("UPDATE Product SET name=%s, type_id=%s, description=%s, barcode=%s, unit_price=%s WHERE product_id=%s", (name, type_id, description, barcode, unit_price, product_id))
            connection.commit()
            flash("Producto actualizado correctamente")
            return redirect('/home/modify_product')
        except pymysql.MySQLError as e:
            print(f"Error al actualizar el producto: {e}")
            flash("Error al actualizar el producto")
            return redirect('/home/modify_product')
        finally:
            cursor.close()
            connection.close()

@app.route('/api/payment-methods', methods=['GET'])
def get_payment_methods():
    connection = get_db_connection()
    cursor = connection.cursor()
        
    try:
        cursor.execute("SELECT payment_id, name FROM Payment_Method")
        methods = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify(methods)
    except Exception as e:
        print(f"Error fetching payment methods: {str(e)}")
        return jsonify({'error': 'Failed to fetch payment methods'}), 500

@app.route('/api/checkout', methods=['POST'])
@login_required
def checkout():
    connection = None
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        data = request.get_json()
        
        #if not data or 'products' not in data or not data['products']:
        #    return jsonify({'error': 'No items provided'}), 400

        # Start transaction
        connection.begin()

        # Insert ticket
        cursor.execute("""
            INSERT INTO Ticket (user_id, payment_id, amount)
            VALUES (%s, %s, %s)
        """, (session['user_id'], data['payment_id'], data['amount']))
        
        # Get the ticket_id
        ticket_id = cursor.lastrowid

        # Process each product
        for product in data['products']:
            # Insert into Ticket_Product
            cursor.execute("""
                INSERT INTO Ticket_Product (ticket_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (ticket_id, product['product_id'], product['quantity']))

            # Get stock_id for the product
            cursor.execute("""
                SELECT stock_id FROM Product 
                WHERE product_id = %s
            """, (product['product_id'],))
            
            result = cursor.fetchone()
            if not result:
                raise Exception(f"Product not found: {product['product_id']}")
            
            stock_id = result[0]

            # Verify stock availability
            cursor.execute("""
                SELECT available, minimum FROM Stock 
                WHERE stock_id = %s
            """, (stock_id,))
            
            stock = cursor.fetchone()
            if not stock:
                raise Exception(f"Stock not found for product: {product['product_id']}")
            
            available, minimum = stock
            new_quantity = available - product['quantity']

            if new_quantity < 0:
                raise Exception(f"Insufficient stock for product_id: {product['product_id']}")
            
            if new_quantity < minimum:
                print(f"Warning: Stock below minimum for product_id: {product['product_id']}")

            # Update stock
            cursor.execute("""
                UPDATE Stock 
                SET available = available - %s
                WHERE stock_id = %s
            """, (product['quantity'], stock_id))

        # Commit
        connection.commit()

        return jsonify({
            'message': 'Checkout successful',
            'ticket_id': ticket_id
        }), 200

    except Exception as e:
        # Rollback
        if connection:
            connection.rollback()
        print(f"Error during checkout: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        connection.close()

@app.route('/home/ticket', methods=['GET', 'POST'])
def ticket():
    if (request.method == 'GET'):
        return render_template('ticket.html')
    elif (request.method == 'POST'):
        pass

@app.route('/home/show_tickets', methods=['GET'])
def show_tickets():
    return render_template('showTickets.html')

@app.route('/home/delete_product', methods=['GET', 'POST'])
def delete_product():
    if request.method == 'GET':
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT * FROM Product")
            products = cursor.fetchall()
            return render_template('deleteProduct.html', products=products)
        except pymysql.MySQLError as e:
            print(f"Error al obtener los productos: {e}")
            flash("Error al cargar los productos")
            return redirect('/home/')
        finally:
            cursor.close()
            connection.close()
    
    elif request.method == 'POST':
        product_id = request.form['product_id']
        connection = get_db_connection()
        cursor = connection.cursor()

        try:            
            cursor.execute("DELETE FROM Product WHERE product_id = %s", (product_id,))
            connection.commit() 
            flash("Producto eliminado correctamente")
            return redirect('/home/')
        except pymysql.MySQLError as e:
            print(f"Error al eliminar el producto: {e}")
            flash("Error al eliminar el producto")
            return redirect('/home/')
        finally:
            cursor.close()
            connection.close()

@app.route('/get_product_by_name/<string:name>', methods=['GET'])
def get_product_by_name(name: str):
    connection = get_db_connection()
    if (connection is None):
        return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), HTTPStatus.SERVICE_UNAVAILABLE
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute('''SELECT p.name, pt.name as product_type, p.description, p.barcode, p.unit_price, s.available, s.minimum
                        FROM Product p
                        INNER JOIN Product_Type pt ON pt.type_id = p.type_id
                        INNER JOIN Stock s ON s.stock_id = p.stock_id
                        WHERE p.name = %s;''', (name,))
        
        product = cursor.fetchone()
        
        if product is None:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), HTTPStatus.NOT_FOUND
        
        return jsonify({
            'success': True,
            'data': product
        }), HTTPStatus.OK
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        cursor.close()
        connection.close()

@app.route('/get_product_by_barcode/<string:barcode>', methods=['GET'])
def get_product_by_barcode(barcode: str):
    connection = get_db_connection()
    if (connection is None):
        return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), HTTPStatus.SERVICE_UNAVAILABLE
            
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute('''SELECT p.name, pt.name as product_type, p.description, p.barcode, p.unit_price, s.available, s.minimum
                        FROM Product p
                        INNER JOIN Product_Type pt ON pt.type_id = p.type_id
                        INNER JOIN Stock s ON s.stock_id = p.stock_id
                        WHERE p.barcode = %s;''', (barcode,))
       
        product = cursor.fetchone()
       
        if product is None:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), HTTPStatus.NOT_FOUND
       
        return jsonify({
            'success': True,
            'data': product
        }), HTTPStatus.OK
        
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({
            'success': False,
            'error': f'Database error: {str(e)}'
        }), HTTPStatus.INTERNAL_SERVER_ERROR
        
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)
