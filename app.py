from flask import Flask, render_template, request, redirect, session
import sqlite3, hashlib

app = Flask(__name__)
app.secret_key = 'tajny_kluc'

def get_db():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        action = request.form['action']
        db = get_db()

        if action == 'register':
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            db.commit()
        elif action == 'login':
            user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
            if user:
                session['user_id'] = user['id']
                return redirect('/diary')
        db.close()
    return render_template('index.html')

@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if 'user_id' not in session:
        return redirect('/')
    db = get_db()
    if request.method == 'POST':
        date = request.form['date']
        mood = request.form['mood']
        notes = request.form['notes']
        db.execute('INSERT INTO entries (user_id, date, mood, notes) VALUES (?, ?, ?, ?)',
                   (session['user_id'], date, mood, notes))
        db.commit()
    entries = db.execute('SELECT * FROM entries WHERE user_id = ?', (session['user_id'],)).fetchall()
    db.close()
    return render_template('diary.html', entries=entries)

if __name__ == '__main__':
    with sqlite3.connect('db.sqlite3') as db:
        db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
        db.execute('''CREATE TABLE IF NOT EXISTS entries (
                          id INTEGER PRIMARY KEY,
                          user_id INTEGER,
                          date TEXT,
                          mood TEXT,
                          notes TEXT,
                          FOREIGN KEY(user_id) REFERENCES users(id))''')
    app.run(debug=True)