from flask import Flask, render_template, request, redirect, flash
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
        cursor.execute("SELECT * FROM Product_Type")
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
        flash('Error al iniciar sesión')
        return False
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        flash('Error al iniciar sesión')
    finally:
        cursor.close()
        connection.close()  

@app.route('/', methods=['GET', 'POST'])
def login():
    if (request.method == 'GET'):
        return render_template('login.html')
    if (request.method == 'POST'):
        if (checkCredentials(request)):
            return redirect('/home/')
        return redirect('/')

@app.route('/home/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
