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
    if (request.method == 'GET'):
        return render_template('addProduct.html')
    elif (request.method == 'POST'):
        pass

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
    if (request.method == 'GET'):
        return render_template('deleteProduct.html')
    elif (request.method == 'POST'):
        pass

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
