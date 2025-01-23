from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = '8f42a73054b1749f8f58848be5e6502c'

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'n1cgq.h.filess.io'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'kopi_beautiful'
app.config['MYSQL_PASSWORD'] = '6c79a542ddb254cb2414df18d536af99f3de81b2'
app.config['MYSQL_DB'] = 'kopi_beautiful'

mysql = MySQL(app)

# Route untuk login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials', 'danger')
    return render_template('login.html')

# Route untuk logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Route untuk halaman utama (CRUD)
@app.route('/home')
def home():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM items')
        items = cursor.fetchall()
        return render_template('home.html', username=session['username'], items=items)
    return redirect(url_for('login'))

# Route untuk tambah item
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO items (name, description) VALUES (%s, %s)', (name, description))
            mysql.connection.commit()
            flash('Item added successfully!', 'success')
            return redirect(url_for('home'))
        return render_template('add.html')
    return redirect(url_for('login'))

# Route untuk edit item
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            cursor.execute('UPDATE items SET name = %s, description = %s WHERE id = %s', (name, description, id))
            mysql.connection.commit()
            flash('Item updated successfully!', 'success')
            return redirect(url_for('home'))
        cursor.execute('SELECT * FROM items WHERE id = %s', (id,))
        item = cursor.fetchone()
        return render_template('edit.html', item=item)
    return redirect(url_for('login'))

# Route untuk hapus item
@app.route('/delete/<int:id>')
def delete(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM items WHERE id = %s', (id,))
        mysql.connection.commit()
        flash('Item deleted successfully!', 'success')
        return redirect(url_for('home'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
