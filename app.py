from flask import Flask, render_template, request, redirect, flash, jsonify
from http import HTTPStatus
import pymysql, hashlib
from dbconfig import get_db_connection
from dbinfo import secretKey

app = Flask(__name__)

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
    if (request.method == 'GET'):
        return render_template('login.html')
    elif (request.method == 'POST'):
        if (checkCredentials(request)):
            return redirect('/home/')
        return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if (request.method == 'GET'):
        return render_template('signup.html')
    elif (request.method == 'POST'):
        trySignUp(request)
        return redirect('/')

@app.route('/home/', methods=['GET'])
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
def modify_product():
    if (request.method == 'GET'):
        return render_template('modifyProduct.html')
    elif (request.method == 'POST'):
        pass


@app.route('/home/show_tickets', methods=['GET'])
def show_tickets():
    return render_template('showTickets.html')

@app.route('/home/delete_product', methods=['GET', 'POST'])
def delete_product():
    if request.method == 'GET':
        # Mostrar los productos disponibles para eliminar
        # Asegúrate de que la función getProducts() recupere correctamente los productos de la base de datos
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT * FROM Product")
            products = cursor.fetchall()  # Recupera todos los productos
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


@app.route('/home/ticket', methods=['GET', 'POST'])
def ticket():
    if (request.method == 'GET'):
        return render_template('ticket.html')
    elif (request.method == 'POST'):
        pass

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
