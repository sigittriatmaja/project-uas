from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = '8f42a73054b1749f8f58848be5e6502c'

# Konfigurasi MySQL
db_config = {
    'host': 'n1cgq.h.filess.io',
    'port': 3307,
    'user': 'kopi_beautiful',
    'password': '6c79a542ddb254cb2414df18d536af99f3de81b2',
    'database': 'kopi_beautiful'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Route untuk login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        cursor.close()
        conn.close()

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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM items')
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('home.html', username=session['username'], items=items)
    return redirect(url_for('login'))

# Route untuk tambah item
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO items (name, description) VALUES (%s, %s)', (name, description))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Item added successfully!', 'success')
            return redirect(url_for('home'))
        return render_template('add.html')
    return redirect(url_for('login'))

# Route untuk edit item
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            cursor.execute('UPDATE items SET name = %s, description = %s WHERE id = %s', (name, description, id))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Item updated successfully!', 'success')
            return redirect(url_for('home'))
        cursor.execute('SELECT * FROM items WHERE id = %s', (id,))
        item = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit.html', item=item)
    return redirect(url_for('login'))

# Route untuk hapus item
@app.route('/delete/<int:id>')
def delete(id):
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM items WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Item deleted successfully!', 'success')
        return redirect(url_for('home'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
