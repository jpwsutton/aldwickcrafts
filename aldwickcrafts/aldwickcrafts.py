import sqlite3
from flask import (Flask, request, session, g, redirect, url_for, abort,
render_template, flash)
import os

"""
This is the application code for aldwickcrafts.co.uk

Developed by James Sutton: jsutton.co.uk 2014
"""

# Create the application
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'aldwickcrafts.db'),
    DEBUG=True,
    SECRET_KEY='development_key',
    USERNAME='admin',
    PASSWORD='default'
    ))
app.config.from_envvar('ALDWCKCFT_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    """Creates the database tables"""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.route('/')
def show_about():
    return render_template('about.html')

@app.route('/home')
def show_products():
    db = get_db()
    cur = db.execute('select name, description, category, image, price from products order by id desc')
    products = cur.fetchall()
    return render_template('show_products.html', products=products)

@app.route('/add', methods=['POST'])
def add_product():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into products(name, description, category, image, price) values (?,?,?,?,?)',
            [request.form['name'], request.form['description'], request.form['category'], request.form['image'], request.form['price']])
    db.commit()
    flash('New Product was successfully posted')
    return redirect(url_for('show_products'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_products'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_products'))



@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()





if __name__ == '__main__':
    app.run()
