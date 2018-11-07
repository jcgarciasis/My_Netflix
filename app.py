# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_pymongo import pymongo


app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='1234',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

#@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        db = get_db()
        cur = db.execute('select username, pass from users where username = ?',[request.form['username']]) #cursor
        users = cur.fetchall()
        if users == []:
            error = 'Invalid username'
        elif request.form['password'] != users[0]['pass']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if not session.get('logged_in'):
        if request.method == 'POST':
            db = get_db()
            db.execute('insert into users (username, pass, payment) values (?, ?, ?)',[request.form['username'], request.form['password'],False])
            db.commit()
            return redirect(url_for("login"))
        return render_template('register.html', error=error)
    else:
        return redirect(url_for("show_entries"))

@app.route('/catalogue', methods=['GET', 'POST'])
def catalogue():
    error = None
    db = get_db()
    #cur = db.execute('''SELECT payment FROM users WHERE username = ?''',session['username'])
    cur = db.execute('''SELECT payment FROM users WHERE username=?''',[session['username']])
    payment = cur.fetchall()
    var = payment[0]
    payments = var['payment']
    #test = payment[0]['payment']
    if payments == "1":
        if request.method == 'POST':
        #if __name__ == '__main__':
        #Connection to MongoDB
        #try:
            conn = pymongo.MongoClient("mongodb://35.227.172.49/trailers",80)
            print("Connection established successfully!!!")
            # except pymongo.errors.ConnectionFailure:
            #print("Could not connect to MongoDB: %s" % e)
            db = conn.trailers  #Your database name
            print(db)
            collection = db.trailers #Your collection name
            print(collection)
            d = request.form['Name']
            print(d)
            docs = list(collection.find({'Name': d}))
            if docs != []:
                print(docs)
                var = docs[0]
                videos = var['Url']
                name = var['Name']
                image = var['Pic']
                #url = docs({"Url"})
                #print(url)
                flash("Movie found it")
                return render_template('show_videos.html', videos=videos,name=name,image=image)
                #return redirect(url_for('show_entries'))    
            else:
                error = 'Invalid Movie or trailer. Movie does not found it'
        return render_template('catalogue.html', error=error)
    else:
        flash ('You have to pay')
        return render_template('payment.html', error=error)
        

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    error = None
    if session.get('logged_in'):
        if request.method == 'POST':
            db = get_db()
            #db.execute('update users  set creditcard = ?, cvv= ? where username = ?', (request.form['creditcard'], request.form['cvv'], session['username'])  )
            #db.execute('''UPDATE users SET creditcard = ? WHERE username = ?''', (request.form['creditcard'], session['username']))
            db.execute('''UPDATE users SET creditcard = ?, cvv = ?, payment = ? WHERE username = ?''', (request.form['creditcard'],request.form['cvv'],True, session['username']))
            db.commit()
            flash('New payment was successfully done')
            return redirect(url_for("catalogue"))
        return render_template('payment.html', error=error)
    else:
        return redirect(url_for("show_entries"))


if __name__ == "__main__":
    app.run(host="0.0.0.0")
    #app.secret_key = os.urandom(24)
    debug = True
    







