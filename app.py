from flask import Flask, render_template, request, redirect, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# Configuración de MySQL
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'apolo9404'
app.config['MYSQL_DB'] = 'tienda'
app.config['MYSQL_HOST'] = 'localhost'

app.secret_key = 'supersecretkey'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template("frm.html")

@app.route('/add_product', methods=['POST', 'GET'])
def add_product():
    try:
        if request.method == "POST":
            name = request.form['name']
            price = request.form['price']
            quantity = request.form['quantity']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "INSERT INTO productos (name, price, quantity) VALUES (%s, %s, %s)"
            values = (name, price, quantity)
            cursor.execute(sql, values)
            mysql.connection.commit()
            cursor.close()

            flash('Producto agregado exitosamente')
            return redirect('/')
    except Exception as e:
        print(e)
    return render_template("frm.html")

@app.route('/show_products')
def show_products():
    products = []
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM productos")
        products = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(e)
    return render_template("out.html", productos=products)

@app.route('/delete_product/<int:id>', methods=['GET'])
def delete_product(id):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "DELETE FROM productos WHERE id = %s"
        cursor.execute(sql, (id,))
        mysql.connection.commit()
        cursor.close()

        flash('Producto eliminado exitosamente')
    except Exception as e:
        print(e)
    return redirect('/show_products')

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = None
    if request.method == 'GET':
        # Obtener los detalles actuales del producto
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
        product = cursor.fetchone()
        cursor.close()
        return render_template('edit_product.html', product=product)
    
    elif request.method == 'POST':
        # Obtener los nuevos valores del formulario
        new_price = request.form['price']
        new_quantity = request.form['quantity']
        
        # Actualizar los datos del producto en la base de datos
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "UPDATE productos SET price = %s, quantity = %s WHERE id = %s"
        cursor.execute(sql, (new_price, new_quantity, id))
        mysql.connection.commit()
        cursor.close()

        flash('Producto actualizado exitosamente')
        return redirect('/show_products')

if __name__ == "__main__":
    app.run(debug=True)
